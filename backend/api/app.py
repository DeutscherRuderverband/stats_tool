import os
from secrets import token_hex
import datetime
import json
from collections import OrderedDict
from statistics import stdev, median, mean
import numpy as np
from collections import OrderedDict

from flask import Flask
from flask import request
from flask import abort, jsonify
from flask import Response
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

# disable auth by uncommenting the following line
# jwt_required = lambda: (lambda x: x) # disable auth

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

from . import auth
from model import model
from .race import result_time_best_of_year_interval, compute_intermediates_figures
from common.rowing import propulsion_in_meters_per_stroke
from . import mocks  # todo: remove me
from . import globals

# app is the main controller for the Flask-Server and will start the app in the main function 
app = Flask(__name__, template_folder=None)
app.config['JSON_SORT_KEYS'] = False

# NOTE that the following line opens ALL endpoints for cross-origin requests!
# This has to be tied to the actual public frontend domain as soon as a
# serious authentication system is implemented. See docs of flask_cors
CORS(app)

# Auth / JWT
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY') or token_hex(16)
jwt = JWTManager(app)

# used similar to a context manager. using the constructor creates a scoped session, bound to its creating function scope 
Scoped_Session = model.Scoped_Session


# Receive JSON via POST in flask: https://sentry.io/answers/flask-getting-post-data/#json-data
# Parameterized route etc.: https://pythonbasics.org/flask-tutorial-routes/
# Route syntax doc: https://flask.palletsprojects.com/en/2.2.x/api/#url-route-registrations
# Multiple Joins: https://docs.sqlalchemy.org/en/14/orm/queryguide.html#chaining-multiple-joins


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("user", "")
    password = request.json.get("pass", "")
    authorized = auth.hashed(password) == auth.MASTER_PASSWORD_HASHED
    if not authorized:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/report', methods=['POST'])
@jwt_required()
def get_report():
    """
    
    """
    filter_dict = request.json
    data = mocks.generic_get_data(_filter=filter_dict)
    return data


@app.route('/healthcheck')
def healthcheck():
    return "healthy"


@app.route('/competition_category/', methods=['GET', 'POST'])
@jwt_required()
def get_competition_categories():
    """
    todo: comment
    """
    result = []

    session = Scoped_Session()
    iterator = session.execute(select(model.Competition_Category)).scalars()
    for entity in iterator:
        mapped = {"id": entity.id, "display_name": entity.name}
        result.append(mapped)

    return result


@app.route('/boatclass_information')
@jwt_required()
def get_boatclass_information() -> dict:
    return globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT


@app.route('/competition_category_information')
@jwt_required()
def get_competition_category_information() -> dict:
    session = Scoped_Session()
    statement = (
        select(
            model.Competition_Type.additional_id_,
            model.Competition_Type.name,
            model.Competition_Type.abbreviation
        )
    )

    return {
        v[0]: (
            v[1], 
            globals.ALLOWED_COMPETITION_TYPES_MAPPING[v[2]]
            ) 
        for v in session.execute(statement).fetchall()
        if v[2] in globals.ALLOWED_COMPETITION_TYPES_MAPPING
        }


@app.route('/competition', methods=['POST'])
@jwt_required()
def get_competitions_year_category() -> dict:
    """
    WHEN?
    This endpoint is used, when the user is on the page for the 'Rennstrukturanalyse' and selected filter for
        - year
        - competition_category
    of interest.
    @param filter_dict: example for filter_dict {  "year": 2008, "competition_category_id": 5  }
    @return: nested dict/json: structure containing competitions, their events and their races respectively.
    See https://github.com/N10100010/DRV_project/blob/api-design/doc/backend-api.md#user-auswahl-jahr-einzeln-und-wettkampfklasse-zb-olympics for mock of return value.

    """
    from datetime import datetime
    import logging

    year = request.json["data"].get('year')
    competition_category_id = request.json["data"].get('competition_category_id')

    logging.debug(f"Year: {year}, comp cat: {competition_category_id}")

    session = Scoped_Session()

    statement = (
        select(
            model.Competition
        )
        .join(model.Competition.competition_category)
        .where(
            and_(
                model.Competition_Category.id == competition_category_id,
                model.Competition.year == year,
            )
        )
    )

    filtered_competitions = session.execute(statement).fetchall()

    competitions = []
    for _comp in filtered_competitions:
        _comp = _comp['Competition']
        _venue = _comp.venue
        _country = _venue.country
        comp = {
            "id": _comp.id,
            "name": _comp.name,
            "start": _comp.start_date,
            "end": _comp.end_date,
            "venue": f"{_venue.site}/{_venue.city}, {_country.name}",
        }

        events = []
        for _event in _comp.events:
            event = {
                "id": _event.id,
                "name": _event.name,
                "boat_class": _event.boat_class.abbreviation
            }

            races = []
            for _race in _event.races:
                race = {
                    "id": _race.id,
                    "name": _race.name,
                    "phase_type": _race.phase_type,
                    "sub_phase": _race.phase_number if _race.phase_number else _race.phase_subtype
                }
                races.append(race)

            event['races'] = races
            events.append(event)

        comp['events'] = events
        competitions.append(comp)

    return competitions


