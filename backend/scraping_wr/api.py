import logging
from typing import Union, Optional, Iterator
from datetime import datetime, date
import json as jsn

import re


# from tqdm import tqdm
tqdm = lambda i : i

from . import utils_wr as ut_wr
from . import pdf_race_data as pdf_race_data
from . import pdf_result as pdf_result_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

########################################################################################################################
# GLOBALS:
WR_BASE_URL = "https://world-rowing-api.soticcloud.net/stats/api/"
# ENDPOINTS FOR THE BASE-URL
WR_ENDPOINT_RACE = "race/"
WR_ENDPOINT_EVENT = "event/"
WR_ENDPOINT_COMPETITION = "competition/"
WR_ENDPOINT_COMPETITION_CATEGORIES = "competitionCategory/"
WR_ENDPOINT_COMPETITION_TYPES = "competitionType/"
WR_ENDPOINT_STATS = "statistic/"
WR_ENDPOINT_VENUE = "venue/"
WR_ENDPOINT_BOATCLASSES = "boatClass/"
WR_ENDPOINT_COUNTIRES = "country/"
WR_INCLUDE_EVERYTHING = "?include=" + ",".join(
    [
        "competitionType",
        "competitionType.competitionCategory",
        "venue",
        "venue.country",
        "events.gender",
        "events.boatClass",
        "events.pdfUrls",
        "events.races",
        "events.races.raceStatus",
        "events.races.racePhase",
        "events.races.raceBoats.boat",
        "events.races.raceBoats.invalidMarkResultCode",
        "events.races.raceBoats.country",
        "events.races.raceBoats.raceBoatAthletes.person",
        "events.races.raceBoats.raceBoatAthletes.person.country",
        "events.races.raceBoats.raceBoatIntermediates.distance",
        "events.races.pdfUrls.orisCode",
        "pdfUrls.orisCode"
    ]
)

# SELECTION FILTERS
OLYMPIC_BOATCLASSES = [
    "M1x",
    "LM2x",
    "W1x",
    "M2x",
    "M2-",
    "LW2x",
    "M4-",
    "W1x",
    "W2x",
    "W2-",
    "M4x",
    "M8+",
    "W4x",
    "W8+",
    "W4-",
]


# what is this?
## This constant provides...
## - list of race-phase-names (the keys fo the dict)
## - ids to the respective phases (e.g. RACE_PHASES['Test Race']['id'])
## - processes rsc_code_snippets, that occured in the past, processes by the function 'process_rsc_code' in this file
# todo: should we make the keys short forms? Or ar least all lower?
# todo: needed: FA must be mapped to "potentially" to FNL0001000
## the short version is found in the pdfs, top right
RACE_PHASES = {
    'Test Race': {
        'id': '92b34c4e-af58-4e91-8f4a-22c09984a006',
        'rsc_code_snippets': []
    },
    'RoundOf16': {
        'id': 'ef6a596d-7de4-4646-81a7-7dbeaf515cfd',
        'rsc_code_snippets': ['8FNL000100']
    },
    'Heat': {
        'id': 'cd3d5ca1-5aed-4146-b39b-a192ae6533f1',
        'rsc_code_snippets': ['HEAT000100', 'HEAT0001RR', 'HEAT000200', 'HEAT000300', 'HEAT000400', 'HEAT000500',
                              'HEAT000600', 'HEAT000700', 'HEAT000800', 'RND2000100', 'RND2000200', 'RND2000300',
                              'RND2000400', 'RND2000500', 'RND2000600', 'RND3000100', 'RND3000200', 'RND3000300',
                              'RND3000400', 'RND3000500', 'RND3000600']
    },
    'Final': {
        'id': 'e0fc3320-cd66-43af-a5b5-97afd55b2971',
        'rsc_code_snippets': ['FNL000100', 'FNL0001RR', 'FNL000200', 'FNL000300', 'FNL000400', 'FNL000500', 'FNL000600',
                              'FNL000700', 'FNL000800']
    },
    'Preliminary': {
        'id': '92b34c4e-af58-4e91-8f4a-22c09984a006',
        'rsc_code_snippets': ['PREL000100', 'PREL000200']
    },
    'Seeding': {
        'id': '6c281206-2291-41bc-b9cd-5ecd82b1638c',
        'rsc_code_snippets': ['RND1000100', 'SEED000100', 'SEED000200', 'SEED000300']
    },
    'Repechage': {
        'id': '0959f5e8-f85a-40fb-93ab-b6c477f6aade',
        'rsc_code_snippets': ['REP000100', 'REP0001RR', 'REP000200', 'REP000300', 'REP000400', 'REP000500', 'REP000600',
                              'REP000700', 'REP000800', 'REP005100', 'REP005200', 'REP005300', 'REP005400',
                              'SFNL000100']
    },
    'Semifinal': {
        'id': 'e6693585-d2cf-464c-9f8e-b2e531b26400',
        'rsc_code_snippets': ['SFNL000100', 'SFNL000200', 'SFNL000300', 'SFNL000400', 'SFNL000500', 'SFNL000600',
                              'SFNL000700', 'SFNL000800']
    },
    'Quarterfinal': {
        'id': 'a0b6ffd8-92b8-427b-a667-ac2ff640031a',
        'rsc_code_snippets': ['QFNL000100', 'QFNL000200', 'QFNL000300', 'QFNL000400', 'QFNL000500', 'QFNL000600',
                              'QFNL000700', 'QFNL000800']
    },
}

