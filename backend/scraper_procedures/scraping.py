import logging
import datetime
from contextlib import suppress

tqdm = lambda x: x
# from tqdm import tqdm

from sqlalchemy import select
from sqlalchemy import func, desc, and_, or_, not_
from sqlalchemy.orm import joinedload

from .config import *
from .common import bubble_up_2km_intermediate
from model import model
from model import dbutils
from scraping_wr import api, pdf_race_data, pdf_result
from common import rowing
from common.helpers import get_, select_first, Timedelta_Parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrape")

REQUIRED_INTERMEDIATES_MARKS = ( 500, 1000, 1500, 2000 )

def _get_competitions_to_scrape(session):
    """Returns tuple: competitions_iterator, number_of_competitions"""
    LEVEL_PRESCRAPED = model.Enum_Maintenance_Level.world_rowing_api_prescraped.value
    LEVEL_SCRAPED = model.Enum_Maintenance_Level.world_rowing_api_scraped.value
    DATA_PROVIDER_ID = model.Enum_Data_Provider.world_rowing.value

    statement = (
        select(model.Competition)
        .where(model.Competition.scraper_data_provider == DATA_PROVIDER_ID)
        #.where(model.Competition.scraper_maintenance_level.in_( [LEVEL_PRESCRAPED, LEVEL_SCRAPED] ))
        .order_by(
            desc(model.Competition.year),
            desc(model.Competition.start_date),
            desc(model.Competition.end_date)
        )
    )
    competitions = session.execute(statement).scalars().all()
    N = len(competitions) # TODO: Get rid of all() call and use a count query to get N: https://stackoverflow.com/a/65775282
    return competitions, N


def _competition_within_rescrape_window(comp: model.Competition) -> bool:
    # LEVEL_SCRAPED is assumed
    rescrape_limit = datetime.datetime.now() - datetime.timedelta(days=int(SCRAPER_RESCRAPE_LIMIT_DAYS))
    # if only start date is given, assume X days for competition to take
    competition_duration_default_assumption = 14
    gracious_date_limit = rescrape_limit - datetime.timedelta(days=competition_duration_default_assumption)
    
    if comp.end_date:
        if comp.end_date >= rescrape_limit:
            return True
        return False

    if comp.start_date:
        if comp.start_date >= gracious_date_limit:
            return True
        return False

    if comp.year:
        if comp.year >= gracious_date_limit.year:
            return True
        return False

    if comp.scraper_last_scrape < gracious_date_limit:
        return False

    # no date data found
    return True


def _date_of_competition(comp: model.Competition) -> datetime.date:
    year = None
    with suppress(Exception):
        year = datetime.date(year=comp.year, month=1, day=1)
    return comp.end_date.date() or comp.start_date.date() or year


def _parse_and_inject_pdf_race_data(session, race: model.Race):
    url = race.pdf_url_race_data
    logger.info(f'pdf_racedata:Fetch & parse PDF race data url="{url}"')
    pdf_race_data_, _ = pdf_race_data.extract_data_from_pdf_url([url])
    if not pdf_race_data_:
        logger.info(f'pdf_racedata:Failed to parse (or fetch)')
        return
    matched_log_list_ = []

    # Ideas:
    # - sanity check with parsed ranks
    # - check for multiple matches on either side.
    #       (pop out of pdf_result_list; or with seen in set() pattern from wr_map_race_boat)
    # - check if all race_boats were matched.
    race_boat: model.Race_Boat
    for race_boat in race.race_boats:
        for pdf_boat in pdf_race_data_.get('data', []):
            matched_name = race_boat.name.lower().strip() == pdf_boat.get('country','').lower().strip()
            
            parsed_rank = None
            with suppress(Exception):
                parsed_rank = int(pdf_boat.get('rank'))
            matched_rank = race_boat.rank == parsed_rank

            if matched_name: # optional -> matched_name and matched_rank
                matched_log_list_.append(race_boat.name)
                data_ = get_(pdf_boat, 'data', {})
                dists   = get_(data_, 'dist [m]', [])
                speeds  = get_(data_, 'speed', [])
                strokes = get_(data_, 'stroke', [])
                is_consistent = len(dists) == len(speeds) == len(strokes)
                
                if not is_consistent:
                    logger.error(f'pdf_racedata:Data is inconsistent: Arrays have different lengths')
                    continue # TODO: consider not commiting for this Race_Boat at all
                
                for dist, speed, stroke in zip(dists, speeds, strokes):
                    try:
                        race_data_point = select_first(race_boat.race_data, lambda i: i.distance_meter==dist)
                        if not race_data_point:
                            race_data_point = model.Race_Data()
                        race_data_point.data_source=model.Enum_Data_Source.world_rowing_pdf.value
                        race_data_point.distance_meter = dist
                        race_data_point.speed_meter_per_sec = speed
                        race_data_point.stroke = stroke
                    except Exception:
                        logger.error(f'pdf_racedata:Failed to write dist="{dist}" speed="{speed}" stroke="{stroke}"')
                    else:
                        session.add(race_data_point)
                        race_boat.race_data.append(race_data_point)
    logger.info(f'pdf_racedata:Race data matched for {matched_log_list_}')


