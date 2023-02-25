
from sqlalchemy import select, update, or_, and_, func
from sqlalchemy.orm.session import Session
from model import model

tqdm = lambda x: x
#from tqdm import tqdm 

import logging
import os 


OUTLIER_DETECTION_PERCENTILE_MIN = float(os.environ.get('OUTLIER_DETECTION_PERCENTILE_MIN','.001').strip())
OUTLIER_DETECTION_PERCENTILE_MAX = float(os.environ.get('OUTLIER_DETECTION_PERCENTILE_MAX','.97').strip())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outlier_detector")


def outlier_detection_race_data(session:Session, boat_class: model.Boat_Class) -> None:
    logger.info(f"Marking race_data for boat class: {boat_class.id}")
    race_data_statement = (
        select(
            model.Race_Data.distance_meter,
            model.Competition_Category.id.label("competition_category_id")
        )
        .join(model.Race_Data.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .join(model.Competition_Type.competition_category)
        .where(model.Event.boat_class_id == boat_class.id)
        .order_by(model.Race_Data.distance_meter)
        .group_by(
            model.Race_Data.distance_meter,
            model.Competition_Category.id
        )
    )
    race_data = session.execute(race_data_statement).all()

    for row in race_data: 

        percentiles_statement = (
            select(
                
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MIN).within_group(model.Race_Data.speed_meter_per_sec.desc()).label("percentile_smps_min"),
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MAX).within_group(model.Race_Data.speed_meter_per_sec.desc()).label("percentile_smps_max"),
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MIN).within_group(model.Race_Data.stroke.desc()).label("percentile_stroke_min"),
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MAX).within_group(model.Race_Data.stroke.desc()).label("percentile_stroke_max"),
                
            )
            .join(model.Race_Data.race_boat)
            .join(model.Race_Boat.race)
            .join(model.Race.event)
            .join(model.Event.competition)
            .join(model.Competition.competition_type)
            .join(model.Competition_Type.competition_category)
            .where(
                and_(
                    model.Event.boat_class_id == boat_class.id,
                    model.Race_Data.distance_meter == row.distance_meter,
                    model.Competition_Category.id == row.competition_category_id,
                    model.Race_Data.speed_meter_per_sec != 0
                )
            )
        )

        percentiles = session.execute(percentiles_statement).fetchall()[0]

        if not all(percentiles): 
            # if there is a None in percentiles, it means they could not have been calculated. 
            # This is a result from no data present to calc the percentiles.
            logger.info(
                f"""Could not calculate the percentiles. The folloing filters result in no data:
                    - Event.boat_class_id: {boat_class.id}
                    - Race_Data.distance_meter: {row.distance_meter}
                    - Event.competition_category: {row.competition_category_id}
                moving on to next distance_meter."""
            )
            continue
        else: 
            min_smps, max_smps, min_stroke, max_stroke = sorted(percentiles)

        to_adjust_statement = (
            select(
                model.Race_Data.race_boat_id,
                model.Race_Data.distance_meter
            )
            .join(model.Race_Data.race_boat)
            .join(model.Race_Boat.race)
            .join(model.Race.event)
            .join(model.Event.competition)
            .join(model.Competition.competition_type)
            .join(model.Competition_Type.competition_category)
            .where(
                and_(
                    model.Event.boat_class_id == boat_class.id,
                    or_(
                        ~model.Race_Data.speed_meter_per_sec.between(min_smps, max_smps),
                        ~model.Race_Data.stroke.between(min_stroke, max_stroke),
                    ),
                    model.Race_Data.distance_meter == row.distance_meter,
                    model.Competition_Category.id == row.competition_category_id
                )
            )
        )

        to_adjust = session.execute(to_adjust_statement).fetchall()
        # todo: how to do a bulk-update? 
        for race_boat_id, distance_meter in to_adjust: 
            updt = update(model.Race_Data)
            updt = updt.values({'is_outlier': True})
            updt = updt.where(model.Race_Data.race_boat_id == race_boat_id)
            updt = updt.where(model.Race_Data.distance_meter == distance_meter)

            session.execute(updt)
            session.commit()

    return None



