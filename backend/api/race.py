import datetime
from collections import OrderedDict, defaultdict
from contextlib import suppress
import itertools
import statistics
from collections.abc import Iterable

from scipy import stats
import numpy as np
import math

from sqlalchemy import select, or_, and_, func

from common.helpers import stepfunction
from model import model

COND_VALID_2000M_RESULTS = and_(
    model.Intermediate_Time.distance_meter == 2000,
    model.Intermediate_Time.result_time_ms != None,
    model.Intermediate_Time.invalid_mark_result_code_id == None,
    or_(
        model.Intermediate_Time.is_outlier == False,
        model.Intermediate_Time.is_outlier == None
    )
)

def result_time_best_of_year_interval(session, boat_class_id, year_start,
                                      year_end=datetime.date.today().year):
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

def _skipping_non_int(values):
    """iterates only ints"""
    return ( val for val in values if isinstance(val,int) )

def _skip_NoneType(values):
    """drop None values"""
    return ( val for val in values if val != None )

def _find_min_difference(values):
    min_diff = None
    last_val = None
    for idx, val in enumerate(_skipping_non_int(values)):
        first_loop = idx == 0
        if first_loop:
            last_val = val
            continue

        diff = val - last_val
        min_diff = diff if min_diff == None else min(diff, min_diff)
        last_val = val
    return min_diff

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

def _instantaneous_speed(figures_dict, grid_resolution):
    pace = figures_dict.get('pace', None)
    if pace != None:
        return grid_resolution/pace
    return None

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

def getIntermediateTimes(race_boat):
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

def calculateIntermediateTimes(intermediates):
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

#Calculate the 95% confidence interval for population mean
#n <= 30, t-distribution, n>30 z-distribution
#return mean, lower, upper
def calculateConfidenceIntervall(sample_data):
    sample_data = list(filter(lambda x: x is not None and x != 0, sample_data)) #Filter none and 0 values
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

#Possible pacing profiles are: Even, J-shape, Reverse J-shape, negativ, positiv, other
def getPacingProfile(t1, t2, t3, t4):
    pacing_profile = "Other"
    t_average = (t1 + t2 + t3 + t4) / 4
    if isEven(t1, t_average) and isEven(t2, t_average) and isEven(t3, t_average) and isEven(t4, t_average):
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

def isEven(ta, t_average):
    if t_average == 0:
        return False
    relative_time = ta / t_average
    return 0.99 <= relative_time and relative_time <= 1.01


if __name__ == '__main__':
    from sys import exit as sysexit

    with model.Scoped_Session() as session:
        stmt = (select(model.Race))
        iterator = session.execute(stmt).scalars()
        for race in iterator:
            result = compute_intermediates_figures(race.race_boats)
            break

    sysexit()

    with model.Scoped_Session() as session:
        for boat_class in session.scalars(select(model.Boat_Class)):
            res = result_time_best_of_year_interval(
                session=session,
                boat_class_id=boat_class.id,
                year_start=2020
            )
            print('result_time_best_of_last_n_years', res)