@app.route('/matrix', methods=['POST'])
@jwt_required()
def get_matrix() -> dict:
    """
        todo: How to realize the filtering? 
        @Harri: if a filter is filtering for all, do not put the filter in there 
    """
    filter_key_mapping = {
        'gender': model.Event.gender_id,  # list
        'boat_class': model.Boat_Class.id,  # list
        'interval': model.Competition.year,  # tuple
        'competition_category': model.Competition_Category.id,  # list
        'race_phase_type': model.Race.phase_type,  # list
        'race_phase_subtype': model.Race.phase_number,  # list
        'placement': model.Race_Boat.rank  # list
    }

    # remove None's from the filters
    filters = {k: v for k, v in request.json['data'].items() if v}

    # example filter args 
    # filters = {'gender': [1]}

    session = Scoped_Session()
    avg_times_statement = (
        select(
            func.avg(model.Intermediate_Time.result_time_ms).label("mean"),
            func.min(model.Intermediate_Time.result_time_ms).label("min"),
            func.count(model.Intermediate_Time.race_boat_id).label("cnt"),
            model.Boat_Class.additional_id_.label("id")  # add_id_
        )
        .join(model.Intermediate_Time.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.boat_class)
        .where(
            model.Intermediate_Time.distance_meter == 2000,
            # model.Intermediate_Time.is_outlier == True,
            model.Intermediate_Time.result_time_ms != 0
        )
        .group_by(
            model.Boat_Class.additional_id_
        )
    )

    for k, v in filters.items():
        if k == 'interval':
            avg_times_statement = avg_times_statement.where(filter_key_mapping[k].between(v[0], v[1]))
        else:
            avg_times_statement = avg_times_statement.where(filter_key_mapping[k].in_(v))

    wbt_statement = (
        select(
            model.Boat_Class.additional_id_,
            model.Race_Boat.result_time_ms
        )
        .join(model.Race_Boat)
    )

    avg_times = session.execute(avg_times_statement).fetchall()
    wbts = session.execute(wbt_statement).fetchall()

    result = {}

    for time in avg_times:
        wbt = [wbt for wbt in wbts if wbt[0] == time.id]
        if len(wbt) < 1:
            wbt = time.min
            used_wbt = True
        else:
            wbt = wbt[0][1]
            used_wbt = False

        result[time.id] = {
            'wbt': wbt,
            'mean': time.mean,
            'delta': float(time.mean) - float(wbt),
            'count': time.cnt,
            'used_wbt': used_wbt
        }
    return result


@app.route('/get_race/<int:race_id>/', methods=['GET'])
@jwt_required()
def get_race(race_id: int) -> dict:
    """
    WHEN? THIS FUNCTION IS CALLED WHEN THE USER SELECTED A RACE 
    Gets the mandatory information to display a race-analysis (Rennstrukturanalyse).
    @race_id: the internal, unique id identifying a race. 
    @return: the information of a race
    """
    session = Scoped_Session()

    # Join relationship fields using "Joined Load" to fetch all-in-one:
    #   https://docs.sqlalchemy.org/en/14/orm/tutorial.html#joined-load
    #   https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#sqlalchemy.orm.joinedload
    statement = (
        select(model.Race)
        .where(model.Race.id == int(race_id))
        .options(
            joinedload(model.Race.race_boats)
            .joinedload(model.Race_Boat.intermediates),
            joinedload(model.Race.event)
            .options(
                joinedload(model.Event.boat_class),
                joinedload(model.Event.competition)
                .joinedload(model.Competition.venue)
                .joinedload(model.Venue.country)
            )
        )
    )

    race: model.Race
    race = session.execute(statement).scalars().first()
    if race == None:
        abort(404)

    venue = race.event.competition.venue

    world_best_race_boat = race.event.boat_class.world_best_race_boat
    world_best_time_ms = None
    if world_best_race_boat:
        world_best_time_ms = world_best_race_boat.result_time_ms

    best_of_last_4_years_ms = result_time_best_of_year_interval(
        session=session,
        boat_class_id=race.event.boat_class.id,
        year_start=datetime.date.today().year - 4
    )

    intermediates_figures = compute_intermediates_figures(race.race_boats)

    result = {
        "race_id": race.id,
        "display_name": race.name,
        "start_date": str(race.date),
        "venue": f"{venue.site}/{venue.city}, {venue.country.name}",
        "boat_class": race.event.boat_class.abbreviation,  # long name?
        "result_time_world_best": world_best_time_ms,
        "result_time_best_of_current_olympia_cycle": best_of_last_4_years_ms,  # int in ms
        "progression_code": race.progression,
        "pdf_urls": {
            "result": race.pdf_url_results,
            "race_data": race.pdf_url_race_data
        },
        "race_boats": []
    }

    sorted_race_boat_data = sorted(race.race_boats, key=lambda x: x.rank)
    race_boat: model.Race_Boat
    for race_boat in sorted_race_boat_data:
        rb_result = {
            "name": race_boat.name,  # e.g. DEU2
            "lane": race_boat.lane,
            "rank": race_boat.rank,
            "athletes": [],
            "intermediates": OrderedDict(),
            "race_data": OrderedDict()
        }
        result['race_boats'].append(rb_result)

        # athletes
        athlete_assoc: model.Association_Race_Boat_Athlete
        for athlete_assoc in race_boat.athletes:
            athlete: model.Athlete = athlete_assoc.athlete
            rb_result['athletes'].append({
                "id": athlete.id,
                "first_name": athlete.first_name__,
                "last_name": athlete.last_name__,
                "full_name": athlete.name,
                "boat_position": athlete_assoc.boat_position
            })

        # race_data aka gps data
        sorted_race_data = sorted(race_boat.race_data, key=lambda x: x.distance_meter)
        race_data: model.Race_Data
        for race_data in sorted_race_data:
            propulsion = propulsion_in_meters_per_stroke(race_data.stroke, race_data.speed_meter_per_sec)
            rb_result['race_data'][str(race_data.distance_meter)] = {
                "speed [m/s]": race_data.speed_meter_per_sec,
                "stroke [1/min]": race_data.stroke,
                "propulsion [m/stroke]": propulsion
            }

        # intermediates
        sorted_intermediates = sorted(race_boat.intermediates, key=lambda x: x.distance_meter)
        intermediate: model.Intermediate_Time
        for intermediate in sorted_intermediates:
            figures = intermediates_figures[intermediate.race_boat_id][intermediate.distance_meter]
            result_time_ms = intermediate.result_time_ms
            if intermediate.is_outlier:
                continue
            if intermediate.invalid_mark_result_code:
                result_time_ms = intermediate.invalid_mark_result_code.id

            rb_result['intermediates'][str(intermediate.distance_meter)] = {
                "rank": intermediate.rank,
                "time [millis]": result_time_ms,
                "pace [millis]": figures.get('pace'),
                "speed [m/s]": figures.get('speed'),
                "deficit [millis]": figures.get('deficit'),
                "rel_diff_to_avg_speed [%]": figures.get('rel_diff_to_avg_speed')
            }
            # relative difference to average time at this mark

    return Response(json.dumps(result, sort_keys=False), content_type='application/json')


