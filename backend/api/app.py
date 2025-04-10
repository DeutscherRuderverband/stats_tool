import os
import datetime
import json
from secrets import token_hex
from collections import OrderedDict
from statistics import stdev, median, mean

import numpy as np
from typing import List

from flask import Flask, request, abort, jsonify, Response
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, JWTManager

from sqlalchemy import select, func, and_, or_, distinct
from sqlalchemy.orm import joinedload

from . import auth
from . import mocks  # todo: remove me
from . import globals
from . import race as r
from model import model
from common.rowing import propulsion_in_meters_per_stroke


# disable auth by uncommenting the following line
#jwt_required = lambda: (lambda x: x) # disable auth

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

    # Fetch year range
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()

    # Fetch primary and secondary competition categories separately
    competition_categories = r.fetch_competition_categories(session, globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
    secondary_competition_categories = r.fetch_competition_categories(session, globals.SECONDARY_CMP_TYPE_ABBREVIATIONS)

    nations = {entity.country_code: entity.name for entity in session.execute(select(model.Country)).scalars()}

    return {"years": (min_year, max_year),
            "competition_categories": competition_categories,
            "secondary_competition_categories": secondary_competition_categories,
            "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
            "nations": dict(sorted(nations.items(), key=lambda x: x[0])),
            "runs": globals.RACE_PHASE_FILTER_OPTIONS,
            "ranks": [1, 2, 3, 4, 5, 6]
            }


@app.route('/race_analysis_filter_results', methods=['POST'])
@jwt_required()
def get_race_analysis_filter_results() -> dict:
    """
    WHEN?
    This endpoint is used, when the user is on the page for the 'Rennstrukturanalyse' and selected filter for
        - year
        - competition_type
    of interest.
    OR 
    This endpoint is used, when the user clicks on a competition in the calendar subpage.
    BOTH USAGES ARE VALID!
    @param filter_dict: example for filter_dict {  "year": 2008, "competition_type": f5da0ad6-afea-436c-a396-19de6497762f , [OPTIONAL] "competition_id": 42 }
    @return: nested dict/json: structure containing competitions, their events and their races respectively.
    See https://github.com/N10100010/DRV_project/blob/api-design/doc/backend-api.md#user-auswahl-jahr-einzeln-und-wettkampfklasse-zb-olympics for mock of return value.

    """
    #from datetime import datetime
    import logging

    year = request.json["data"].get('year', None)
    competition_type = request.json["data"].get('competition_type', None) 
    competition_id = request.json["data"].get('competition_id', None) 

    logging.info(f"Year: {year}, comp cat: {competition_type}, comp id: {competition_id}")

    session = Scoped_Session()

    if competition_id: 
        statement = (
            select(
                model.Competition
            )
            .where(
                model.Competition.id == competition_id
            )
        )
    else: 
        statement = (
            select(
                model.Competition
            )
            .join(model.Competition.competition_type)
            .join(model.Competition_Type.competition_category)
            .where(
                and_(
                    model.Competition_Type.abbreviation == competition_type,
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
            model.Intermediate_Time.is_outlier == False, 
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

#Comment
@app.route('/get_race_boat_groups', methods=['POST'])
@jwt_required()
def get_race_boat_groups():
    """
    WHEN? THIS FUNCTION IS CALLED WHEN THE USER SELECTED RACEGROUPS WITH THE MULTIPLE FILTER IN RENNSTRUKTURANALYSE
    Gets the mandatory information to display a race-analysis of several race-boat-groups (Rennstrukturanalyse-Multiple).
    @return: the information of the race groups
    """
    session = Scoped_Session()

    boat_class = request.json["data"]["boat_class"]
    groups_filter = request.json["data"]["groups"]

    groups = []
    for index, data in enumerate(groups_filter):
    
        min_Year = data["start_year"]
        max_Year = data["end_year"]
        country = data["country"]
        competitions = data["events"]
        ranks = data["placements"]
        phases_filter = data["phases"]
        phases, phases_subtype = r.separatePhaseTypes(phases_filter)
        athletes_id = data.get("athletes")

        statement = (
        select(model.Race_Boat)
        .distinct()
        .join(model.Race_Boat.country)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.boat_class)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .join(model.Race_Boat.athletes)
        .where(
            model.Country.country_code == country,
            model.Race_Boat.rank.in_(ranks),
            model.Boat_Class.abbreviation == boat_class,
            model.Competition.year >= min_Year,
            model.Competition.year <= max_Year,
            model.Competition_Type.abbreviation.in_(competitions),
            or_(
                and_(
                    model.Race.phase_type != "final",
                    model.Race.phase_type.in_(phases)
                ),
                and_(
                    model.Race.phase_type == 'final',
                    model.Race.phase_number.in_(phases_subtype)
                )
            )
        ))

        if athletes_id:
            statement = statement.where(
                model.Association_Race_Boat_Athlete.athlete_id == athletes_id,
            )
    
        race_boats: List[model.Race_Boat]
        race_boats = session.execute(statement).scalars().all()

        boats_formatted = []
        relevant_competitions = set()
        total_boats = 0

        for boat in race_boats:
            total_boats+= 1
            relevant_competitions.add(boat.race.event.competition.competition_type.abbreviation)

            # intermediate data
            times = r.getIntermediateTimes(boat)
            calculated_times = r.calculateIntermediateTimes(times)
            strokes =  r.strokes_for_intermediate_steps(boat.race_data)
            for key, stroke,  in strokes.items():
                if calculated_times.get(key) is not None:
                    calculated_times[key]["stroke [1/min]"] = stroke

            # race_data aka gps data
            race_data_result = {}
            sorted_race_data = sorted(boat.race_data, key=lambda x: x.distance_meter)
            race_data: model.Race_Data
            for race_data in sorted_race_data:
                propulsion = propulsion_in_meters_per_stroke(race_data.stroke, race_data.speed_meter_per_sec)
                race_data_result[str(race_data.distance_meter)] = {
                    "speed [m/s]": race_data.speed_meter_per_sec,
                    "stroke [1/min]": race_data.stroke,
                    "propulsion [m/stroke]": propulsion
            }
                
            #athletes
            athletes = r.getAthletes(boat.athletes)

            boat_formatted = {
                "id": boat.id,
                "name": boat.name,
                "time": boat.result_time_ms,
                "rank": boat.rank,
                "phase": boat.race.phase_type,
                "phase_sub": r.getPhaseType(boat.race.phase_type, boat.race.phase_subtype, boat.race.phase_number),
                "year": boat.race.event.competition.year,
                "event": boat.race.event.competition.competition_type.abbreviation,
                "city": boat.race.event.competition.venue.city,
                "athletes": athletes,
                "intermediates": calculated_times,
                "race_data": race_data_result
            }

            boats_formatted.append(boat_formatted)

        #Get intermediate values of all boats
        stats = {}
        for boat in boats_formatted:
            for distance, values in boat["intermediates"].items():
                if distance not in stats:
                    stats[distance] = {}
                for key, figure in values.items():
                    if key not in stats[distance]:
                        stats[distance][key] = []
                    stats[distance][key].append(figure)

        #Calculate means 
        summary = {}
        for distance, values in stats.items():
            summary[distance] = {}
            for key, figures in values.items():
                if key != "is_outlier":
                    summary[distance][key] = {}
                    mean, lower, upper =  r.calculateConfidenceIntervall(figures)
                    summary[distance][key]["mean"] = mean
                    summary[distance][key]["lower_bound"] = lower
                    summary[distance][key]["upper_bound"] = upper

        #Get race_data/gps values of all boats 
        stats_gps = {}
        for boat in boats_formatted:
            for distance, values in boat["race_data"].items():
                if distance not in stats_gps:
                    stats_gps[distance] = {}
                for key, figure in values.items():
                    if key not in stats_gps[distance]:
                        stats_gps[distance][key] = []
                    stats_gps[distance][key].append(figure)

        #Calculate means for gps data
        summary_gps = {}
        for distance, values in stats_gps.items():
            summary_gps[distance] = {}
            for key, figures in values.items():
                if key != "is_outlier":
                    summary_gps[distance][key] = {}
                    mean, lower, upper =  r.calculateConfidenceIntervall(figures)
                    summary_gps[distance][key]["mean"] = mean
                    summary_gps[distance][key]["lower_bound"] = lower
                    summary_gps[distance][key]["upper_bound"] = upper

        #Get Pacing Profile
        pacing_profile = "-"
        if summary != {}:
            pacing_profile =  r.getPacingProfile(summary[500]["pace [millis]"]["mean"], summary[1000]["pace [millis]"]["mean"], summary[1500]["pace [millis]"]["mean"], summary[2000]["pace [millis]"]["mean"])

        group = f"Gruppe {index + 1}"
        groups.append({"name": group, "stats": summary, "stats_race_data": summary_gps, "pacing_profile": pacing_profile, "count": total_boats, "min_year": min_Year, "max_year": max_Year,"events": list(relevant_competitions), "phases": phases_filter, "ranks": ranks, "country": country, "race_boats": boats_formatted})

    #World Best Times
    best_oz_time = r.getOzBestTime(boat_class, datetime.datetime.today().year)
    world_best_time_ms = r.getWorldBestTime(boat_class, session)

    return {"boat_class": boat_class, "world_best_time": world_best_time_ms, "oz_best_time": best_oz_time, "groups": groups}
    


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

    #World Best Times
    best_oz_time =  r.getOzBestTime(race.event.boat_class.abbreviation, datetime.datetime.today().year)
    world_best_time_ms = r.getWorldBestTime(race.event.boat_class.abbreviation, session)

    best_of_last_4_years_ms =  r.result_time_best_of_year_interval(
        session=session,
        boat_class_id=race.event.boat_class.id,
        year_start=datetime.date.today().year - 4
    )

    result = {
        "race_id": race.id,
        "display_name": race.name,
        "start_date": str(race.date),
        "venue": f"{venue.site}/{venue.city}, {venue.country.name}",
        "boat_class": race.event.boat_class.abbreviation,  # long name?
        "result_time_world_best": world_best_time_ms,
        "result_time_best_of_current_olympia_cycle": best_of_last_4_years_ms,  # int in ms
        "result_time_world_best_before_olympia_cycle": best_oz_time,
        "progression_code": race.progression,
        "pdf_urls": {
            "result": race.pdf_url_results,
            "race_data": race.pdf_url_race_data
        },
        "race_boats": []
    }

    sorted_race_boat_data = sorted(race.race_boats, key=lambda x: x.rank if x.rank is not None else float('inf'))
    race_boat: model.Race_Boat
    for race_boat in sorted_race_boat_data:
        rb_result = {
            "name": race_boat.name,  # e.g. DEU2
            "lane": race_boat.lane,
            "rank": race_boat.rank,
            "athletes": OrderedDict(),
            "intermediates": OrderedDict(),
            "race_data": OrderedDict(),
        }
        result['race_boats'].append(rb_result)

        # athletes
        rb_result["athletes"] = r.getAthletes(race_boat.athletes)

        # race_data aka gps data
        sorted_race_data = sorted(race_boat.race_data, key=lambda x: x.distance_meter)
        race_data: model.Race_Data
        for race_data in sorted_race_data:
            propulsion = propulsion_in_meters_per_stroke(race_data.stroke, race_data.speed_meter_per_sec)
            rb_result['race_data'][str(race_data.distance_meter)] = {
                "speed [m/s]": race_data.speed_meter_per_sec,
                "stroke [1/min]": race_data.stroke,
                "propulsion [m/stroke]": propulsion or 0
            }

        # intermediates
        intermediates_figures =  r.compute_intermediates_figures(race.race_boats)
        strokes_for_intermediates =  r.strokes_for_intermediate_steps(race_boat.race_data)
        total_time = race_boat.result_time_ms
        for distance_meter, figures in intermediates_figures[race_boat.id].items(): # ❌ TODO: iterate over figure matrix (see intermediates_figures) to provide dicts for all 'cells'
            intermediate: model.Intermediate_Time = figures["__intermediate"]
            intermediate_dict = {
                "rank": None,
                "time [millis]": None,
                "pace [millis]": None,
                "speed [m/s]": None,
                "rel_speed [%]": None,
                "rel_diff_to_avg_speed [%]": None,
                "stroke [1/min]": None,
                "is_outlier": None
            }
            rb_result['intermediates'][str(distance_meter)] = intermediate_dict

            result_time = figures.get('result_time')
            intermediate_dict["time [millis]"] = result_time

            is_valid_mark = isinstance(result_time, int)
            if is_valid_mark:
                rel_speed = figures.get('speed')/(2000/ total_time * 1000 )
                intermediate_dict.update({
                    "rank": intermediate.rank if intermediate else None,
                    "pace [millis]": figures.get('pace'),
                    "speed [m/s]": figures.get('speed'),
                    "rel_speed [%]": rel_speed,
                    "rel_diff_to_avg_speed [%]": figures.get('rel_diff_to_avg_speed'),
                    "stroke [1/min]": strokes_for_intermediates.get(distance_meter),
                    "is_outlier": intermediate.is_outlier if intermediate else None
                })

        # pacing profile
        rb_result['pacing_profile'] = r.getPacingProfile(intermediates_figures[race_boat.id][500]['pace'], intermediates_figures[race_boat.id][1000]['pace'], intermediates_figures[race_boat.id][1500]['pace'], intermediates_figures[race_boat.id][2000]['pace'])

    return Response(json.dumps(result, sort_keys=False), content_type='application/json')


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
            model.Race.id.label("race_id")
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
        race_id = row
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
                    model.Intermediate_Time.race_boat_id == race_boat.id, 
                    model.Intermediate_Time.is_outlier == False
                ).all()
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

    race_results, race_ids, athlete_boat_classes, best_time_boat_class, nation, race_phase = [], [], set(), "", "", ""
    total, gold, silver, bronze, final_a, final_b = 0, 0, 0, 0, 0, 0

    for i, race_boat in enumerate(race_boats):
        race_ids.append(race_boat.race_id)
        boat = race_boat.race
        phase = boat.phase_type
        phase_num = boat.phase_number

        race_phase = r.getPhaseType(phase, boat.phase_subtype, phase_num)

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

        race_results.append({
            "race_id": race_boat.race_id,
            "rank": race_boat.rank,
            "race_phase": race_phase,
            "result_time": race_boat.result_time_ms,
            "name": race_boat.race.event.competition.name,
            "venue": f'{race_boat.race.event.competition.venue.city}, {race_boat.race.event.competition.venue.country.name}',
            "boat_class": race_boat.race.event.boat_class.abbreviation,
            "start_time": str((race_boat.race.date).strftime("%Y-%m-%d %H:%M")),
            "competition_category": race_boat.race.event.competition.competition_type.competition_category.name
        })
        nation = race_boat.country.country_code

    races = session.query(model.Race).order_by(model.Race.date.desc()).filter(model.Race.id.in_(race_ids)).all()

    gender, athlete_disciplines = set(), set()
    for i, race in enumerate(races):
        gender.add(race.event.gender.name)
        boat_class_name = race.event.boat_class.abbreviation
        athlete_boat_classes.add(boat_class_name)

        # check disciplines
        if any(ath.endswith("x") for ath in athlete_boat_classes):
            athlete_disciplines.add("Skull")
        elif not any(ath.endswith("x") for ath in athlete_boat_classes):
            athlete_disciplines.add("Riemen")

    sorted_race_results = sorted(race_results, key=lambda item: item['start_time'], reverse=True)

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
        "race_list": sorted_race_results,
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

@app.route('/get_all_races_list', methods=['GET'])
@jwt_required()
def get_all_races_list():
    session = Scoped_Session()

    statement = (
        select(model.Association_Race_Boat_Athlete)
        .join(model.Association_Race_Boat_Athlete.race_boat)
        .join(model.Race_Boat.race)
        .join(model.Race.event)
        .join(model.Event.competition)
        .join(model.Competition.competition_type)
        .where(
            model.Race_Boat.country_id == 12,
            model.Competition_Type.abbreviation.in_(["WCH", "WCp 1", "WCp 2", "WCp 3", "U23WCH", "JWCH", "EJCH", "OG", "ECH"]),
            model.Race.phase_type == "final"
        )
    )

    results = session.execute(statement).scalars()
    races = []
    for result in results:
        row = [result.race_boat.country.country_code, result.athlete.last_name__, result.athlete.first_name__, result.athlete.birthdate, result.race_boat.race.event.gender.name, result.race_boat.race.event.competition.name, result.race_boat.race.date, result.race_boat.race.event.competition.venue.city, result.race_boat.race.event.boat_class.abbreviation, result.race_boat.race.phase_type, result.race_boat.race.phase_number, result.race_boat.rank, result.race_boat.result_time_ms]
        #print(f'Rank: {result.race_boat.rank}, Time: {result.race_boat.result_time_ms}, Country: {result.race_boat.country.country_code}, First name: {result.athlete.first_name__}, Last name: {result.athlete.last_name__}, Geburtsdatum: {result.athlete.birthdate}, Geschlecht: {result.race_boat.race.event.gender.name}, Event: {result.race_boat.race.event.name}, Date: {result.race_boat.race.date}, Bootsklasse: {result.race_boat.race.event.boat_class.abbreviation}, Stadt: {result.race_boat.race.event.competition.venue.city}, Lauf: {result.race_boat.race.phase_type}, Phase_number: {result.race_boat.race.phase_number}')
        races.append(row)

    return races


@app.route('/get_teams_filter_options', methods=['GET'])
@jwt_required()
def get_teams_filter_options():
    """
        Delivers the filter options for the teams page.
        """
    session = Scoped_Session()
    min_year, max_year = session.query(func.min(model.Competition.year), func.max(model.Competition.year)).first()
    competition_categories = r.fetch_competition_categories(session, globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
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

    competition_categories = r.fetch_competition_categories(session, globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
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

   # Fetch primary and secondary competition categories separately
    competition_categories = r.fetch_competition_categories(session, globals.RELEVANT_CMP_TYPE_ABBREVATIONS)
    secondary_competition_categories = r.fetch_competition_categories(session, globals.SECONDARY_CMP_TYPE_ABBREVIATIONS)

    return json.dumps([{
        "years": [{"start_year": min_year}, {"end_year": max_year}],
        "boat_classes": globals.BOATCLASSES_BY_GENDER_AGE_WEIGHT,
        "competition_categories": competition_categories,
        "secondary_competition_categories": secondary_competition_categories,
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


@app.teardown_appcontext
def shutdown_session(exception=None):
    ''' Enable Flask to automatically remove database sessions at the
    end of the request or when the application shuts down.
    Ref: http://flask.pocoo.org/docs/patterns/sqlalchemy/
    Ref: https://stackoverflow.com/a/45719168
    '''
    Scoped_Session.remove()