RACE_STATUSES = {
    'Unofficial': 'd168a581-658d-40ad-8537-e3a07470b20a',
    'Cancelled': '3e5b4b12-4610-4f75-8b23-5f878e8ffc54',
    'Scheduled': 'f89cc288-076b-4bb6-9776-96e66820e1b8',
    'Official': '182f6f15-8e78-41c3-95b3-8b006af2c6a1'
}

########################################################################################################################
def extract_race_phase_details(rsc_code: str, display_name: str):  # -> dict:
    """
    Extracts detail information about a race.
    ! Both values to the keys can be None.
    @param rsc_code: The associated rsc-code of a race
    @param display_name: the associated display name of a race
    @return: dict, containing the sub
    """

    _, coarse_phase = ut_wr.process_rsc_code(rsc_code)
    _, subtype = ut_wr.extract_race_phase_from_rsc(coarse_phase)

    if 'SFNL' in coarse_phase:
        subtype, number = ut_wr.process_semifinal_display_name(display_name)
        if subtype == '' or subtype == 'r':
            # edge-case; no proper display-name was entered in world-rowing-data
            subtype = 'sfnl'

        ret = {'subtype': subtype, 'number': number}
    else:
        ret = {'subtype': None, 'number': subtype}

    return ret


def save(data: dict, fn: str):
    with open(fn, 'w', encoding='ascii') as file:
        jsn.dump(data, file)


def load(fn: str) -> dict:
    with open(fn, 'r', encoding='ascii') as file:
        j = jsn.load(file)

    return j


def _extract(nested: iter, successor_filter: str = None) -> list:
    """
    Helper function extracting nested iterators
    @param nested: iter: lazy generator. Used in the loop
    @return: list: unpacked version of nested.
    """
    _l = []
    if successor_filter:
        for item in list(nested):
            _l.extend([_item[successor_filter] for _item in item])
    else:
        for item in list(nested):
            if isinstance(item, dict):
                _l.append(item)
            else:
                _l.extend(item)

    return _l


def select_pdf_(pdfUrls: list, title: str) -> Union[dict, None]:
    for pdf_info in pdfUrls:
        try:
            if pdf_info['title'].lower() == title.lower():
                return pdf_info
        except Exception as e: 
            logger.error(e)
            return None 

    return None # or raise error?