@app.teardown_appcontext
def shutdown_session(exception=None):
    ''' Enable Flask to automatically remove database sessions at the
    end of the request or when the application shuts down.
    Ref: http://flask.pocoo.org/docs/patterns/sqlalchemy/
    Ref: https://stackoverflow.com/a/45719168
    '''
    Scoped_Session.remove()


# @app.route('/result', 'POST')
# def get_result(filter_dict: dict):
#     """

#     """
#     data = mocks.generic_get_data(_filter=filter_dict)
#     return data


# @app.route('/analysis', 'POST')
# def get_analysis(filter_dict: dict) -> Union[list, dict]:
#     """
#     When?
#     This endpoint is used, when the user is on the page for the 'Rennstrukturanalyse' and selected filter for
#         - year
#         - competition_category
#     of interest.
#     @param filter_dict: example for filter_dict {  "year": 2008, "competition_category_id": 5  }
#     @return: nested dict/json: structure containing competitions, their events and their races respectively.
# See https://github.com/N10100010/DRV_project/blob/api-design/doc/backend-api.md#user-auswahl-jahr-einzeln-und-wettkampfklasse-zb-olympics for mock of return value.
#     """
#     # data = generic_get_data(_filter=filter_dict)
#     data = mocks.mock_standard_analysis_endpoint()
#     return data


# @app.route('/analysis/<race_id>', 'GET')
# def get_race_analysis(race_id: str):
#     race_id = "bcda473e-f602-4747-a61e-a35963bd7198"
#     # data = generic_get_data(_filter={'id': race_id})
#     data = mocks.mock_race_analysis_endpoint()
#     return data


# @app.route('/get_report_filter_options', 'GET')
# def get_report_filter_options(filter_dict: dict):
#     """
#     todo:
#     """
#     return {}


