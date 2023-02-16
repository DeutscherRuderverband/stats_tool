"""
####################################################################################################
This module extracts results data from World Rowing Result pdf files.

Example file:
https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/JWCH_2014/JWCH_2014_ROWWSCULL1--J---------SFNL000100--_C73X4443.pdf

Basic stats:
* Extraction time per file: approx. 1.0 - 1.8s
####################################################################################################
"""

import pandas as pd
import itertools
import camelot
import re
from typing import Union
import json

from .utils_general import write_to_json
from .utils_pdf import (clean, clean_df, get_string_loc, handle_table_partitions,
                       clean_str, print_stats)
import logging

logger = logging.getLogger(__name__)
logging.getLogger('camelot').setLevel(logging.WARNING)

# constants
DISTS = ["250", "500", "750", "1000", "1500", "2000"]  # includes basic 500m interval and 250m para intervals
SPECIAL_VALUES = ["dna", "DNA", "dns", "DNS", "dnf", "DNF", "BUW", "-"]  # special codes that imply missing values
COMPETITION_LIMIT = 1000
START_YEAR = 2011
END_YEAR = 2021
EVERY_NTH_DOCUMENT = 25


def get_athletes(df: pd.DataFrame, rows: list, i: int) -> list:
    """
    Handles extraction of athlete names.
    -----------------------
    Parameters:
    * df:       dataframe
    * rows:     list of country row indices as start points for names of given country
    * i:        index of current country w.r.t. countries in given pdf
    -----------------------
    Returns:    list of strings containing athlete names
    """
    # rows: starts at row of current country, ends at row of following country
    start_row = rows[i]
    end_row = rows[i + 1] if (i + 1 < len(rows)) else df.shape[0]
    raw_athlete_data = df.iloc[start_row:end_row, 0:df.shape[1] - 1].dropna().values.reshape(-1)
    filtered_athletes = clean_str(raw_athlete_data, style="name")
    return clean_str(filtered_athletes, style='name')


def get_times(df: pd.DataFrame, row: int, cols: list) -> dict:
    """
    Handles extraction of intermediate times
    ----------------------
    Parameters:
    * df:   dataframe
    * row:  row index of current country
    """
    # Check intermediate distances that are present in df
    distance_data = ''.join(str(el) for el in df.values)
    distances = [dist for dist in DISTS if dist in distance_data]

    # get raw time values from dataframe row and find all time patterns in row for current country/row
    raw_t_values = df.iloc[row:row+1, cols[0]-1:].values
    time_regex = r"(?:\d{1,2}:)?\d{2}\.\d{2}|" + "|".join(SPECIAL_VALUES)
    [extracted_time_values] = [re.findall(time_regex, str(raw_t_val)) for raw_t_val in raw_t_values]

    # if time values are missing
    if len(extracted_time_values) != len(distances):
        # when there are special values, e.g. DNF, DNA
        special_vals_included = set(extracted_time_values).intersection(set(SPECIAL_VALUES))
        if special_vals_included:
            extracted_time_values = [next(iter(special_vals_included or []), None)] * len(distances)

    # check interval and place time values according to distance
    dist_diffs = [int(j) - int(i) for i, j in zip(distances[:-1], distances[1:])]
    intermediate_interval = max(set(dist_diffs), key=dist_diffs.count)
    times = {}
    for key, time in enumerate(extracted_time_values):
        dict_key = (key + 1) * intermediate_interval
        times[dict_key] = time
    return times


def get_intermediate_ranks(df: pd.DataFrame, row: int) -> list:
    times_row = df.iloc[row-1:row + 1, :].values.tolist()
    ranks_regex = r"\((\d)\)"
    ranks = re.findall(ranks_regex, str(times_row))
    return [int(rank) for rank in ranks if rank]


def get_country_code(df: pd.DataFrame, row: int) -> str:
    """
    Handles extraction of country code.
    ----------------
    Parameters:
    * df:   dataframe
    * row:  row index of country
    * cols: list of column indices containing country codes
    ---------------
    Returns: string representing the country code
    """
    country_df = df.iloc[row:row + 1, 0:df.shape[1] - 1]
    country_data = country_df.values.reshape(-1)
    reg = r"(?<![A-Z])[A-Z]{3}(?![A-Z])(?!\s)[1-9]?"
    country = list(itertools.chain(*[re.findall(reg, str(x)) for x in country_data]))
    return next(iter(clean_str(country, style="country")), None)


def get_lane(df: pd.DataFrame, row: int, i: int) -> Union[int, None]:
    lane_data = df.iloc[row:row + 1, 0:df.shape[1] - 1].values.reshape(-1)
    lane_string = ''.join(str(el) for el in lane_data)
    # get first two numbers in country row
    lane_regex = r"^\d{1,2}$"
    nums = [int(re.findall(lane_regex, str(el))[0]) for el in lane_string if el.isdigit()][:2]
    # lane is either the number that is not the rank or it is equal to the rank
    if len(nums) == 1:
        return nums[0]
    elif len(nums) == 2:
        num1, num2 = nums
        if num1 == i + 1 or num1 == 0:
            return num2
        elif num2 == i + 1:
            return num1
        return None


