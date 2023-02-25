import os
from secrets import token_hex
import datetime
import json
from itertools import groupby
from collections import OrderedDict
from statistics import stdev, median, mean
import numpy as np

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
from .race import result_time_best_of_year_interval, compute_intermediates_figures, strokes_for_intermediate_steps
from common.rowing import propulsion_in_meters_per_stroke
from . import mocks  # todo: remove me
from . import globals

# app is the main controller for the Flask-Server and will start the app in the main function 
app = Flask(__name__, template_folder=None)
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=60)

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


@jwt.invalid_token_loader
def invalid_token_handler(reason):
    http_status_code = 401 # Code 401 is important here for robust login handling in the frontend
    return {"msg": str(reason)}, http_status_code


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


@app.route('/race_analysis_filter_options/', methods=['GET', 'POST'])
@jwt_required()
def get_race_analysis_filter_options():
    """
    This endpoint give the filter options data for the race data page.
    """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    statement = select(model.Competition_Type.additional_id_, model.Competition_Type.abbreviation)
    competition_categories = [{
        "id": v[0],
        "display_name": v[1],
    } for v in session.execute(statement).fetchall()]
    sorted_categories = sorted(competition_categories, key=lambda x: x['display_name'])

    return {"years": (min_year, max_year), "competition_categories": sorted_categories}