@app.route('/get_report_boat_class', methods=['POST'])
@jwt_required()
def get_report_boat_class():
    """
    Delivers the report results for a single boat class.
    """
    filter_data = request.json["data"]
    filter_keys = ["interval", "competition_category", "boat_class", "race_phase_type",
                   "race_phase_subtype" "placement"]
    interval, competition_categories, boat_class, runs, ranks = [filter_data.get(key) for key in filter_keys]
    start_year, end_year = interval[0], interval[1]

    # read from db
    session = Scoped_Session()
    start_date = func.to_timestamp(func.concat(start_year, "-01-01 00:00:00"), 'YYYY-MM-DD HH24:MI:SS')
    end_date = func.to_timestamp(func.concat(end_year, "-12-31 23:59:59"), 'YYYY-MM-DD HH24:MI:SS')

    statement = (
        select(
            model.Race.id.label("race_id"),
            model.Competition.id.label("competition_id")
        )
        .join(model.Race.event)
        .join(model.Event.competition)
        .join(model.Competition.competition_category)
        .where(and_(
            model.Race.date >= start_date,
            model.Race.date <= end_date,
            model.Event.boat_class_id == model.Boat_Class.id,
            model.Boat_Class.additional_id_ == boat_class,
            model.Competition_Category.competition_type_id.in_(competition_categories)
        ))
    )

    result = session.execute(statement).fetchall()
    boat_class_name, wb_time, lowest_time_period = "", 0, 0
    race_times, race_dates, int_times_500, int_times_1000 = [], [], [], []
    comp_categories = set()

    for row in result:
        race_id, competition_id = row
        race = session.query(model.Race).get(race_id)
        boat_class_name = race.event.boat_class.abbreviation
        comp_categories.add(race.event.competition.competition_category.name)

        world_best_race_boat = race.event.boat_class.world_best_race_boat
        if world_best_race_boat:
            wb_time = world_best_race_boat.result_time_ms

        for race_boat in race.race_boats:
            if race_boat.result_time_ms and race.date and race.phase_type in runs \
                    and (race_boat.rank in ranks if ranks else True):
                race_times.append(race_boat.result_time_ms)
                date = race.date
                race_dates.append(
                    '{:02d}'.format(date.year) + '-{:02d}'.format(date.month) + '-{:02d}'.format(date.day))
                intermediate_times_for_race_boat = session.query(model.Intermediate_Time).filter(
                    model.Intermediate_Time.race_boat_id == race_boat.id).all()
                for intermediate_time in intermediate_times_for_race_boat:
                    if intermediate_time.distance_meter == 500:
                        int_times_500.append(intermediate_time.result_time_ms)
                    elif intermediate_time.distance_meter == 1000:
                        int_times_1000.append(intermediate_time.result_time_ms)

    avg_500_time = int(mean(int_times_500)) if int_times_500 else 0
    avg_1000_time = int(mean(int_times_1000)) if int_times_1000 else 0

    results, mean_speed, mean_time, stdev_race_time, median_race_time = 0, 0, 0, 0, 0
    hist_data, hist_labels = [], []
    fastest_times_mean, fastest_times_n = 0, 0
    medium_times_mean, medium_times_n = 0, 0
    slow_times_mean, slow_times_n = 0, 0
    slowest_times_mean, slowest_times_n = 0, 0
    sd_1_low, sd_1_high = 0, 0
    hist_mean, hist_sd_low, hist_sd_high = 0, 0, 0

    if race_times:
        results = len(race_times)
        lowest_time_period = min(race_times)
        # TODO: Set race length dynamically
        race_distance = 2000
        mean_speed = round(mean([race_distance / (time / 1000) for time in race_times]), 2)
        mean_time = int(mean(race_times))
        stdev_race_time = int(stdev(race_times))
        median_race_time = int(median(race_times))

        hist_data, bin_edges = np.histogram(race_times, bins="fd")
        hist_data = hist_data.tolist() if len(hist_data) > 0 else []
        hist_labels = [int(bin_edge) for bin_edge in bin_edges]
        hist_mean = np.average(bin_edges[:-1], weights=hist_data)
        hist_var = np.average((bin_edges[:-1] - hist_mean) ** 2, weights=hist_data)
        hist_std = np.sqrt(hist_var)
        hist_sd_low = hist_mean - hist_std
        hist_sd_high = hist_mean + hist_std

        fastest_times = [x for x in race_times if x < (mean_time - stdev_race_time)]
        medium_times = [x for x in race_times if
                        (mean_time - stdev_race_time) < x < (mean_time - (1 / 3 * stdev_race_time))]
        slow_times = [x for x in race_times if
                      (mean_time - (1 / 3 * stdev_race_time)) < x < (mean_time + (1 / 3 * stdev_race_time))]
        slowest_times = [x for x in race_times if x > (mean_time + (1 / 3 * stdev_race_time))]

        fastest_times_n = len(fastest_times)
        medium_times_n = len(medium_times)
        slow_times_n = len(slow_times)
        slowest_times_n = len(slowest_times)

        fastest_times_mean = int(mean(fastest_times))
        medium_times_mean = int(mean(medium_times))
        slow_times_mean = int(mean(slow_times))
        slowest_times_mean = int(mean(slowest_times))

        sd_1_low = mean_time - stdev_race_time
        sd_1_high = mean_time + stdev_race_time

    return json.dumps({
        "competition_categories": list(comp_categories),
        "results": results,
        "boat_classes": boat_class_name,
        "start_date": start_year,
        "end_date": end_year,
        "world_best_time_boat_class": wb_time,
        "best_in_period": lowest_time_period,
        "mean": {
            "mm:ss,00": mean_time,
            "m/s": mean_speed,
            "pace 500m": avg_500_time,
            "pace 1000m": avg_1000_time
        },
        "std_dev": stdev_race_time,
        "median": median_race_time,
        "gradation_fastest": {
            "results": fastest_times_n,
            "time": fastest_times_mean
        },
        "gradation_medium": {
            "results": medium_times_n,
            "time": medium_times_mean
        },
        "gradation_slow": {
            "results": slow_times_n,
            "time": slow_times_mean
        },
        "gradation_slowest": {
            "results": slowest_times_n,
            "time": slowest_times_mean
        },
        "plot_data": {
            "histogram": {
                "labels": hist_labels,
                "data": hist_data,
            },
            "histogram_mean": int(hist_mean),
            "histogram_sd_low": int(hist_sd_low),
            "histogram_sd_high": int(hist_sd_high),
            "scatter_plot": {
                "labels": race_dates,
                "data": race_times
            },
            "scatter_1_sd_low": {
                "labels": [
                    f'{start_year}-01-01', f'{end_year}-12-30'
                ],
                "data": [sd_1_low, sd_1_low]
            },
            "scatter_1_sd_high": {
                "labels": [
                    f'{start_year}-01-01', f'{end_year}-12-30'
                ],
                "data": [sd_1_high, sd_1_high]
            },
            "scatter_mean": {
                "labels": [
                    f'{start_year}-01-01', f'{end_year}-12-30'
                ],
                "data": [mean_time, mean_time]
            }
        }
    })