def _shallow_validation_pdf_intermediates(pdf_results, race: model.Race):
    """ compares boat/team names of both data sources
    """
    upper_ = lambda x: x.strip().upper() if isinstance(x, str) else x

    pdf_boat_names = map(lambda d: d.get('country'), pdf_results)
    db_boat_names = map(lambda rb: rb.name, race.race_boats)

    pdf_boat_names = list(map(upper_, pdf_boat_names))
    db_boat_names = list(map(upper_, db_boat_names))

    pdf_boat_names.sort()
    db_boat_names.sort()

    if len(pdf_boat_names) != len(db_boat_names):
        return False
    
    for pdf_boat_name, db_boat_name in zip(pdf_boat_names, db_boat_names):
        if pdf_boat_name != db_boat_name:
            return False

    return True


def _intermediates_validation_pdf_intermediates(pdf_results_):
    """ checks plausibility of parsed data meaning that { 500, 1000, 1500, 2000 } has to have a result time for each boat
    (assumes 2km race course length with 500m resolution)
    """
    valid = True
    for pdf_result_ in pdf_results_:
        times = get_(pdf_result_, 'times', [])        
        for required_mark in REQUIRED_INTERMEDIATES_MARKS:
            if not required_mark in times:
                return False

            result_time_str = get_(times, required_mark, None)
            try:
                result_time = Timedelta_Parser.to_millis(result_time_str)
            except:
                return False
            
            if result_time < 0:
                return False

    return True


def _create_intermediates_table(pdf_results_):
    """ returns dict of form
        dict[distance_meter][idx] containing a dict for: boat_name, result_time, rank
        e.g. dict[1500][2] = { boat_name: 'GER2', result_time: 54321, rank: 5 }
    """
    table = {}

    for pdf_result in pdf_results_:
        boat_name = pdf_result.get('country','').strip().upper()
        for distance_meter in REQUIRED_INTERMEDIATES_MARKS:
            if not distance_meter in table:
                table[distance_meter] = []
            
            result_time_str = pdf_result['times'][distance_meter]
            result_time = Timedelta_Parser.to_millis(result_time_str)

            table[distance_meter].append({
                "boat_name": boat_name,
                "result_time": result_time,
                "rank": None
            })

    # sorting in order to determine ranks
    for distance_meter, boats_list in table.items():
        boats_list.sort(key=lambda d: d['result_time'])
        for idx, dict_ in enumerate(boats_list):
            dict_['rank'] = idx+1

    return table


