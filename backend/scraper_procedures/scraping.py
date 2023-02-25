import logging
import datetime
from contextlib import suppress

tqdm = lambda x: x
# from tqdm import tqdm

from sqlalchemy import select
from sqlalchemy import func, desc, and_, or_, not_
from sqlalchemy.orm import joinedload

from .config import *
from model import model
from model import dbutils
from scraping_wr import api, pdf_race_data
from common import rowing
from common.helpers import get_, select_first

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_competitions_to_scrape(session):
    """Returns tuple: competitions_iterator, number_of_competitions"""
    LEVEL_PRESCRAPED = model.Enum_Maintenance_Level.world_rowing_api_prescraped.value
    LEVEL_SCRAPED = model.Enum_Maintenance_Level.world_rowing_api_scraped.value
    DATA_PROVIDER_ID = model.Enum_Data_Provider.world_rowing.value

    statement = (
        select(model.Competition)
        .where(model.Competition.scraper_data_provider == DATA_PROVIDER_ID)
        .where(model.Competition.scraper_maintenance_level.in_( [LEVEL_PRESCRAPED, LEVEL_SCRAPED] ))
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
    competition_duration_default_assumption = 10
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


def _scrape_competition(session, competition: model.Competition, parse_pdf_race_data=True, parse_pdf_intermediates=True, logger=logger):
    uuid = competition.additional_id_
    assert not uuid == None

    logger.info(f'''Fetching competition="{uuid}" year="{competition.year}" name="{competition.name}"''')
    competition_data = api.get_by_competition_id_(comp_ids=[uuid], parse_pdf=False)

    logger.info(f"Write competition to database")
    # let's use the mapper func directly since we already have the ORM instance
    competition = dbutils.wr_map_competition_scrape(session, competition, competition_data)
    session.commit() # TODO: consider removing multiple commits

    logger.info(f"Determine course lengths")
    for event in competition.events:
        race: model.Race
        for race in event.races:
            race.course_length = rowing.get_course_length(
                boat_class=event.boat_class.abbreviation,
                race_date=_date_of_competition(competition)
            )
    session.commit()

    logger.info(f'Fetch & parse PDF race data')
    if parse_pdf_race_data:
        for event in competition.events:
            race: model.Race
            for race in event.races:
                url = race.pdf_url_race_data
                logger.info(f'Fetch & parse PDF race data race="{race.additional_id_}" url="{url}"')
                pdf_race_data_, _ = pdf_race_data.extract_data_from_pdf_url([url])
                if not pdf_race_data_:
                    logger.info(f'Failed to parse (or fetch)')
                
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

                        if matched_name and matched_rank:
                            logger.info(f'Race data matched for "{race_boat.name}"')
                            data_ = get_(pdf_boat, 'data', {})
                            dists   = get_(data_, 'dist [m]', [])
                            speeds  = get_(data_, 'speed', [])
                            strokes = get_(data_, 'stroke', [])
                            is_consistent = len(dists) == len(speeds) == len(strokes)
                            
                            if not is_consistent:
                                logger.error(f'Data is inconsistent: Arrays have different lengths')
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
                                    logger.error(f'Failed to write dist="{dist}" speed="{speed}" stroke="{stroke}"')
                                else:
                                    session.add(race_data_point)
                                    race_boat.race_data.append(race_data_point)
                            

def scrape(parse_pdf=True):
    logger = logging.getLogger("scrape")
    LEVEL_PRESCRAPED    = model.Enum_Maintenance_Level.world_rowing_api_prescraped.value
    LEVEL_SCRAPED       = model.Enum_Maintenance_Level.world_rowing_api_scraped.value
    LEVEL_POSTPROCESSED = model.Enum_Maintenance_Level.world_rowing_api_postprocessed.value

    with model.Scoped_Session() as session:
        competitions_iter, num_competitions = _get_competitions_to_scrape(session=session)
        logger.info(f"Competitions that have to be scraped N={num_competitions}")

        for competition in tqdm(competitions_iter):
            competition_uuid = competition.additional_id_
            logger.info(f'Competition uuid="{competition_uuid}"')
            try:
                if not competition_uuid:
                    logger.error(f"Competition with id={competition.id} has no UUID (w.r.t. World Rowing API); Skip")
                    continue
                
                scrape = True
                if competition.scraper_maintenance_level in [LEVEL_SCRAPED, LEVEL_POSTPROCESSED]:
                    scrape = _competition_within_rescrape_window(comp=competition)

                if scrape:
                    # this also advances the maintenance_level
                    _scrape_competition(
                        session=session,
                        competition=competition,
                        parse_pdf_intermediates=parse_pdf,
                        parse_pdf_race_data=parse_pdf,
                        logger=logger
                    )

                # HIGH PRIO TODO:
                #   - introduce deep_scrape/parse_pdf param?
                #   - set maintenance state in the end
                #   - set scraper_last_scrape in the end

                session.commit()
                # Race Data PDF here or in maintain()
            except Exception as error:
                logger.error(f'ERROR while scraping Competition uuid="{competition_uuid}"')
                logger.error(str(error))