@app.route('/get_athlete/<int:athlete_id>', methods=['GET'])
@jwt_required()
def get_athlete(athlete_id: int):
    """
    Give athlete data for specific athlete
    """
    session = Scoped_Session()
    athlete = session.query(model.Athlete).filter_by(id=int(athlete_id)).first()
    athlete_race_boats = [race_boat.race_boat_id for race_boat in athlete.race_boats]

    # get race_boat related data
    race_boats = session.query(model.Race_Boat).filter(model.Race_Boat.id.in_(athlete_race_boats)).all()

    race_results, race_ids, athlete_boat_classes, best_time_boat_class, nation = {}, [], set(), "", ""
    total, gold, silver, bronze, final_a, final_b = 0, 0, 0, 0, 0, 0

    for i, race_boat in enumerate(race_boats):
        race_ids.append(race_boat.race_id)
        if race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 1:
            final_a += 1
            if race_boat.rank == 1:
                gold += 1
                total += 1
            elif race_boat.rank == 2:
                silver += 1
                total += 1
            elif race_boat.rank == 3:
                bronze += 1
                total += 1
        elif race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 2:
            final_b += 1

        race_results[i] = {
            "race_id": race_boat.race_id,
            "time": race_boat.result_time_ms,
            "rank": race_boat.rank,
            "boat_class": None,
            "start_time": None
        }
        nation = race_boat.country.country_code

    races = session.query(model.Race).filter(model.Race.id.in_(race_ids)).all()

    gender, athlete_disciplines = set(), set()
    for i, race in enumerate(races):
        gender.add(race.event.gender.name)
        comp = session.query(model.Competition).filter(model.Competition.id == race.event.competition_id).one()
        boat_class_name = race.event.boat_class.abbreviation
        best_time_boat_class = str(race.event.boat_class.world_best_race_boat)
        athlete_boat_classes.add(boat_class_name)

        # check disciplines
        if any(ath.endswith("x") for ath in athlete_boat_classes):
            athlete_disciplines.add("Skull")
        elif not any(ath.endswith("x") for ath in athlete_boat_classes):
            athlete_disciplines.add("Riemen")

        comp_type = race.event.competition.competition_category.name
        race_results[i]["name"] = comp.name
        race_results[i]["venue"] = f'{comp.venue.city}, {comp.venue.country.name}'
        race_results[i]["boat_class"] = boat_class_name
        race_results[i]["start_time"] = str(race.date)
        race_results[i]["competition_category"] = comp_type

    return json.dumps({
        "name": athlete.name,
        "athlete_id": athlete.id,
        "nation": nation,
        "gender": gender.pop(),
        "dob": str(athlete.birthdate),
        "weight": athlete.weight_kg__,
        "height": athlete.height_cm__,
        "disciplines": list(athlete_disciplines),
        "boat_class": ", ".join(athlete_boat_classes),
        "medals_total": total,
        "medals_gold": gold,
        "medals_silver": silver,
        "medals_bronze": bronze,
        "final_a": final_a,
        "final_b": final_b,
        "world_best_boat_class": best_time_boat_class,
        "best_time_current_oz": None,  # TODO: Where to find this?
        "num_of_races": len(athlete_race_boats),
        "race_list": race_results,
    })


@app.route('/get_athlete_by_name/', methods=['POST'])
@jwt_required()
def get_athlete_by_name():
    """
    Delivers the athlete search result depending on the search query.
    @Params: search_query string and filter data
    """
    data = request.json["data"]
    search_query = data["search_query"]
    birth_year = data["birth_year"]
    nation = data["nation"][:3] if data["nation"] else None
    boat_class = data["boat_class"]

    session = Scoped_Session()
    athletes = session.query(model.Athlete).filter(
        or_(
            model.Athlete.first_name__.ilike(search_query),
            model.Athlete.last_name__.ilike(search_query)
        )
    ).all()
    output_athletes = set(athletes)
    if nation or boat_class:
        output_athletes = set()
        for athlete in athletes:
            athlete_race_boat_ids = [race_boat.race_boat_id for race_boat in athlete.race_boats]
            race_boats = session.query(model.Race_Boat).filter(model.Race_Boat.id.in_(athlete_race_boat_ids)).all()
            athlete_nations = set(race_boat.country.country_code for race_boat in race_boats)
            race_ids = [race_boat.race_id for race_boat in race_boats]
            races = session.query(model.Race).filter(model.Race.id.in_(race_ids)).all()
            race_boat_classes = set(race.event.boat_class.additional_id_ for race in races)
            if nation and nation in athlete_nations:
                output_athletes.add(athlete)
            if boat_class and boat_class in race_boat_classes:
                output_athletes.add(athlete)

    if birth_year:
        output_athletes = [athlete for athlete in output_athletes if athlete.birthdate.year == birth_year]

    return json.dumps([{
        "name": f"{athlete.last_name__}, {athlete.first_name__} ({athlete.birthdate})",
        "id": athlete.id,
    } for athlete in output_athletes])


