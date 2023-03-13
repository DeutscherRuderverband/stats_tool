import logging
from contextlib import suppress
from itertools import count

from sqlalchemy import select, update
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload

from .common import bubble_up_2km_intermediate, bubble_down_2km_intermediate
from model import model
from model import dbutils
from scraping_wr import api
from scraper_procedures import outlier_detection
from common.helpers import Timedelta_Parser, get_, true_every_nth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("postprocessing")

def _wr_select_boat_class(boat_classes_dict, search_str):
    result = None
    for boat_class_data in boat_classes_dict:
        if search_str.strip() == boat_class_data.get('DisplayName','').strip():
            result = boat_class_data
            break
    return result

def refresh_world_best_times(session):
    wbts = api.get_world_best_times()
    boat_classes = api.get_boatclasses()
    for wbt in wbts:
        boat_class_abbr = wbt.get('boat_class','')
        logger.info(f'Boat Class "{boat_class_abbr}"')
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

        bubble_down_2km_intermediate(
            session=session,
            race_boat=race_boat,
            data_source=model.Enum_Data_Source.world_rowing_api.value,
            force_overwrite=True,
            outlier_val=False
        )

        boat_class.world_best_race_boat = race_boat

        logger.info(f"Updating wbt for boat_class: {boat_class_abbr}")

    session.commit()


def mark_outliers(session):
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

def bubble_down_2km_intermediate_(session, force_overwrite=True, outlier_val=True):
    statement = (
        select(model.Race_Boat)
        # .options( joinedload(model.Race_Boat.intermediates) )
    )
    iterator = session.execute(statement).scalars()
    entities_written = 0
    for race_boat, n, print_log in zip(iterator, count(), true_every_nth(1500)):
        written = bubble_down_2km_intermediate(session=session, race_boat=race_boat, force_overwrite=force_overwrite, outlier_val=outlier_val)
        if written:
            entities_written += 1

        if print_log:
            logger.info(f'... visited so far: {n}')

    session.commit()
    logger.info(f"Bubbled down count={entities_written}")

def postprocess():
    with model.Scoped_Session() as session:
        logger.info(f"Bubble-down precedure (synchronize/create 2km intermediate)")
        bubble_down_2km_intermediate_(session=session, force_overwrite=True, outlier_val=True)

        logger.info(f"Fetch & write world best times. Also syncs to 2km intermediate")
        refresh_world_best_times(session=session)

        logger.info("Outlier Marking")
        mark_outliers(session=session)
        
        session.commit()
