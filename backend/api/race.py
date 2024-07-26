import datetime
import itertools
import math
import statistics
from collections import OrderedDict, defaultdict
from collections.abc import Iterable
from contextlib import suppress

from scipy import stats
import numpy as np
import pandas as pd
from sqlalchemy import select, or_, and_, func

from model import model
from common.helpers import stepfunction


COND_VALID_2000M_RESULTS = and_(
    model.Intermediate_Time.distance_meter == 2000,
    model.Intermediate_Time.result_time_ms != None,
    model.Intermediate_Time.invalid_mark_result_code_id == None,
    or_(
        model.Intermediate_Time.is_outlier == False,
        model.Intermediate_Time.is_outlier == None
    )
)

def result_time_best_of_year_interval(session, boat_class_id, year_start, year_end=datetime.date.today().year):
    """returns result time as flot in ms"""

    statement = (
        select(
            func.min(model.Intermediate_Time.result_time_ms).label("shortest_result")
        )
        .join(model.Intermediate_Time.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.boat_class)
        .join(model.Event.competition)
        .where(model.Boat_Class.id == boat_class_id)
        .where(model.Competition.year >= year_start)
        .where(model.Competition.year <= year_end)
        .where(COND_VALID_2000M_RESULTS)
    )

    result_time = session.execute(statement).one_or_none().shortest_result
    if not result_time == None:
        result_time = float(result_time)

    return result_time


def _assign_intermediates_to_grid(race_boats, grid) -> OrderedDict:
    transposed = OrderedDict()

    for distance in grid:
        transposed[distance] = { race_boat.id : None for race_boat in race_boats }

    race_boat: model.Race_Boat
    for race_boat in race_boats:
        intermediate: model.Intermediate_Time
        for intermediate in race_boat.intermediates:
            dist = intermediate.distance_meter

            fits_to_grid = dist in transposed
            if not fits_to_grid:
                continue

            transposed[dist][race_boat.id] = intermediate
    return transposed

def prepare_grid(race_boats, force_grid_resolution=None, course_length=2000) -> list:
    """ This functions assumes 2km race course length by default
    """
    grid_resolution = force_grid_resolution

    if not force_grid_resolution:
        # grid_resolution = _find_min_difference( ... sorted Race_Boat.distance_meter list ... )
        raise NotImplementedError('Automatic grid resolution are not supported')

    return list(range(grid_resolution, course_length+grid_resolution, grid_resolution))

def _skip_NoneType(values):
    """drop None values"""
    return ( val for val in values if val != None )

def valid_intermediate(interm: model.Intermediate_Time) -> bool:
    return (
        isinstance(interm, model.Intermediate_Time)
        and interm.invalid_mark_result_code_id == None
        and not interm.is_outlier
        and not interm.result_time_ms == None
    )

def _best_time(intermediates: list[model.Intermediate_Time]) -> int:
    valid_intermediates = tuple(( i for i in intermediates if valid_intermediate(i) ))
    result_times = tuple( map(lambda i: i.result_time_ms, valid_intermediates) )
    best_time = None
    with suppress(ValueError):
        best_time = min(result_times)
    return best_time

def _speeds(boats_dict, distance):
    for _, distance_dict in boats_dict.items():
        figures = distance_dict[distance]
        yield figures['speed']

def compute_intermediates_figures(race_boats):
    """ returns: dict[race_boat_id][distance] each containing {"pace":..., ...}
    """
    grid_resolution = 500

    grid = prepare_grid(race_boats, force_grid_resolution=grid_resolution, course_length=2000)
    lookup = _assign_intermediates_to_grid(race_boats, grid=grid)

    result = defaultdict(lambda: defaultdict(dict))
    last_distance = 0
    last_valid_intermeds_lookup = {}
    first_distance = True
    for distance, intermediates_dict in lookup.items():
        intermediates = intermediates_dict.values()

        best_time = _best_time(intermediates)

        valid_intermeds_lookup = {}
        intermediate: model.Intermediate_Time
        for race_boat_id, intermediate in intermediates_dict.items():
            figures = {
                "__intermediate": None,
                "deficit": None,
                "rel_diff_to_avg_speed": None,
                "pace": None,
                "speed": None,
                "result_time": None
            }
            result[race_boat_id][distance] = figures

            figures["__intermediate"] = intermediate

            # handle cases with no meaningful result_time
            if intermediate == None or intermediate.result_time_ms == None:
                figures["result_time"] = "NaN"
                continue
            if intermediate.invalid_mark_result_code_id != None:
                figures["result_time"] = intermediate.invalid_mark_result_code_id
                continue

            valid_intermeds_lookup[race_boat_id] = intermediate

            # relative to best boat
            deficit = None
            if best_time != None:
                deficit = intermediate.result_time_ms - best_time

            pace = None
            if first_distance:
                pace = intermediate.result_time_ms
            elif race_boat_id in last_valid_intermeds_lookup:
                last_result_time = last_valid_intermeds_lookup[race_boat_id].result_time_ms
                pace = intermediate.result_time_ms - last_result_time
        
            speed = None
            if pace != None:
                pace_in_seconds = pace / 1000 # assuming milliseconds here
                dist_ = distance - last_distance
                speed = dist_/pace_in_seconds

            figures["deficit"] = deficit
            figures["pace"] = pace
            figures["speed"] = speed
            figures["result_time"] = intermediate.result_time_ms

        # now that we have all the pace values, we can compute avg speeds
        avg_speed = None
        with suppress(statistics.StatisticsError):
            avg_speed = statistics.mean(_skip_NoneType(_speeds(boats_dict=result, distance=distance)))

        for race_boat_id, intermediate in valid_intermeds_lookup.items():
            figures = result[race_boat_id][distance]
            speed = figures['speed']
            if avg_speed:
                rel_diff_to_avg_speed = (speed - avg_speed) / avg_speed * 100.0
                figures["rel_diff_to_avg_speed"] = rel_diff_to_avg_speed

        first_distance = False
        last_distance = distance
        last_valid_intermeds_lookup = valid_intermeds_lookup

    return result