@app.route('/get_athletes_filter_options', methods=['GET'])
@jwt_required()
def get_athletes_filter_options():
    """
    Delivers the filter options for the athletes page.
    """
    session = Scoped_Session()
    iterator = session.execute(select(model.Athlete)).scalars()
    birth_years = [entity.birthdate.year for entity in iterator]

    return json.dumps([{
        "birth_years": [
            {"start_year": min(birth_years)},
            {"end_year": max(birth_years)}],
        "nations": {entity.country_code: entity.name for entity in
                    session.execute(select(model.Country)).scalars()},
        "boat_classes": {
            'men': {
                'u19': {
                    'single': ("JM1x", "Junior Men's Single Sculls", "079e71bb-98cd-47f4-8ca4-e3fd0cdbc538"),
                    'double': ("JM2x", "Junior Men's Double Sculls", "78f004f6-cadd-4d0f-804b-21cf26458355"),
                    'quad': ("JM4x", "Junior Men's Quadruple Sculls", "dc9439cd-36d9-47fd-a205-bc2612f4f83b"),
                    'pair': ("JM2-", "Junior Men's Pair", "5851b9f9-5240-4fea-a19e-43b24eb99a10"),
                    'coxed_four': ("JM4+", "Junior Men's Coxed Four", "1797cb82-0ced-4fb3-9acd-4a6646f824cb"),
                    'four': ("JM4-", "Junior Men's Four", "8661c474-9506-473a-9784-d00ecfa2167f"),
                    'eight': ("JM8+", "Junior Men's Eight", "bed56642-164b-4ea5-93ce-1fcadd0ef017")
                },
                'u23': {
                    'single': ("BM1x", "U23 Men's Single Sculls", "6b7c0445-c065-49cd-90b3-4c56317e4346"),
                    'double': ("BM2x", "U23 Men's Double Sculls", "74864b35-be40-431a-a48c-f1b605a6759e"),
                    'quad': ("BM4x", "U23 Men's Quadruple Sculls", "be5a6d89-d55b-4316-9366-7ed1ef0f307b"),
                    'pair': ("BM2-", "U23 Men's Pair", "3830f652-0963-4d75-a081-a4ef4553a10c"),
                    'coxed_four': ("BM4+", "U23 Men's Coxed Four", "e784fbb3-b45f-45d5-be67-0699cdba4553"),
                    'four': ("BM4-", "U23 Men's Four", "2fc7bcd7-3ccc-49eb-ab18-50ab09ae501d"),
                    'eight': ("BM8+", "U23 Men's Eight", "2a2a5aa7-8592-4684-99ce-4f02679061e6"),
                    'lw_single': (
                        "BLM1x", "U23 Lightweight Men's Single Sculls", "2a2a5aa7-8592-4684-99ce-4f02679061e6"),
                    'lw_double': (
                        "BLM2x", "U23 Lightweight Men's Double Sculls", "cc8022e2-3ee1-463a-bddf-aa115d68e704"),
                    'lw_quad': (
                        "BLM4x", "U23 Lightweight Men's Quadruple Sculls", "8df04fba-76af-40c4-ac38-73f377bfb258"),
                    'lw_pair': ("BLM2-", "U23 Lightweight Men's Pair", "3830f652-0963-4d75-a081-a4ef4553a10c"),
                },
                'elite': {
                    'single': ("M1x", "Men's Single Sculls", "3f0d0a7d-92a6-4c53-90f5-7c8f01972964"),
                    'double': ("M2x", "Men's Double Sculls", "9cb5d841-32a6-4388-8a30-6d7f51bdfdbc"),
                    'quad': ("M4x", "Men's Quadruple Sculls", "d4140064-67dc-47d0-957a-a42e90bf8433"),
                    'pair': ("M2-", "Men's Pair", "02316e75-fdf2-4660-af40-48dda1867e1f"),
                    'four': ("M4-", "Men's Four", "27d5614e-6530-49d1-acf5-da132b71a45d"),
                    'eight': ("M8+", "Men's Eight", "532b264c-47e1-4d35-928a-85d9733928d0"),
                    'lw_single': ("LM1x", "Lightweight Men's Single Sculls", "182d0aae-7e73-4900-ae8e-f1aafbe5c48a"),
                    'lw_double': ("LM2x", "Lightweight Men's Double Sculls", "4458faa3-d55b-495f-8018-51250f82e5ba"),
                    'lw_quad': ("LM4x", "Lightweight Men's Quadruple Sculls", "ba397032-a5c6-466a-ba1b-23e521237048"),
                    'lw_pair': ("LM2-", "Lightweight Men's Pair", "46564a8c-b4b3-4bb3-bbf4-cd96bb4ee4f5"),
                },
                'para': {
                    '1': ("PR1 M1x", "PR1 Men's Single Sculls", "d7365b40-b544-480b-aa99-b0ffad7a13e9"),
                    '2': ("PR2 M1x", "PR2 Men's Single Sculls", "731e3206-45c5-4596-b48e-5a21b1675918"),
                    '3': ("PR3 M2-", "PR3 Men's Pair", "15e1ef74-79c6-4227-96f1-86d793efbf5b"),
                }
            },
            'women': {
                'u19': {
                    'single': ("JW1x", "Junior Women's Single Sculls", "683b227a-51fd-4c09-a6a0-460ca3711b08"),
                    'double': ("JW2x", "Junior Women's Double Sculls", "26af8860-5146-422d-bb10-3eef8b28d883"),
                    'quad': ("JW4x", "Junior Women's Quadruple Sculls", "6edc9d42-edda-4f32-9469-91d54e0eaeb1"),
                    'pair': ("JW2-", "Junior Women's Pair", "4bbcf35e-b424-4000-9f4f-048f2edce263"),
                    'coxed_four': ("JW4+", "Junior Women's Coxed Four", "5911da97-fe4a-42ce-8431-7f3aa9cdfb20"),
                    'four': ("JW4-", "Junior Women's Four", "ff2aa19c-db81-4c8e-a523-b7a3ef50ce31"),
                    'eight': ("JW8+", "Junior Women's Eight", "d97e6295-e55a-4235-abc3-e986dead5137"),
                },
                'u23': {
                    'single': ("BW1x", "U23 Women's Single Sculls", "e22e0fe4-66bc-42f1-82f4-162bb1cc384b"),
                    'double': ("BW2x", "U23 Women's Double Sculls", "5a308214-114a-4b49-b985-fdc6e0b7b319"),
                    'quad': ("BW4x", "U23 Women's Quadruple Sculls", "ba9814b9-0243-445c-979d-189da9ad8407"),
                    'pair': ("BW2-", "U23 Women's Pair", "3304a580-b3b1-4b4e-b51f-e4f63d2e5853"),
                    'coxed_four': ("BW4+", "U23 Women's Coxed Four", "e972ad8f-b73e-41ef-a30b-dee4a391a734"),
                    'four': ("BW4-", "U23 Women's Four", "c5810370-41ac-45c2-aeff-01dcb1d6d078"),
                    'eight': ("BW8+", "U23 Women's Eight", "871abbbb-2413-45b5-b83c-03619c6f0ee5"),
                    'lw_single': (
                        "BLW1x", "U23 Lightweight Women's Single Sculls", "60cecbef-919c-47c0-9f16-0a8edd105d82"),
                    'lw_double': (
                        "BLW2x", "U23 Lightweight Women's Double Sculls", "aee5f04d-6939-4173-a829-999dfb77f159"),
                    'lw_quad': (
                        "BLW4x", "U23 Lightweight Women's Quadruple Sculls", "c18403e0-53cf-4b6b-a1f1-60ad2b220c5a"),
                    'lw_pair': ("BLW2-", "U23 Lightweight Women's Pair", "0f218eeb-6f65-48c7-941c-97f0901cb8cd"),
                },
                'elite': {
                    'single': ("W1x", "Women's Single Sculls", "8a078108-6741-4ad1-ab5a-704194538227"),
                    'double': ("W2x", "Women's Double Sculls", "16946db9-72f2-4375-a797-a26fd485dd26"),
                    'quad': ("W4x", "Women's Quadruple Sculls", "7249e207-5c76-4c58-9c7c-b7e2a4c74b50"),
                    'pair': ("W2-", "Women's Pair", "5e834702-14c3-4a85-b38d-9afb419f5294"),
                    'four': ("W4-", "Women's Four", "2b2bfa01-a902-4ad8-be87-4527c9ba7e6d"),
                    'eight': ("W8+", "Women's Eight", "b834436f-4378-4825-aaa0-f9905959abdb"),
                    'lw_single': ("LW1x", "Lightweight Women's Single Sculls", "43b5679c-8f9e-45f9-8111-fca22bdc02cc"),
                    'lw_double': ("LW2x", "Lightweight Women's Double Sculls", "61be8c32-b56d-4cac-bf56-46246fb1c349"),
                    'lw_quad': ("LW4x", "Lightweight Women's Quadruple Sculls", "c47c6b93-dd0d-4645-9545-2ee853db284c"),
                    'lw_pair': ("LW2-", "Lightweight Women's Pair", "7b8c2fd0-0286-4bd3-a5c3-0f17a4bc3bd0"),
                },
                'para': {
                    '1': ("PR1 W1x", "PR1 Women's Single Sculls", "b61f430f-d4ee-48e0-a632-95b9194ccb16"),
                    '2': ("PR2 W1x", "PR2 Women's Single Sculls", "dd434535-b9eb-4b38-9ecf-f3fd6dc9cadf"),
                    '3': ("PR3 W2-", "PR3 Women's Pair", "15e1ef74-79c6-4227-96f1-86d793efbf5b"),
                }
            },
            'mixed': {
                'double_2': ("PR2 Mix2x", "PR2 Mixed Double Sculls", "843310e2-f28c-41a7-90e9-b6f8c289b154"),
                'double_3': ("PR3 Mix2x", "PR3 Mixed Double Sculls", "e23cc24f-4a62-4de3-ab99-50a40c8416f0"),
                'four': ("PR3 Mix4+", "PR3 Mixed Coxed Four", "b6bcf280-a57c-4a6a-96fb-91e6a1355002"),
            },
            "all": {
                "all": ("Alle", "Alle")
            },
        }
    }], sort_keys=False)


