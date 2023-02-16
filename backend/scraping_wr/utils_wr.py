from tenacity import retry, wait_exponential, stop_after_attempt
from datetime import datetime
from typing import Union

import re
import requests
import pandas as pd
import numpy as np


import logging
logger = logging.getLogger(__name__)

############################################################
## ABBREVIATIONS
#WR = WorldRowing


WR_FILTER_MAPPING = {
    'year': 'Year',
    'category': 'Category'
    # todo: extend me...
}

STR_NUMBERS_0_10 = ''.join([str(n) for n in range(0, 10)])


def procedure_init():
    """
    TODO:
     -
    @return:
    """

    pass


def procedure_update():
    """
    TODO:
     - check, for races and events, what the biggest dates are
     - query (big, combined query string for endpoint) data from the endpoint with respective filters for
        races-dates and event-dates
     - build connection to the database? should we do that here?

    @return:
    """

    pass


def get_all(data: Union[dict, list], key: str):
    """
    Gets every value of occurrences of the key and yields it.
    @param data: dict|list
    @param key: some string like 'events', 'races', ...
    @return: generator
    """
    sub_iter = []
    if isinstance(data, dict):
        if key in data:
            yield data[key]
        # we ensured the type of data is dict
        #  values() is an internal function of the dict class
        sub_iter = data.values()
    if isinstance(data, list):
        sub_iter = data

    # iterate over all values
    for x in sub_iter:
        for y in get_all(x, key):
            yield y


@retry(wait=wait_exponential(max=5), stop=stop_after_attempt(5))
def load_json(url: str, content_field='data', params=None, timeout=20., **kwargs):
    """
    Loads any json from any URL.
    The function will be retried, if the endpoint might not be reachable atm.
    ------------
    :param url: str - A url to an endpoint, that might contain a filter string
    :param params: not used
    :param timeout: should stay at default (most of the time)
    :param kwargs: mostly not used
    :return: dict
    """
    res = None
    try:
        res = requests.get(url, params=params, timeout=timeout, **kwargs)
        res.raise_for_status()
    except (Exception, ) as e:
        logger.error(f"Error appeared during get(). \n\tStatuscode: {res.status_code}\n\tURL: {url}")
        return {}

    if res.text and res.status_code != 404:
        return res.json()[content_field]
    else:
        return {}


def stringify_params(val: Union[int, float, str, list]) -> str:
    """
    Stringifies a value
    ---------
    :param val: The parameter that will be stringified.
    :return: Stringified val
    """
    if isinstance(val, (str, int, float, np.int64)):
        return str(val)
    elif isinstance(val, list):
        return '||'.join(map(str, val))
    else:
        logger.error(f"Passed value of unknown type: {type(val)}. Allowed types: [str, int, np.int64, float, list]")


def build_filter_string(filter_params: dict) -> str:
    """
    -
    :param filter_params: dict - containing the parameters that are supposed to be filtered.
        example: {'year': 2010} OR {'year': [2010, 2012]}
        The passed value in the dict is allowed to be a list.

    :returns: returns the string containing the parameters for filtering the resulting json.
    """
    ret = '?'
    splitter = '&'
    schema = 'filter[{PARAM}]={VALUE}'

    if not set(filter_params.keys()).issubset(set(WR_FILTER_MAPPING.keys())):
        # the keys for filters start with capital letters. For ease of use, this is taken care of by the function.
        logger.error(f"A key of the passed filter is not allowed. Allowed filters: {list(WR_FILTER_MAPPING.keys())}")

    param_pairs = []
    for k, v in filter_params.items():
        param_pair = schema.format(PARAM=WR_FILTER_MAPPING[k], VALUE=stringify_params(val=v))
        param_pairs.append(param_pair)

    query_string = ret + "&".join(param_pairs)
    return query_string


def process_rsc_code(code: str) -> tuple[str, str]:
    """
    Processes the RscCode of a race to extract the phase (Lauf) of the race.
    @param code: str - total rcs code
    @return: str - processed rsc code
    # todo: same here as the todo in function filter_by_race_phase. Add filter parameteres to the database
    """
    processed = code.split('---')
    boat_class = processed[0].strip('--')
    phase = processed[-1].strip('--')
    phase = "".join(re.split("[^0-9a-zA-Z*]", phase))
    phase = phase.lstrip(STR_NUMBERS_0_10)

    return boat_class, phase