def is_valid_race_data(race_data: model.Race_Data) -> bool:
    return race_data.is_outlier == False

def _iter_strokes_from_race_data(race_data_list: Iterable[model.Race_Data]):
    for race_data in race_data_list:
        is_valid_stroke = (
            race_data.is_outlier == False
            and race_data.stroke != None
        )
        if is_valid_stroke:
            yield race_data.stroke

def strokes_for_intermediate_steps(race_data_list, stepsize=500):
    result = {}
    map_to_steps_func = lambda race_data: stepfunction(race_data.distance_meter, stepsize=stepsize)
    for meter_mark, data_points in itertools.groupby(race_data_list, key=map_to_steps_func):
        avg = None
        with suppress(TypeError, statistics.StatisticsError):
            avg = statistics.fmean(_iter_strokes_from_race_data(data_points))
        result[meter_mark] = avg
    return result

def getIntermediateTimes(race_boat: model.Race_Boat):
    """
    Get rank, time and is_outlier for every 500m section
    Return:
        Dictionary: intermediates[distance][metric]
        -> distance: 500, 1000, 1500, 2000
        -> metric: 'rank', 'time [millis]', 'is_outlier'
    """
    intermediates = {}

    grid = prepare_grid(race_boat, force_grid_resolution=500, course_length=2000)

    for distance in grid:
        intermediates[distance] = {"rank": 0, "time [millis]": 0, "is_outlier": 0}

    intermediate : model.Intermediate_Time
    for intermediate in race_boat.intermediates:
        distance = intermediate.distance_meter
        if intermediates.get(distance) is not None:
            intermediates[distance]["rank"] = intermediate.rank
            intermediates[distance]["time [millis]"] = intermediate.result_time_ms if intermediate.result_time_ms is not None else 0
            intermediates[distance]["is_outlier"] = intermediate.is_outlier
    return intermediates

def calculateIntermediateTimes(intermediates: dict) -> dict:
    """
    Extend intermediates dictionary with pace, speed and relative speed
    Args:
        Dictionary: intermediates[distance][metric]
        -> distance: 500, 1000, 1500, 2000
        -> metric: 'rank', 'time [millis]', 'is_outlier'
    Returns:
        Dictionary: intermediates[distance][metric]
        -> distance: 500, 1000, 1500, 2000
        -> metric: 'rank', 'time [millis]', 'is_outlier', 'pace [millis]', 'speed [m/s]', 'rel_speed [%]'
    """
    time = 0
    total_time = intermediates[2000]["time [millis]"]
    for key, value in intermediates.items():
        pace = value["time [millis]"] - time
        intermediates[key]["pace [millis]"] = pace
        time = value["time [millis]"]
        if pace != 0:
            intermediates[key]["speed [m/s]"] = 500 / pace * 1000 
            intermediates[key]["rel_speed [%]"] =  total_time / (4 * pace)
        else:
            intermediates[key]["speed [m/s]"] = 0
            intermediates[key]["rel_speed [%]"] = 0

    return intermediates

def calculateConfidenceIntervall(sample_data: list) -> tuple:
    """
    Calculate the 95% confidence interval from sample data.
    The true population mean lies with 95% certainty in the computed range.

    Args:
        sample_data (List): Mean values from all race boats in sample

    Returns:
        Tuple: Containing mean (float), lower bound (float), upper bound (float) of 95% ci.
    """
    sample_data = list(filter(lambda x: x is not None and x > 0, sample_data)) #Filter none and 0 values
    n = len(sample_data)
    if n == 0:
        return 0, 0, 0
    elif n == 1:
        return sample_data[0], sample_data[0], sample_data[0]
    else:
        mean = np.mean(sample_data)
        std_dev = np.std(sample_data, ddof=1)  # ddof=1 for sample standard deviation
        std_error = std_dev / math.sqrt(n)
        
        if n<= 30: 
            critical_value = stats.t.ppf(1 - 0.05/2, n - 1) #t-value for 95% confidence
        else:
            critical_value = 1.96  #z-value for large sample sizes

        margin_of_error = critical_value * std_error

        #Calculate confidence Intervall
        lower = mean - margin_of_error
        upper = mean + margin_of_error

        return mean, lower, upper