@app.route('/get_teams_filter_options', methods=['GET'])
@jwt_required()
def get_teams_filter_options():
    """
        Delivers the filter options for the teams page.
        """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "competition_categories": [{"id": entity.id, "display_name": entity.name} for entity in
                                   session.execute(select(model.Competition_Category)).scalars()],
        "nations": {entity.country_code: entity.name for entity in
                    session.execute(select(model.Country)).scalars()}
    }], sort_keys=False)


@app.route('/get_medals_filter_options', methods=['GET'])
@jwt_required()
def get_medals_filter_options():
    """
    Delivers the filter options for the medals page.
    """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    statement = select(model.Competition_Category, model.Competition_Type.abbreviation
                       ).join(model.Competition_Category.competition_type)

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "competition_categories": [{
            "id": entity[0].id,
            "display_name": entity[1],
        } for entity in session.execute(statement).fetchall()],
        "medal_types": [
            {"display_name": "Gesamt", "id": "0"},
            {"display_name": "Olympisch", "id": "1"},
            {"display_name": "Nicht-Olympisch", "id": "2"}
        ],
        "nations": {entity.country_code: entity.name for entity in
                    session.execute(select(model.Country)).scalars()},
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
    }], sort_keys=False)


@app.route('/get_medals', methods=['POST'])
@jwt_required()
def get_medals():
    data = request.json["data"]
    start, end = data["years"][0], data["years"][1]
    start_date = func.to_timestamp(func.concat(start, "-01-01 00:00:00"), 'YYYY-MM-DD HH24:MI:SS')
    end_date = func.to_timestamp(func.concat(end, "-12-31 23:59:59"), 'YYYY-MM-DD HH24:MI:SS')
    nations = [nation[:3] for nation in data["nations"]]
    comp_ids = data["competition_categories"]

    session = Scoped_Session()

    nation_ids = session.query(model.Country.id).filter(model.Country.country_code.in_(nations)).all()
    nation_ids = [nation_id[0] for nation_id in nation_ids]

    race_boats = (
        session.query(model.Race_Boat)
        .join(model.Race)
        .join(model.Event)
        .join(model.Boat_Class)
        .filter(
            model.Race_Boat.country_id.in_(nation_ids),
            model.Race.date >= start_date,
            model.Race.date <= end_date
        )
        .all()
    )

    medal_data, total_result_counter = [], 0
    for nation in nations:
        total, gold, silver, bronze, final_a, final_b = 0, 0, 0, 0, 0, 0
        for race_boat in race_boats:
            if race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 1 \
                    and race_boat.country.country_code == nation:
                total_result_counter += 1
                final_a += 1
                if race_boat.rank == 1:
                    gold += 1
                    total += 1
                elif race_boat.rank == 2:
                    silver += 1
                    total += 1
                elif race_boat.rank == 3:
                    bronze += 1
                    total += 1
            elif race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 2 \
                    and race_boat.country.country_code == nation:
                total_result_counter += 1
                final_b += 1

        medal_data.append({
            "nation": nation,
            "total": total,
            "gold": gold,
            "silver": silver,
            "bronze": bronze,
            "final_a": final_a,
            "final_b": final_b
        })

    medal_data.sort(key=lambda x: x['gold'], reverse=True)
    for i, obj in enumerate(medal_data):
        obj['rank'] = i + 1

    return json.dumps({
        "results": total_result_counter,
        "start_date": start,
        "end_date": end,
        "data": medal_data
    })