def extract_race_phase_from_rsc(processed: str) -> (str, int):
    """
    This extraction allows to identify a race, within a competition, given the class of a race.
    CAUTION: Expects the second value from the function process-rsc-code.
    @param processed: The processed phase of a race, from its rsc-code
    @return: Extracted race phase, with its respective stage (phase: str, stage: int)
    """
    lower = processed.lower()

    if lower[0:4] in ('qfnl', 'sfnl', 'heat', 'prel', 'seed'):
        start, end = 4, 4
    elif lower[0:3] in ('fnl', 'rep'):
        start, end = 3, 4
    elif lower[0:3] in ('rnd'):
        start, end = 3, 1
    else:
        logger.warning(f"Encountered unknown phase in rsc-code. Seen value: {lower}")
        return processed, 0

    # remove unwanted parts of the string
    processed = processed[0: start + end]

    # return only parts that indicate the phase
    return processed[0: start], int(processed[-1])


def process_semifinal_display_name(name: str) -> tuple[str, int]:
    """
    Processes the display-name of a race to extract the type of it.
    ! This is to cover an edge-case to cover semifinals. this means we know that it is semifinals display-name
    @param name: The unprocessed display-name of a race
    @return: The processed short-version of a display-name
    """
    lower = name.lower()
    if 'semifinal' in lower:
        last_occurrence = lower.rindex('semifinal')
        #  9 = len(semifinal)
        lower = lower[last_occurrence + 9: len(lower)]

    org_lower = lower.replace('0', '').lstrip('s')
    number = re.findall(r'\d+', org_lower)
    number = number[0] if len(number) > 0 else None

    # strip-fct's can handle None value - does nothing
    lower = org_lower.lstrip('sf').lstrip('f').rstrip('r').rstrip(number).replace(' ', '').lstrip('s')

    return lower, number

def extract_competition_ids(values: dict) -> list[str]:
    """
    -
    @param values: dict - holding information about competitions
    @return: list[str] - list holding the competition ids
    """
    return [comp['id'] for comp in values]

########################################################################################################################
# NICK - OLD
########################################################################################################################


def preprocess_json_to_dataframe(json: dict) -> pd.DataFrame:
    """
    return: dataframe with lowered column names from WR json
    """
    assert ("data" in json.keys())
    df = pd.DataFrame.from_dict(json['data'])
    df.columns = string_list_lower(df.columns.to_list())
    return df


def get_date_columns(str_list: list) -> list:
    """
    return: list of columns that contain 'date' in their name
    """
    lower = [s.lower() for s in str_list]
    filtered = list(filter(lambda x: "date" in x, lower))

    if len(filtered) > 0:
        return [str_list[lower.index(k)] for k in filtered]
    else:
        return []


def get_binary_columns(df: pd.DataFrame) -> list:
    """
    return: list of columns with potentially binary data
    """
    is_binary = df.isin([0., 1., 0, 1, np.nan]).any()
    return [is_binary.index[i] for i, val in enumerate(is_binary) if val]


def string_list_lower(l: list) -> list:
    """
    Applies the lower-func to the columns of a dataframe.
    """
    return [col_name.lower() for col_name in l]


def alter_dataframe_column_types(df: pd.DataFrame, type_mapping: dict[str, str]) -> pd.DataFrame:
    """
    return: DataFrame with altered types, according to `type_mapping`
    """

    def _fix_date_values(values: list[str]) -> list[str]:
        """
        replace not-allowed values for date-parsing
        """
        return [val if val not in ['0000-00-00 00:00:00', None, ''] else '1900-01-01 00:00:00' for val in values]

    # TODO: adjust me if we use python >= 3.10
    #  switch/case would be the call here. That is only present in python >= 3.10
    #  UPGRADE TO python 3.10
    assert (set(type_mapping.keys()).issubset(set(df.columns.to_list())))

    try:
        for k, v in type_mapping.items():
            if v == "str":
                df[k] = df[k].astype(str)
            elif v == "int":
                df[k] = df[k].astype(int)
            elif v == "float":
                df[k] = df[k].astype(float)
            elif v == "bool":
                df[k] = df[k].astype(bool)
            elif v == "date":
                if np.mean(df[k].isna()) < .35:
                    # there are date columns that contain less than 24% data and these dates contain unknown timezones.
                    # Can we get the information if we need that data?
                    df[k] = [datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                             for val in _fix_date_values(df[k].values)]
                else:
                    logger.info(f"Skipping type-mapping: {k}:{v}. Less than 35% data present.")
            else:
                logger.warning(f"Received unknown type-mapping for {k}: {v}")
    except (ValueError, ) as e:
        raise e

    return df


def merge(dfs, **kwargs):
    left = dfs[0]
    n = len(dfs[1:])

    def iterate(val):
        if isinstance(val, tuple):
            return iter(val)
        else:
            return (val for _ in range(n))

    iter_kwargs = {k: iterate(val) for k, val in kwargs.items()}

    for right in dfs[1:]:
        kws = {
            k: next(val) for k, val in iter_kwargs.items()
        }
        left = pd.merge(left, right, **kws)

    return left
