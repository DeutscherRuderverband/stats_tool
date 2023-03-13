import logging

from model import model
# from model import dbutils
from common.helpers import get_, select_first

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

DISTANCE_METER_IS_2KM = lambda i: i.distance_meter==2000

def bubble_up_2km_intermediate(intermediate: model.Intermediate_Time):
    """ writes 2km intermediate data to Race_Boat entity
    """
    if not intermediate.distance_meter == 2000:
        raise ValueError("Not a 2km intermediate entity")
    
    intermediate.race_boat.result_time_ms = intermediate.result_time_ms
    intermediate.race_boat.invalid_mark_result_code_id = intermediate.invalid_mark_result_code_id
    intermediate.race_boat.rank = intermediate.rank

def bubble_down_2km_intermediate(session, race_boat: model.Race_Boat, force_overwrite=True, outlier_val=True, logger=logger, data_source=None):
    """ synchronizes Race_Boat result data to its 2km Intermediate
    """
    written_something_ = False

    intermediate = select_first(race_boat.intermediates, DISTANCE_METER_IS_2KM)
    create_new = intermediate == None
    if create_new:
        intermediate = model.Intermediate_Time(race_boat=race_boat, distance_meter=2000)
    
    if force_overwrite or create_new:
        written_something_ = True
        intermediate.invalid_mark_result_code_id = race_boat.invalid_mark_result_code_id
        intermediate.rank = race_boat.rank
        intermediate.result_time_ms = race_boat.result_time_ms
        intermediate.is_outlier = outlier_val
        if data_source != None:
            intermediate.data_source = data_source

    if create_new:
        session.add(intermediate)

    return written_something_