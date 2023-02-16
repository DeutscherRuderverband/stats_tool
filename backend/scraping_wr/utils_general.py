from datetime import datetime
from typing import Union
import json
import pandas as pd
import numpy as np

JSON_INDENT_SIZE = 4

import logging
logger = logging.getLogger(__name__)


def write_to_json(data: Union[list,dict], filename: str) -> None:
    """ Takes a list and writes to .json file. """
    with open(filename, "w", encoding='ascii') as fp:
        json.dump(data, fp, indent=2, sort_keys=True)


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