def outlier_detection_result_data(session:Session, boat_class: model.Boat_Class) -> None:

    logger.info(f"Marking result_data for boat class: {boat_class.id}")

    # https://docs.sqlalchemy.org/en/14/core/selectable.html#sqlalchemy.sql.expression.GenerativeSelect.group_by
    # func.xxx ---> https://www.postgresql.org/docs/8.2/functions-aggregate.html
    intermediate_statement = (
        select(
            model.Intermediate_Time.distance_meter,
            model.Competition_Category.id.label('competition_category_id')
        )
        .join(model.Intermediate_Time.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .join(model.Competition_Type.competition_category)
        .where(model.Event.boat_class_id == boat_class.id)
        .order_by(model.Intermediate_Time.distance_meter)
        .group_by(
            model.Intermediate_Time.distance_meter,
            model.Competition_Category.id
        )
    )

    wbt_statement = (
        select(
            model.Boat_Class.id, 
            model.Race_Boat.result_time_ms
        )
        .join(model.Race_Boat)
    )

    intermediates = session.execute(intermediate_statement).all()

    if len(intermediates) == 0: 
        logger.info(f"Skipping boat class: {boat_class.id}. No intermediates with this boatclass")
        return None

    wbts = session.execute(wbt_statement).all()
    wbt = [wb[1] for wb in wbts if wb[0] == boat_class.id]
    wbt = wbt[0] if len(wbt) > 0 else 0
    longest_distance = intermediates[-1].distance_meter

    for row in tqdm(intermediates):

        logger.debug(f"  Competition Category: {row.competition_category_id}")

        percentiles_statement = (
            select(
                [
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MIN).within_group(model.Intermediate_Time.result_time_ms.desc()),
                    func.percentile_cont(OUTLIER_DETECTION_PERCENTILE_MAX).within_group(model.Intermediate_Time.result_time_ms.desc()),
                ],
            )
            .join(model.Intermediate_Time.race_boat)
            .join(model.Race_Boat.race)
            .join(model.Race.event)
            .join(model.Event.competition)
            .join(model.Competition.competition_type)
            .join(model.Competition_Type.competition_category)
            .where(
                and_(
                    model.Event.boat_class_id == boat_class.id,
                    model.Intermediate_Time.distance_meter == row.distance_meter,
                    model.Competition_Category.id == row.competition_category_id,
                    model.Intermediate_Time.result_time_ms != 0
                )
            )
        )

        percentiles = sorted(session.execute(percentiles_statement).fetchall()[0])
        if (row.distance_meter < longest_distance and wbt != 0): 
            """
                todo: this could be done better, 
                    by checking for which distance_meter the wbt was originally achieved
            """
            _min = wbt
            logging.debug("Use WBT for min")
        else: 
            _min = percentiles[0]
        _min = percentiles[0]
        _max = percentiles[1]

        to_adjust_statement = (
            select(
                model.Intermediate_Time.race_boat_id,
                model.Intermediate_Time.distance_meter
            )
            .join(model.Intermediate_Time.race_boat)
            .join(model.Race_Boat.race)
            .join(model.Race.event)
            .join(model.Event.competition)
            .join(model.Competition.competition_type)
            .join(model.Competition_Type.competition_category)
            .where(
                and_(
                    model.Event.boat_class_id == boat_class.id,
                    ~model.Intermediate_Time.result_time_ms.between(_min, _max),
                    model.Intermediate_Time.distance_meter == row.distance_meter,
                    model.Competition_Category.id == row.competition_category_id
                )
            )
        )

        to_adjust = session.execute(to_adjust_statement).fetchall()
        # todo: how to do a bulk-update? 
        for intermediate_id, distance_meter in to_adjust: 
            updt = update(model.Intermediate_Time)
            updt = updt.values({'is_outlier': True})
            updt = updt.where(model.Intermediate_Time.race_boat_id == intermediate_id)
            updt = updt.where(model.Intermediate_Time.distance_meter == distance_meter)

            session.execute(updt)
            session.commit()

    return None