def getPacingProfile(t1: float, t2: float, t3: float, t4: float) -> str:
    """Identify Pacing Profile based on 500m times."""
    pacing_profile = "Other"
    t_average = (t1 + t2 + t3 + t4) / 4
    if _isEven(t1, t_average) and _isEven(t2, t_average) and _isEven(t3, t_average) and _isEven(t4, t_average):
        pacing_profile = "Even"
    elif t1 < t4 and t4 < min(t2, t3):
        pacing_profile = "Reverse J-Shape"
    elif t4 < t1 and t1 < min(t2, t3):
        pacing_profile = "J-Shape"
    elif t1 < t2 and t2 < min(t3, t4):
        pacing_profile = "Negative"
    elif t4 < t3 and t3 < min(t1, t2):
        pacing_profile = "Positive"
    return pacing_profile

def _isEven(ta: float, t_average: float) -> bool:
    """Check if time 'ta' is within a 1% difference from average time 't_average'."""
    if t_average == 0:
        return False
    relative_time = ta / t_average
    return 0.99 <= relative_time and relative_time <= 1.01

def _getOlympicCycle(year: int):
    """Find period of olymic cycle for given year."""
    start_year = year - (year + 3) % 4
    end_year = year + (3 - (year + 3) % 4)
    if (start_year == 2021):
        start_year = 2022
    if (end_year == 2020):
        end_year = 2021
    return f"{start_year}-{end_year}"

def getOzBestTime(boat_class: str, year: int) -> int:
    """
    Gets the best time of a boat class before a specific Olympia Cycle.
    Data from wbt.csv file.

    Args:
        boat_class (String): boat class abbreviation (e.g. M1x)
        column (String): olympia cycle period (e.g. 2022-2024)
    
    Returns:
        String: best time in format 'M:SS,MS'    
    """
    column_name = _getOlympicCycle(year)
    try:
        df = pd.read_csv('/usr/src/app/wbt.csv', sep=';', index_col=0)
        best_time = df.loc[boat_class, column_name]
        return _convertToMs(best_time)
    except:
        return 0
    
def _convertToMs(time: str) -> int:
    """Convert time with format 'M:SS,MS' to milliseconds."""
    time_format = "%M:%S,%f"
    time_obj = datetime.datetime.strptime(time, time_format)
    total_milliseconds = (time_obj.minute * 60 * 1000) + (time_obj.second * 1000) + int(time_obj.microsecond / 1000)
    return total_milliseconds

def getWorldBestTime(boat_class: str, session) -> int:
    """Get the world best time of a boat class"""
    statement = select(model.Boat_Class).where(model.Boat_Class.abbreviation == boat_class)
    boat_class_object = session.execute(statement).scalars().first()
    world_best_race_boat = boat_class_object.world_best_race_boat
    if world_best_race_boat:
        return world_best_race_boat.result_time_ms
    else:
        return 0


def getAthletes(race_boat_athletes: model.Association_Race_Boat_Athlete) -> dict:
    '''
    Get information of all athletes in boat.
    
    Returns:
        Dict: athletes{0:{id, first_name, last_name, full_name, boat_position}, 1:{...}, ...}
    '''
    sorted_athletes = sorted(race_boat_athletes, key=lambda x: (x.boat_position != 'b', x.boat_position))
    athlete_assoc: model.Association_Race_Boat_Athlete
    athletes = {}
    for idx, athlete_assoc in enumerate(sorted_athletes):
        athlete: model.Athlete = athlete_assoc.athlete
        athletes[idx] = {
            "id": athlete.id,
            "first_name": athlete.first_name__,
            "last_name": athlete.last_name__,
            "full_name": athlete.name,
            "boat_position": athlete_assoc.boat_position
        }
    return athletes

def getPhaseType(phase_type: str, phase_subtype: str, phase_num: int) -> str:
    "Merge phase type, subtype and number into one string"
    phase_subtype = phase_subtype if phase_subtype else ""
    phase_string = globals.RACE_PHASE_MAPPING.get(phase_type + phase_subtype + str(phase_num))
    return phase_string if phase_string else phase_type + str(phase_num)

def separatePhaseTypes(phases: list):
    "Separate phase types, into phase type and phase number (-> in this case phase number only relevant for final)"
    mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
    phase_type = set()
    phase_number = set()
    phase: str
    for phase in phases:
        if phase == 'final':
            continue
        elif phase[:5] == "final":
            phase_type.add("final")
            phase_number.add(mapping[phase[-1]])
        else:
            phase_type.add(phase)
    return list(phase_type), list(phase_number)


if __name__ == '__main__':
    from sys import exit as sysexit
    pass        #replace for testing purposes
    sysexit()