def _parse_and_inject_pdf_intermediates(session, race: model.Race):
    url = race.pdf_url_results
    logger.info(f'pdf_results:Fetch & parse PDF results url="{url}"')
    pdf_parser_result__, _ = pdf_result.extract_data_from_pdf_urls([url])
    if not pdf_parser_result__:
        logger.info(f'pdf_results:Failed to parse (or fetch)')
        return
    
    pdf_results_ = get_(pdf_parser_result__, 'data', [])

    shallow_valid = _shallow_validation_pdf_intermediates(pdf_results=pdf_results_, race=race)
    if not shallow_valid:
        logger.info(f'pdf_results:Validation failed: could not match all boat/team names')
        return

    completeness_valid = _intermediates_validation_pdf_intermediates(pdf_results_=pdf_results_)
    if not completeness_valid:
        logger.info(f'pdf_results:Validation failed: incomplete data')
        return

    intermediates_table = _create_intermediates_table(pdf_results_=pdf_results_)

    for distance_meter, boats_list in intermediates_table.items():
        for boat_data in boats_list:
            race_boat_name = boat_data['boat_name']
            pdf_time = boat_data['result_time']
            computed_rank = boat_data['rank']

            race_boat: model.Race_Boat = select_first(race.race_boats, lambda rb: rb.name==race_boat_name)
            intermediate: model.Intermediate_Time = select_first(race_boat.intermediates, lambda i: i.distance_meter==distance_meter)
            if not intermediate:
                intermediate = model.Intermediate_Time(race_boat=race_boat, distance_meter=distance_meter)
                session.add(intermediate)
                
            intermediate.data_source = model.Enum_Data_Source.world_rowing_pdf.value
            intermediate.result_time_ms = pdf_time
            intermediate.rank = computed_rank
            intermediate.invalid_mark_result_code_id = None
            intermediate.is_outlier = True

            if distance_meter == 2000:
                bubble_up_2km_intermediate(intermediate)

    logger.info(f'pdf_results:Completely matched & written')
    


def _scrape_competition(session, competition: model.Competition, parse_pdf_race_data=True, parse_pdf_intermediates=True):
    uuid = competition.additional_id_
    assert not uuid == None

    logger.info(f'''Fetching competition="{uuid}" year="{competition.year}" name="{competition.name}"''')
    competition_data = api.get_by_competition_id_(comp_ids=[uuid], parse_pdf=False)

    logger.info(f"Write competition to database")
    # let's use the mapper func directly since we already have the ORM instance
    competition = dbutils.wr_map_competition_scrape(session, competition, competition_data)
    session.commit() # TODO: consider removing multiple commits

    for event in competition.events:
        race: model.Race
        for race in event.races:
            if parse_pdf_intermediates or parse_pdf_race_data:
                logger.info(f'Begin PDF injection for race="{race.additional_id_}"')
            if parse_pdf_intermediates:
                _parse_and_inject_pdf_intermediates(session=session, race=race)
            if parse_pdf_race_data:
                _parse_and_inject_pdf_race_data(session=session, race=race)
    session.commit()

def scrape(parse_pdf=True):
    LEVEL_PRESCRAPED    = model.Enum_Maintenance_Level.world_rowing_api_prescraped.value
    LEVEL_SCRAPED       = model.Enum_Maintenance_Level.world_rowing_api_scraped.value

    with model.Scoped_Session() as session:
        competitions_iter, num_competitions = _get_competitions_to_scrape(session=session)
        logger.info(f"Competitions that have to be scraped N={num_competitions}")

        competition: model.Competition
        for competition in tqdm(competitions_iter):
            competition_uuid = competition.additional_id_
            logger.info(f'Competition uuid="{competition_uuid}"')
            try:
                if not competition_uuid:
                    logger.error(f"Competition with id={competition.id} has no UUID (w.r.t. World Rowing API); Skip")
                    continue
                
                scrape = True
                if competition.scraper_maintenance_level in [LEVEL_SCRAPED]:
                    scrape = _competition_within_rescrape_window(comp=competition)

                if scrape:
                    # this also advances the maintenance_level
                    _scrape_competition(
                        session=session,
                        competition=competition,
                        parse_pdf_intermediates=parse_pdf,
                        parse_pdf_race_data=parse_pdf,
                    )

                    # mark competition as SCRAPED along with date for rescrape logic
                    competition.scraper_maintenance_level = LEVEL_SCRAPED
                    competition.scraper_last_scrape = datetime.datetime.now()

                session.commit()
            except Exception as error:
                logger.error(f'ERROR while scraping Competition uuid="{competition_uuid}"')
                logger.error(str(error))
                if SCRAPER_DEV_MODE:
                    raise error