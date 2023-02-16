from datetime import date

import logging
logger = logging.getLogger(__name__)

from .helpers import make_keys_lowercase, is_number

__course_length_2000m_lookup_table = make_keys_lowercase({
    "LW1x": date(1998,1,1),
    "PR3 W2-": date(2007,1,1)
    # ... TODO: Kay ...
})

def get_course_length(boat_class: str, race_date: date, **kwargs) -> int:
    """
    Returns course length

    Parameters
    ----------
    boat_class: Short form of the boat class e.g. "LW1x", "PR3 W2-", etc.
    date: Date of the race
    """
    DEFAULT_LENGTH = None

    threshold_date = __course_length_2000m_lookup_table.get(boat_class.strip())
    
    if not threshold_date:
        # TODO: uncomment logging when lookup table is complete
        # logger.error(f"Boat class '{boat_class}' not found in course length lookup table (2km)")
        return DEFAULT_LENGTH

    if race_date > threshold_date:
        return 2000

def propulsion_in_meters_per_stroke(strokes_per_min, speed_in_meter_per_sec):
    valid_params = (
        is_number(strokes_per_min)
        and is_number(speed_in_meter_per_sec)
        and not strokes_per_min == 0
    ) 
    if not valid_params:
        logger.error(f'propulsion_in_meters_per_stroke:invalid input received')
        return None
        
    distance_in_one_minute = 60 * speed_in_meter_per_sec
    propulsion = distance_in_one_minute / strokes_per_min
    return propulsion