@app.route('/get_report_filter_options', methods=['GET'])
@jwt_required()
def get_report_filter_options():
    """
    Delivers the filter options for the report page.
    Note: preserving the order of the key's important for rendering in the frontend.
    """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    statement = select(model.Competition_Category, model.Competition_Type.abbreviation
                       ).join(model.Competition_Category.competition_type)

    competition_categories = [{
        "id": entity[0].id,
        "display_name": entity[1],
    } for entity in session.execute(statement).fetchall()]

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
        "competition_categories": competition_categories,
        "runs": globals.RACE_PHASE_SUBTYPE_BY_RACE_PHASE,
        "ranks": [1, 2, 3, 4, 5, 6]
    }], sort_keys=False)


@app.route('/calendar/<int:year>', methods=['GET'])
@jwt_required()
def get_calendar(year: int):
    """
    TODO: If the db is complete there will be many competitions; perhaps we need some kind of pagination here.
    This route delivers calendar data for all competitions.
    @return: key (relevant for frontend), title, dates for competition
    """
    result = []
    session = Scoped_Session()
    iterator = session.execute(select(model.Competition).where(model.Competition.year == year)).scalars()
    for competition in iterator:
        # only include competitions that have a start and end date
        if competition.start_date and competition.end_date:
            comp_cat_id = session.query(model.Competition).filter(model.Competition.id == competition.id).one()
            comp_type = set(session.query(model.Competition_Category).filter(
                model.Competition_Category.id == comp_cat_id.id
            ).all())

            result.append({
                "key": competition.id,
                # "competition_type": comp_type.pop().name if comp_type else None,
                "comp_type": competition.competition_category.name,
                "customData": {
                    "title": competition.name
                },
                "dates": {
                    "start": datetime.datetime.strptime(str(competition.start_date),
                                                        '%Y-%m-%d %H:%M:%S').strftime('%a, %d %b %Y %H:%M:%S GMT'),
                    "end": datetime.datetime.strptime(str(competition.end_date),
                                                      '%Y-%m-%d %H:%M:%S').strftime('%a, %d %b %Y %H:%M:%S GMT')
                }
            })
    return result