@app.route('/race_analysis_filter_results', methods=['POST'])
@jwt_required()
def get_race_analysis_filter_results() -> dict:
    """
    WHEN?
    This endpoint is used, when the user is on the page for the 'Rennstrukturanalyse' and selected filter for
        - year
        - competition_type
    of interest.
    @param filter_dict: example for filter_dict {  "year": 2008, "competition_type": f5da0ad6-afea-436c-a396-19de6497762f  }
    @return: nested dict/json: structure containing competitions, their events and their races respectively.
    See https://github.com/N10100010/DRV_project/blob/api-design/doc/backend-api.md#user-auswahl-jahr-einzeln-und-wettkampfklasse-zb-olympics for mock of return value.

    """
    from datetime import datetime
    import logging

    year = request.json["data"].get('year')
    competition_type_id = request.json["data"].get('competition_type') 

    logging.debug(f"Year: {year}, comp cat: {competition_type_id}")

    session = Scoped_Session()

    statement = (
        select(
            model.Competition
        )
        .join(model.Competition.competition_type)
        .join(model.Competition_Type.competition_category)
        .where(
            and_(
                model.Competition_Type.additional_id_ == competition_type_id,
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
                    "sub_phase": _race.phase_number if _race.phase_number else _race.phase_subtype,
                    "race_nr": int(_race.race_nr__)
                }
                races.append(race)

            event['races'] = sorted(races, key=lambda d: d["race_nr"])
            events.append(event)

        comp['events'] = events
        competitions.append(comp)

    return competitions


@app.route('/matrix', methods=['POST'])
@jwt_required()
def get_matrix() -> dict:
    """
    COMMENT KAY WINKERT: Events begrenzen auf JWCh, WCh, Ech, WCp1, WCp2, WCp3, OG
    """
    filter_key_mapping = {
        'gender': model.Event.gender_id,  # list
        'boat_class': model.Boat_Class.id,  # list
        'interval': model.Competition.year,  # tuple
        'competition_type': model.Competition_Type.additional_id_,  # list
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
            model.Boat_Class.additional_id_.label('id')
        )
        .join(model.Intermediate_Time.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.boat_class)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .join(model.Competition_Type.competition_category)
        .where(
            model.Intermediate_Time.distance_meter == 2000,
            # model.Intermediate_Time.is_outlier == False, 
            model.Intermediate_Time.result_time_ms != 0
        )
        .group_by(
            model.Boat_Class.id
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

    intermediates_figures = compute_intermediates_figures(race.race_boats, force_500m_grid=True)

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
            "athletes": OrderedDict(),
            "intermediates": OrderedDict(),
            "race_data": OrderedDict()
        }
        result['race_boats'].append(rb_result)

        # athletes
        sorted_athletes = sorted(race_boat.athletes, key=lambda x: (x.boat_position != 'b', x.boat_position))
        athlete_assoc: model.Association_Race_Boat_Athlete
        for idx, athlete_assoc in enumerate(sorted_athletes):
            athlete: model.Athlete = athlete_assoc.athlete
            rb_result['athletes'][idx] = {
                "id": athlete.id,
                "first_name": athlete.first_name__,
                "last_name": athlete.last_name__,
                "full_name": athlete.name,
                "boat_position": athlete_assoc.boat_position
            }

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
        strokes_for_intermediates = strokes_for_intermediate_steps(race_boat.race_data)
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
                "rel_diff_to_avg_speed [%]": figures.get('rel_diff_to_avg_speed'),
                "stroke [1/min]": strokes_for_intermediates.get(intermediate.distance_meter)
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


@app.route('/get_report_boat_class', methods=['POST'])
@jwt_required()
def get_report_boat_class():
    """
    Delivers the report results for a single boat class.
    """
    filter_data = request.json["data"]
    filter_keys = ["interval", "competition_type", "boat_class", "race_phase_type",
                   "race_phase_subtype" "placement"]
    interval, competition_types, boat_class, runs, ranks = [filter_data.get(key) for key in filter_keys]
    start_year, end_year = interval[0], interval[1]
    start_date = datetime.datetime(start_year, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(end_year, 12, 31, 23, 59, 59)

    session = Scoped_Session()

    statement = (
        select(
            model.Race.id.label("race_id"),
            model.Competition.id.label("competition_id")
        )
        .join(model.Race.event)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .join(model.Competition_Type.competition_category)
        .where(and_(
            model.Race.date >= start_date,
            model.Race.date <= end_date,
            model.Event.boat_class_id == model.Boat_Class.id,
            model.Boat_Class.additional_id_ == boat_class,
            model.Competition_Type.additional_id_.in_(competition_types)
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
        comp_categories.add(race.event.competition.competition_type.competition_category.name)

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
    Gives athlete data and race list for specific athlete.
    """
    session = Scoped_Session()
    athlete = session.query(model.Athlete).filter_by(id=int(athlete_id)).first()
    athlete_race_boats = [race_boat.race_boat_id for race_boat in athlete.race_boats]

    race_boats = session.query(model.Race_Boat).filter(model.Race_Boat.id.in_(athlete_race_boats)).all()

    race_results, race_ids, athlete_boat_classes, best_time_boat_class, nation, race_phase = {}, [], set(), "", "", ""
    total, gold, silver, bronze, final_a, final_b = 0, 0, 0, 0, 0, 0

    for i, race_boat in enumerate(race_boats):
        race_ids.append(race_boat.race_id)
        boat = race_boat.race
        phase = boat.phase_type
        phase_num = boat.phase_number
        phase_subtype = boat.phase_subtype if boat.phase_subtype else ""
        phase_string = globals.RACE_PHASE_MAPPING.get(phase + phase_subtype + str(phase_num))
        race_phase = phase_string if phase_string else phase + str(phase_num)
        if phase == 'final' and phase_num == 1:
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
        elif phase == 'final' and phase_num == 2:
            final_b += 1

        race_results[i] = {
            "race_id": race_boat.race_id,
            "rank": race_boat.rank,
            "race_phase": race_phase,
            "result_time": race_boat.result_time_ms
        }
        nation = race_boat.country.country_code

    races = session.query(model.Race).order_by(model.Race.date.desc()).filter(model.Race.id.in_(race_ids)).all()

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

        comp_type = race.event.competition.competition_type.competition_category.name
        race_results[i]["name"] = comp.name
        race_results[i]["venue"] = f'{comp.venue.city}, {comp.venue.country.name}'
        race_results[i]["boat_class"] = boat_class_name
        race_results[i]["start_time"] = str((race.date).strftime("%Y-%m-%d %H:%M"))
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
    nations = {entity.country_code: entity.name for entity in session.execute(select(model.Country)).scalars()}

    return json.dumps([{
        "birth_years": [
            {"start_year": min(birth_years)},
            {"end_year": max(birth_years)}],
        "nations": dict(sorted(nations.items(), key=lambda x: x[0])),
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT
    }], sort_keys=False)


@app.route('/get_teams_filter_options', methods=['GET'])
@jwt_required()
def get_teams_filter_options():
    """
        Delivers the filter options for the teams page.
        """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()
    statement = select(model.Competition_Type.additional_id_, model.Competition_Type.abbreviation)
    competition_categories = [{
        "id": v[0],
        "display_name": v[1],
    } for v in session.execute(statement).fetchall()]
    nations = {entity.country_code: entity.name for entity in session.execute(select(model.Country)).scalars()}

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "competition_categories": sorted(competition_categories, key=lambda x: x['display_name']),
        "nations": dict(sorted(nations.items(), key=lambda x: x[0]))
    }], sort_keys=False)


@app.route('/get_teams', methods=['POST'])
@jwt_required()
def get_teams():
    """
    This endpoint serves the teams data for a given nation and further filter criteria.
    """
    data = request.json["data"]
    start_date = datetime.datetime(data["interval"][0], 1, 1, 0, 0, 0)
    end_date = datetime.datetime(data["interval"][1], 12, 31, 23, 59, 59)
    nation = data["nation"][:3] if data["nation"] else None
    comp_types = data["competition_categories"]

    session = Scoped_Session()

    # get all race boats for given nation
    race_boats = session.query(model.Race_Boat) \
        .join(model.Country, model.Race_Boat.country_id == model.Country.id) \
        .join(model.Race, model.Race_Boat.race_id == model.Race.id) \
        .join(model.Race.event)\
        .join(model.Event.competition)\
        .join(model.Competition.competition_type)\
        .join(model.Competition_Type.competition_category)\
        .filter(model.Country.country_code == str(nation)) \
        .filter(model.Race.date >= start_date) \
        .filter(model.Race.date <= end_date) \
        .filter(model.Competition_Type.additional_id_.in_(comp_types)) \
        .all()

    athletes = set()
    for race_boat in race_boats:
        boat_class = race_boat.race.event.boat_class.additional_id_
        athlete_assoc: model.Association_Race_Boat_Athlete
        for idx, athlete_assoc in enumerate(race_boat.athletes):
            athlete: model.Athlete = athlete_assoc.athlete
            athletes.add((athlete.name, athlete.id, boat_class))

    num_of_results = len(athletes)
    result = {}
    for entry in athletes:
        name, id, key = entry
        if key not in result:
            result[key] = [{"name": name, "id": id}]
        else:
            result[key].append({"name": name, "id": id})

    return {
        "interval": [data["interval"][0], data["interval"][1]],
        "nation": data["nation"],
        "race_boats": str(len(race_boats)),
        "results": num_of_results,
        "athletes": result,
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT
    }

@app.route('/get_medals_filter_options', methods=['GET'])
@jwt_required()
def get_medals_filter_options():
    """
    Delivers the filter options for the medals page.
    """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    statement = select(model.Competition_Type.additional_id_, model.Competition_Type.abbreviation)
    competition_categories = [{
        "id": v[0],
        "display_name": v[1],
    } for v in session.execute(statement).fetchall()]
    nations = {entity.country_code: entity.name for entity in session.execute(select(model.Country)).scalars()}

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "competition_categories": sorted(competition_categories, key=lambda x: x['display_name']),
        "medal_types": [
            {"display_name": "Gesamt", "id": "0"},
            {"display_name": "Olympisch", "id": "1"},
            {"display_name": "Nicht-Olympisch", "id": "2"}
        ],
        "nations": dict(sorted(nations.items(), key=lambda x: x[0])),
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
    }], sort_keys=False)


@app.route('/get_medals', methods=['POST'])
@jwt_required()
def get_medals():
    data = request.json["data"]
    start, end = data["years"][0], data["years"][1]
    start_date = datetime.datetime(start, 1, 1, 0, 0, 0)
    end_date = datetime.datetime(end, 12, 31, 23, 59, 59)
    nations = {nation[:3] for nation in data["nations"]}
    comp_types = data["competition_type"]

    session = Scoped_Session()

    nation_ids = [country.id for country in
                  session.query(model.Country.id).filter(model.Country.country_code.in_(nations)).all()]

    race_boats = (
        session.query(model.Race_Boat)
        .join(model.Race)
        .join(model.Event)
        .join(model.Boat_Class)
        .join(model.Competition)
        .join(model.Competition_Type)
        .filter(
            model.Race_Boat.country_id.in_(nation_ids),
            model.Race.date >= start_date,
            model.Race.date <= end_date,
            model.Competition_Type.additional_id_.in_(comp_types)
        )
        .options(
            joinedload(model.Race_Boat.country),
            joinedload(model.Race_Boat.race),
        )
        .all()
    )

    medal_data, total_result_counter, comp_types = {}, 0, set()
    for race_boat in race_boats:
        comp_types.add(race_boat.race.event.competition.competition_type.abbreviation)
        if race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 1 and race_boat.country.country_code in nations:
            total_result_counter += 1
            nation = race_boat.country.country_code
            if nation not in medal_data:
                medal_data[nation] = {"total": 0, "gold": 0, "silver": 0, "bronze": 0, "four_to_six": 0, "final_a": 0, "final_b": 0}
            medal_data[nation]["final_a"] += 1
            if race_boat.rank == 1:
                medal_data[nation]["gold"] += 1
                medal_data[nation]["total"] += 1
            elif race_boat.rank == 2:
                medal_data[nation]["silver"] += 1
                medal_data[nation]["total"] += 1
            elif race_boat.rank == 3:
                medal_data[nation]["bronze"] += 1
                medal_data[nation]["total"] += 1
            elif 3 < race_boat.rank <= 6:
                medal_data[nation]["four_to_six"] += 1
        elif race_boat.race.phase_type == 'final' and race_boat.race.phase_number == 2 and race_boat.country.country_code in nations:
            nation = race_boat.country.country_code
            if nation not in medal_data:
                medal_data[nation] = {"total": 0, "gold": 0, "silver": 0, "bronze": 0, "four_to_six": 0, "final_a": 0, "final_b": 0}
            medal_data[nation]["final_b"] += 1

    medal_data = [{"nation": nation, **medal_data[nation]} for nation in medal_data]
    medal_data.sort(key=lambda x: x['gold'], reverse=True)

    for i in range(len(medal_data)):
        medal_data[i]['rank'] = i + 1

    return json.dumps({
        "results": total_result_counter,
        "start_date": start,
        "end_date": end,
        "data": medal_data,
        "comp_types": ", ".join(comp_types)
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

    statement = select(model.Competition_Type.additional_id_, model.Competition_Type.abbreviation).where(
        model.Competition_Type.abbreviation.in_(globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
    )
    competition_categories = [{
        "id": v[0],
        "display_name": v[1],
    } for v in session.execute(statement).fetchall()]
    sorted_categories = sorted(competition_categories, key=lambda x: x['display_name'])

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
        "competition_categories": sorted_categories,
        "runs": globals.RACE_PHASE_SUBTYPE_BY_RACE_PHASE,
        "ranks": [1, 2, 3, 4, 5, 6]
    }], sort_keys=False)


@app.route('/calendar/<int:year>', methods=['GET'])
@jwt_required()
def get_calendar(year: int):
    """
    This route delivers calendar data for all competitions.
    @return: key (relevant for frontend), title, dates for competition

    COMMENT KAY WINKERT: Auf relevante Termine begrenzen (EM, WC I-III, WM, OG)
    """
    result = []
    session = Scoped_Session()
    iterator = session.execute(
        select(model.Competition)
        .join(model.Competition.competition_type)
        .where(
            and_(
                model.Competition.year == year,
                model.Competition_Type.abbreviation.in_(globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
            )
        )
    ).scalars()
    for competition in iterator:
        # only include competitions that have a start and end date
        if competition.start_date and competition.end_date:
            result.append({
                "key": competition.id,
                "comp_type": competition.competition_type.competition_category.name,
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
