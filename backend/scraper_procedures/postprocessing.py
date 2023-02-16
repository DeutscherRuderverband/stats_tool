import logging
from contextlib import suppress

from sqlalchemy import select, update
from sqlalchemy.sql.expression import func

from model import model
from scraping_wr import api
from scraper_procedures import outlier_detection
from common.helpers import Timedelta_Parser, get_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def refresh_world_best_times(session, logger=logger):
    wbts = api.get_world_best_times()
    for wbt in wbts:
        boat_class_abbr = wbt.get('boat_class','')
        race_boat_uuid = wbt.get('race_boat_id')
        result_time_ms = None
        with suppress(Exception):
            result_time_ms = Timedelta_Parser.to_millis( wbt.get('result_time') )

        statement = (
            select(model.Boat_Class)
            .where(func.lower(model.Boat_Class.abbreviation) == boat_class_abbr.lower())
        )
        boat_class = session.execute(statement).scalars().first()
        if not boat_class:
            logger.error(f'Boat Class "{boat_class_abbr}" not found in db')
            continue
        
        statement = (
            select(model.Race_Boat)
            .where(model.Race_Boat.additional_id_ == race_boat_uuid)
        )
        race_boat = session.execute(statement).scalars().first()
        if not race_boat:
            logger.error(f'Race Boat "{race_boat_uuid}" not found in db')
            continue

        if not race_boat.result_time_ms == result_time_ms:
            logger.error(f'''!!!!! Integrity Problem: Result time does not match race_boat has "{race_boat.result_time_ms}" wbt says "{result_time_ms}" ({wbt.get('race_boat_id')})''')

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