def get_by_competition_id_(comp_ids: Union[str, list[str]], verbose: bool = False, parse_pdf=False) -> dict:
    """
    Stripped down version of get_by_competition_id()
    """
    comp_id = comp_ids if isinstance(comp_ids, str) else comp_ids[0]

    comp_data = ut_wr.load_json(WR_BASE_URL + WR_ENDPOINT_COMPETITION + comp_id + WR_INCLUDE_EVERYTHING)

    if parse_pdf:
        # PDF parsing/matching was implemented elsewhere. See Scraper.
        raise NotImplementedError

    return comp_data


def get_by_competition_id(comp_ids: Union[str, list[str]], keys_of_interest: Union[str, list[str]], verbose: bool = False) -> dict:
    """
    Get the entities of interest (passed by keys_of_interest) for the id's passed.
    @param verbose: if or if not verbose
    @param comp_ids: Union[str, list[str]]: a singe OR a list of competition id's
    @param keys_of_interest: Union[str, list[str]]: a string = 'everything' OR a list of keys you are interested in.
        Possible keys are denoted blow
    @return: dict[str]: list[dict]
    """

    allowed_keys = {
        'events', 'races', 'pdf',
        'raceBoats', 'raceBoatAthletes',
        'raceBoatIntermediates',
        'venue', 'boatClass'
    }

    if isinstance(keys_of_interest, str) and keys_of_interest == 'everything':
        keys_of_interest = list(allowed_keys)
    else:
        logger.error("The passed string for 'keys_of_interest' does not match the string 'everything'. Check fct-call.")

    if not set(keys_of_interest).issubset(allowed_keys):
        logger.error(f"Some of the passed keys are not allowed: {set(keys_of_interest) - allowed_keys}")
        raise KeyError()

    if isinstance(comp_ids, str):
        comp_ids = [comp_ids]

    if verbose:
        _len = len(comp_ids)

    ret_val = {koi: [] for koi in keys_of_interest}

    for i, _id in tqdm(enumerate(comp_ids), desc='Aggregating WR endpoint data'):
        everything = ut_wr.load_json(WR_BASE_URL + WR_ENDPOINT_COMPETITION + _id + WR_INCLUDE_EVERYTHING)
        for koi in keys_of_interest:
            ret_val[koi].extend(
                _extract(
                    ut_wr.get_all(everything, koi)
                )
            )

    # if race and pdfs is in the koi's, we want to aggregate the data from the pdf
    if 'races' in keys_of_interest and 'pdf' in keys_of_interest:
        races = []
        for race in tqdm(ret_val['races'], desc='Aggregating PDF data'):
            race['pdfUrls'] = extract_pdf_urls(race['pdfUrls'])
            races.append(race)
            results_data = pdf_result_data.extract_data_from_pdf_urls(race['pdfUrls']['results'])[0]
            race_data = pdf_race_data.extract_data_from_pdf_url(race['pdfUrls']['race_data'])[0]
            race['results_data'] = results_data
            race['race_data'] = race_data
            races.append(race)

        ret_val['races'] = races

    return ret_val


def get_competition_heads(years: Optional[Union[list, int]] = None, single_fetch: bool = False) -> Iterator[dict]:
    """
    Returns: An Iterator of Competition (dict) not containing any deeper data fields like e.g. Events.

    Param years: Selects years.
        - Can be a list of years.
        - Can be an int.
        - Can be None -> All years from 1900 to 5 years in the future.

    Param single_fetch: Request the selection of years in a single API call.
    """

    # TODO: The following logic should be in a separate function
    if years == None:
        # current year -1 to + 5; to make sure we get planned comps as well
        present_year = date.today().year
        selected_years = list( range(1900, present_year+5+1) )
    elif isinstance(years, int):
        selected_years = [years]
    elif isinstance(years, list) or isinstance(years, tuple):
        selected_years = list(years)
    else:
        raise TypeError("Param years has to be of type: None, list or int")

    if single_fetch:
        year_batches = [ selected_years ]
    else:
        year_batches = [ [year] for year in selected_years ]

    for year_batch in year_batches:
        query_string = ut_wr.build_filter_string({'year': year_batch})
        competitions = ut_wr.load_json(WR_BASE_URL + WR_ENDPOINT_COMPETITION + query_string)
        for competition in competitions:
            yield competition


