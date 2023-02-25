import logging
from contextlib import suppress

from sqlalchemy import select, update
from sqlalchemy.sql.expression import func

from model import model
from model import dbutils
from scraping_wr import api
from scraper_procedures import outlier_detection
from common.helpers import Timedelta_Parser, get_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _wr_select_boat_class(boat_classes_dict, search_str):
    result = None
    for boat_class_data in boat_classes_dict:
        if search_str.strip() == boat_class_data.get('DisplayName','').strip():
            result = boat_class_data
            break
    return result

def refresh_world_best_times(session, logger=logger):
    wbts = api.get_world_best_times()
    boat_classes = api.get_boatclasses()
    for wbt in wbts:
        boat_class_abbr = wbt.get('boat_class','')
        logger.error(f'Boat Class "{boat_class_abbr}"')
        boat_class_data = _wr_select_boat_class(boat_classes, boat_class_abbr)
        if not boat_class_data:
            logger.error(f'Could not resolve uuid of boat class')
            continue
        boat_class_uuid = boat_class_data.get('id')

        boat_class = dbutils.wr_insert(session, model.Boat_Class, dbutils.wr_map_boat_class, boat_class_data)
        if not boat_class:
            logger.error(f'Could not add boat class to db')
            continue

        race_boat_uuid = wbt.get('race_boat_id')
        result_time_ms = None
        try:
            result_time_ms = Timedelta_Parser.to_millis( wbt.get('result_time') )
        except Exception:
            logger.error(f'Could not parse result time.')
            continue
        
        logger.info(f'''Race_Boat "{wbt.get('race_boat_id')}"''')

        statement = (
            select(model.Race_Boat)
            .where(model.Race_Boat.additional_id_ == race_boat_uuid)
        )
        race_boat = session.execute(statement).scalars().first()
        if not race_boat:
            logger.warning(f'Race Boat "{race_boat_uuid}" not found in db. Create entity')
            race_boat = model.Race_Boat(additional_id_=race_boat_uuid)

        if not race_boat.result_time_ms == result_time_ms:
            logger.warning(f'''Result time does not match race_boat has "{race_boat.result_time_ms}" wbt says "{result_time_ms}"''')
        
        logger.info(f'Overwrite result time')
        race_boat.result_time_ms = result_time_ms
        race_boat.invalid_mark_result_code_id = None

        boat_class.world_best_race_boat = race_boat

        logger.info(f"Updating wbt for boat_class: {boat_class_abbr}")

    session.commit()


def mark_outliers(session, logger=logger):
    # todo: add me to the actual postprocessing
    with model.Scoped_Session() as session:
        statement = select(model.Boat_Class).order_by(model.Boat_Class.id)
        iterator = session.execute(statement).scalars()

        # set all is_outlier to False to ensure that the percentile-strategy works
        session.execute( update(model.Intermediate_Time).values(is_outlier=False) )
        session.execute( update(model.Race_Data).values(is_outlier=False) )

        for boat_class in iterator:
            outlier_detection.outlier_detection_result_data(session=session, boat_class=boat_class)
            outlier_detection.outlier_detection_race_data(session=session, boat_class=boat_class)

            # Low Prio TODO: session.commit() should ideally be executed here

# def _get_competitions_to_maintain(session):
#     """Returns tuple: competitions_iterator, number_of_competitions"""
#     DATA_PROVIDER_ID = model.Enum_Data_Provider.world_rowing.value
#     LEVEL_SCRAPED = model.Enum_Maintenance_Level.world_rowing_api_scraped.value
#     LEVEL_POSTPROCESSED = model.Enum_Maintenance_Level.world_rowing_api_postprocessed.value
#     scrape_before_date = datetime.datetime.now() - datetime.timedelta(days=int(SCRAPER_MAINTENANCE_PERIOD_DAYS))

#     statement = (
#         select(model.Competition)
#         .where(model.Competition.scraper_data_provider == DATA_PROVIDER_ID)
#         .where(
#             or_(
#                 model.Competition.scraper_maintenance_level == LEVEL_SCRAPED,
#                 and_(
#                     model.Competition.scraper_maintenance_level == LEVEL_POSTPROCESSED,
#                     model.Competition.scraper_last_scrape < scrape_before_date
#                 )
#             )
#         )
#     )
#     competitions = session.execute(statement).scalars().all()
#     return competitions, len(competitions)


def postprocess():
    logger = logging.getLogger("postprocessing")
    with model.Scoped_Session() as session:
        logger.info(f"Fetch & write world best times")
        refresh_world_best_times(session=session, logger=logger)

        logger.info("Outlier Marking")
        mark_outliers(session=session, logger=logger)


"""
        logger.info("Find competitions that have to be maintained")
        competitions, N = _get_competitions_to_maintain(session)
        logger.info(f"Found N={N} competitions")
        for competition in competitions:
            competition_uuid = competition.additional_id_
            if not competition_uuid:
                logger.error(f"Competition with id={competition.id} has no UUID (w.r.t. World Rowing API); Skip")
                continue
            logger.info(f"Competition id={competition.additional_id_}")

            # New concept: api.get_by_competition_id_(..., parse_pdf=True)
            #    -> does it make sense to put validation logic (db/model imports) inside api?

            logger.info("Fetch & Parse PDF")

            logger.info("Check Quality of both Datasets")

            # logger.info("Mark maintenance state in db") # Deprecated (?)
"""