def check_extracted_data(data: dict) -> dict:
    # restrict number of athletes to most frequent number of athletes
    lens = [len(v["athletes"]) for v in data.values() if "athletes" in v]
    max_len = max(set(lens), key=lens.count)
    for el in data.values():
        if "athletes" in el:
            el["athletes"] = el["athletes"][:max_len]
    # restrict number of intermediate ranks to n - 1 ranks where n is the number of distances
    inter_ranks_len = [len(v["times"]) for v in data.values() if "times" in v]
    max_inter_len = max(set(inter_ranks_len), key=lens.count)-1
    for el in data.values():
        if "inter_ranks" in el:
            el["inter_ranks"] = el["inter_ranks"][:max_inter_len]
    return data


def extract_data_from_pdf_urls(urls: list) -> tuple[dict, list]:
    """
    This function extracts relevant data from the result data pdfs.
    --------------
    Parameters:
    * urls: list of urls to pdfs
    --------------
    Returns: list with extracted data
    """

    final_data, data, failed_requests, errors, empty_files = {}, [], [], 0, 0

    for url in urls:
        boat_data, tables = {}, []
        try:
            tables = camelot.read_pdf(url, flavor="stream", pages="all", column_tol=2)
        except NotImplementedError:
            logger.error(f" PDF not accessible – ignore file...")
        except Exception as e:
            logger.error(f" Error occurred: {e}")

        if tables:
            try:
                # prepare df
                df = clean(handle_table_partitions(tables=tables, results=True))
                if not df.empty:
                    rank_row = get_string_loc(df, rank=True, column=0)["rank"]["row"]
                    # remove everything above the rank row
                    df = df.iloc[rank_row:].copy()
                    df = clean_df(df)
                    # get columns for intermediate times
                    dist_locs = get_string_loc(df, *DISTS)["str"]["col"]
                    # get country locations
                    cntry_locs = get_string_loc(df, country=True, results=True)["cntry"]
                    country_rows, _ = cntry_locs["row"], cntry_locs["col"]

                    for idx, row in enumerate(country_rows):
                        boat_data[idx] = {
                            "country": get_country_code(df=df, row=row),
                            "rank": idx + 1,
                            "lane": get_lane(df=df, row=row, i=idx),
                            "athletes": get_athletes(df=df, rows=country_rows, i=idx),
                            "times": get_times(df=df, row=row, cols=dist_locs),
                            "inter_ranks": get_intermediate_ranks(df=df, row=row)
                        }
                    data = [value for value in check_extracted_data(boat_data).values()]

                elif df.empty:
                    data = []

                if data:
                    final_data["url"] = url
                    final_data["data"] = data

                    logger.debug(f"Extract of {url.split('/').pop()} successful.")
                else:
                    empty_files += 1
                    logger.warning(f"Empty file found: {url.split('/').pop()}.")

            except Exception as e:
                errors += 1
                failed_requests.append(url)
                logger.exception(f"Error at {url}: {e}.")

    total = len(urls) - empty_files
    rate = "{:.2f}".format(100 - ((errors / total if total else 0) * 100))
    print_stats(total=total, errors=errors, empties=empty_files, rate=rate)

    return final_data, failed_requests


# extract data per year and write data and failed requests to respective json files
# final_extracted_data, final_failed_requests = [], []


# for year in range(START_YEAR, END_YEAR):
#     logger.info(f"Start extraction for year: {year}")
#     # get competition ids for current year
#     competition_ids = get_competition_ids(years=year)
#     pdf_urls = get_pdf_urls(comp_ids=competition_ids, comp_limit=COMPETITION_LIMIT, results=True)[::EVERY_NTH_DOCUMENT]
#     # extract result data and get list of failed requests
#     pdf_data, failed_req = extract_table_data_from_pdf(urls=pdf_urls)
#     # append to final list
#     final_extracted_data.append(pdf_data)
#     final_failed_requests.append(failed_req)
#
# # write results to file
# write_to_json(data=final_extracted_data, filename="result_data")
# write_to_json(data=final_failed_requests, filename="result_data_failed")

'''
# Use this to test selected files
pdf_urls = [
    "https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/WCH_2017/WCH_2017_ROWMNOCOX4------------HEAT000100--_C73X2157.pdf",
]
pdf_data, failed_req = extract_data_from_pdf_urls(urls=pdf_urls)

write_to_json(data=pdf_data, filename="result_data")
write_to_json(data=failed_req, filename="result_data_failed")
'''