def get_competition_ids(*args, **kwargs) -> list[str]:
    competition_heads_iterator = get_competition_heads(*args, **kwargs)
    return [ c['id'] for c in competition_heads_iterator ]


def extract_pdf_urls(race_urls: list[dict]) -> dict:
    """
    Fetches URLs to pdf files on https://d3fpn4c9813ycf.cloudfront.net/
    @param race_urls: child-dict of the races result
    @return: dict of urls for 'race_data' and 'results'
    """

    ret_val = {
        'results': [],
        'race_data': []
    }

    for race_url in race_urls:
        if race_url['title'] == 'Results':
            ret_val['results'].append(race_url.get('url', None))
        elif race_url['title'] == 'Race Data':
            ret_val['race_data'].append(race_url.get('url', None))

    # sanity checking
    if len(ret_val['race_data']) != len(ret_val['results']):
        # todo: do we have to do smth about that?
        logger.warning("\nUnequal number of pdf-urls for race data and results data")

    return ret_val


def get_competition_categories(kwargs: dict = {}):
    ret_val = ut_wr.load_json(url=f'{WR_BASE_URL}{WR_ENDPOINT_COMPETITION_CATEGORIES}', **kwargs)
    return ret_val


def get_competition_types(kwargs: dict = {}):
    ret_val = ut_wr.load_json(url=f'{WR_BASE_URL}{WR_ENDPOINT_COMPETITION_TYPES}', **kwargs)
    return ret_val


def get_countries(kwargs: dict = {}):
    ret_val = ut_wr.load_json(url=f'{WR_BASE_URL}{WR_ENDPOINT_COUNTIRES}', **kwargs)
    return ret_val


def get_statistics(kwargs: dict = {}):
    ret_val = ut_wr.load_json(url=f'{WR_BASE_URL}{WR_ENDPOINT_STATS}', **kwargs)
    return ret_val


def get_world_best_times() -> list[dict]:
    """
        Use the endpoints '/stats', get the filtered world-best-times and get the urls to the jsons.
        Extract the relevant information from the results.

        TODO: Only return the boat-class and the competitor (race_boat_id)
    """
    fs = ut_wr.build_filter_string(filter_params={'category': 'WBT'})
    wbts = ut_wr.load_json(WR_BASE_URL + WR_ENDPOINT_STATS + fs)
    ret = []
    for wbt in wbts:
        if 'Overall' in wbt['description']:
            _wbts = ut_wr.load_json(wbt['url'], content_field='BestTimes')
            for val in _wbts:
                ret.append({
                    'race_boat_id': val['Competitor']['Id'],
                    'boat_class': val['BoatClass'],
                    'result_time': val['Competitor']['ResultTime']
                })
                #athletes = "; ".join([v['Person']['FullName'] for v in val['Competitor']['Athletes']])
                # todo: remove me, once the data structure has been integrated
                # the code below represents the needed information
                #ret.append({
                #    'boat_class': val['BoatClass'],
                #    'event_name': val['Competition']['Name'],
                #    'race_type': val['Race']['Name'],
                #    'competition_id': val['Competition']['Id'],
                #    'race_id': val['Race']['Id'],
                #    'date': val['DateOfBT'],
                #    'venue': val['Venue']['Name'],
                #    'names': athletes,
                #    'time': val['Competitor']['ResultTime']
                #})

    return ret


def get_boatclasses(kwargs: dict = {}):
    ret_val = ut_wr.load_json(url=f'{WR_BASE_URL}{WR_ENDPOINT_BOATCLASSES}', **kwargs)
    return ret_val
