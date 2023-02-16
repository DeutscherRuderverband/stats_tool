import datetime
from collections import OrderedDict, defaultdict
import itertools
import statistics

from sqlalchemy import select, or_, and_, func

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


def _transpose_boatclass_intermediates(race_boats) -> OrderedDict:
    transposed = dict()
    race_boat: model.Race_Boat
    for race_boat in race_boats:
        intermediate: model.Intermediate_Time
        for intermediate in race_boat.intermediates:
            dist = intermediate.distance_meter
            if not dist in transposed:
                transposed[dist] = []
            transposed[dist].append(intermediate)
    return transposed

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
        interm.invalid_mark_result_code_id == None
        and not interm.is_outlier
        and not interm.result_time_ms == None
    )

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
    dict_key = lambda i: i[0]
    lookup = _transpose_boatclass_intermediates(race_boats)
    lookup = OrderedDict( sorted(lookup.items(), key=dict_key ) )
    grid_resolution = _find_min_difference(lookup.keys())
    if grid_resolution == None:
        return []

    result = defaultdict(lambda: defaultdict(dict))
    last_distance = 0
    last_valid_intermeds_lookup = {}
    first_distance = True
    for distance, intermediates in lookup.items():
        valid_intermediates = tuple(( i for i in intermediates if valid_intermediate(i) ))
        result_times = tuple( map(lambda i: i.result_time_ms, valid_intermediates) )
        
        best_time = min(result_times)

        valid_intermeds_lookup = {}
        intermediate: model.Intermediate_Time
        for intermediate in intermediates:
            figures = {
                "deficit": None,
                "rel_diff_to_avg_speed": None,
                "pace": None,
                "speed": None,
                "result_time": None
            }
            result[intermediate.race_boat_id][distance] = figures

            if not valid_intermediate(intermediate):
                inv_mark_code = intermediate.invalid_mark_result_code_id
                if inv_mark_code:
                    figures["result_time"] = inv_mark_code
                else:
                    pass # is outlier -> leaves "result_time" as None
                continue

            valid_intermeds_lookup[intermediate.race_boat_id] = intermediate

            # relative to best boat
            deficit = intermediate.result_time_ms - best_time

            pace = None
            within_grid_resolution = (distance - last_distance) == grid_resolution
            if within_grid_resolution:
                if first_distance:
                    pace = intermediate.result_time_ms
                elif intermediate.race_boat_id in last_valid_intermeds_lookup:
                    last_result_time = last_valid_intermeds_lookup[intermediate.race_boat_id].result_time_ms
                    pace = intermediate.result_time_ms - last_result_time
        
            speed = None
            if pace != None:
                pace_in_seconds = pace / 1000 # assuming milliseconds here
                speed = grid_resolution/pace_in_seconds

            figures["deficit"] = deficit
            figures["pace"] = pace
            figures["speed"] = speed
            figures["result_time"] = intermediate.result_time_ms

        # now we have all the pace values, we can compute avg speeds
        avg_speed = statistics.mean(_skip_NoneType(_speeds(boats_dict=result, distance=distance)))

        for race_boat_id, intermediate in valid_intermeds_lookup.items():
            figures = result[intermediate.race_boat_id][distance]
            speed = figures['speed']
            rel_diff_to_avg_speed = (speed - avg_speed) / avg_speed * 100.0
            figures["rel_diff_to_avg_speed"] = rel_diff_to_avg_speed

        first_distance = False
        last_distance = distance
        last_valid_intermeds_lookup = valid_intermeds_lookup

    return result


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