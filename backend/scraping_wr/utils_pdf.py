"""
####################################################################################################

Contains utility functions for pandas and the extraction of world rowing data from pdfs.

-------------------------------------

####################################################################################################
"""

import re
import pandas as pd
import numpy as np
from itertools import groupby
from operator import itemgetter
import logging

logger = logging.getLogger(__name__)


# constants
COUNTRY_CODES = {
    "AFG": "Afghanistan",
    "ALB": "Albanien",
    "ALG": "Algerien",
    "AND": "Andorra",
    "ANG": "Angola",
    "ANT": "Antigua und Barbuda",
    "ARG": "Argentinien",
    "ARM": "Armenien",
    "ARU": "Aruba",
    "ASA": "Amerikanisch Samoa",
    "AUS": "Australien",
    "AUT": "Österreich",
    "AZE": "Aserbaidschan",
    "BAH": "Bahamas",
    "BAN": "Bangladesch",
    "BAR": "Barbados",
    "BDI": "Burundi",
    "BEL": "Belgien",
    "BEN": "Benin",
    "BER": "Bermuda",
    "BHU": "Bhutan",
    "BIH": "Bosnien und Herzegowina",
    "BIZ": "Belize",
    "BLR": "Belarus",
    "BOL": "Bolivien",
    "BOT": "Botswana",
    "BRA": "Brasilien",
    "BRN": "Bahrain",
    "BRU": "Brunei",
    "BUL": "Bulgarien",
    "BUR": "Burkina Faso",
    "CAF": "Zentralafrikanische Republik",
    "CAM": "Kambodscha",
    "CAN": "Kanada",
    "CAY": "Kaimaninseln",
    "CGO": "Republik Kongo",
    "CHA": "Tschad",
    "CHI": "Chile",
    "CHN": "China",
    "CIV": "Elfenbeinküste",
    "CMR": "Kamerun",
    "COD": "Demokratische Republik Kongo",
    "COK": "Cookinseln",
    "COL": "Kolumbien",
    "COM": "Komoren",
    "CPV": "Kap Verde",
    "CRC": "Costa Rica",
    "CRO": "Kroatien",
    "CUB": "Kuba",
    "CYP": "Zypern",
    "CZE": "Tschechien",
    "DEN": "Dänemark",
    "DJI": "Dschibuti",
    "DMA": "Dominica",
    "DOM": "Dominikanische Republik",
    "ECU": "Ecuador",
    "EGY": "Ägypten",
    "ERI": "Eritrea",
    "ESA": "El Salvador",
    "ESP": "Spanien",
    "EST": "Estland",
    "ETH": "Äthiopien",
    "FIJ": "Fidschi",
    "FIN": "Finnland",
    "FRA": "Frankreich",
    "FSM": "Föderierte Staaten von Mikronesien",
    "GAB": "Gabun",
    "GAM": "Gambia",
    "GBR": "Vereinigtes Königreich",
    "GBS": "Guinea-Bissau",
    "GEO": "Georgien",
    "GEQ": "Äquatorialguinea",
    "GER": "Deutschland",
    "GHA": "Ghana",
    "GRE": "Griechenland",
    "GRN": "Grenada",
    "GUA": "Guatemala",
    "GUI": "Guinea",
    "GUM": "Guam",
    "GUY": "Guyana",
    "HAI": "Haiti",
    "HKG": "Hongkong",
    "HON": "Honduras",
    "HUN": "Ungarn",
    "INA": "Indonesien",
    "IND": "Indien",
    "IRI": "Iran",
    "IRL": "Irland",
    "IRQ": "Irak",
    "ISL": "Island",
    "ISR": "Israel",
    "ISV": "Jungferninseln (US)",
    "ITA": "Italien",
    "IVB": "Jungferninseln (UK)",
    "JAM": "Jamaika",
    "JOR": "Jordanien",
    "JPN": "Japan",
    "KAZ": "Kasachstan",
    "KEN": "Kenia",
    "KGZ": "Kirgisistan",
    "KIR": "Kiribati",
    "KOR": "Südkorea",
    "KOS": "Kosovo",
    "KSA": "Saudi-Arabien",
    "KUW": "Kuwait",
    "LAO": "Laos",
    "LAT": "Lettland",
    "LBA": "Libyen",
    "LBN": "Libanon",
    "LBR": "Liberia",
    "LCA": "St. Lucia",
    "LES": "Lesotho",
    "LIE": "Liechtenstein",
    "LTU": "Litauen",
    "LUX": "Luxemburg",
    "MAD": "Madagaskar",
    "MAR": "Marokko",
    "MAS": "Malaysia",
    "MAW": "Malawi",
    "MDA": "Moldawien",
    "MDV": "Malediven",
    "MEX": "Mexiko",
    "MGL": "Mongolei",
    "MHL": "Marshallinseln",
    "MKD": "Nordmazedonien",
    "MLI": "Mali",
    "MLT": "Malta",
    "MNE": "Montenegro",
    "MON": "Fürstentum Monaco",
    "MOZ": "Mosambik",
    "MRI": "Mauritius",
    "MTN": "Mauretanien",
    "MYA": "Myanmar",
    "NAM": "Namibia",
    "NCA": "Nicaragua",
    "NED": "Niederlande",
    "NEP": "Nepal",
    "NGR": "Nigeria",
    "NIG": "Niger",
    "NOR": "Norwegen",
    "NRU": "Nauru",
    "NZL": "Neuseeland",
    "OMA": "Oman",
    "PAK": "Pakistan",
    "PAN": "Panama",
    "PAR": "Paraguay",
    "PER": "Peru",
    "PHI": "Philippinen",
    "PLE": "Palästina",
    "PLW": "Palau",
    "PNG": "Papua-Neuguinea",
    "POL": "Polen",
    "POR": "Portugal",
    "PRK": "Nordkorea",
    "PUR": "Puerto Rico",
    "QAT": "Katar",
    "ROU": "Rumänien",
    "RSA": "Südafrika",
    "RUS": "Russland",
    "RWA": "Ruanda",
    "SAM": "Samoa",
    "SEN": "Senegal",
    "SEY": "Seychellen",
    "SGP|SIN": "Singapur",  # also SIN could occur: http://www.rowing-memorabilia.de/index.php/ioc-country-codes
    "SKN": "St. Kitts und Nevis",
    "SLE": "Sierra Leone",
    "SLO": "Slowenien",
    "SMR": "San Marino",
    "SOL": "Salomonen",
    "SOM": "Somalia",
    "SRB": "Serbien",
    "SRI": "Sri Lanka",
    "STP": "São Tomé und Príncipe",
    "SUD": "Sudan",
    "SUI": "Schweiz",
    "SUR": "Suriname",
    "SVK": "Slowakei",
    "SWE": "Schweden",
    "SWZ": "Eswatini",
    "SYR": "Syrien",
    "TAN": "Tansania",
    "TGA": "Tonga",
    "THA": "Thailand",
    "TJK": "Tadschikistan",
    "TKM": "Turkmenistan",
    "TLS": "Osttimor",
    "TOG": "Togo",
    "TPE|ROC": "Taiwan",
    "TTO": "Trinidad und Tobago",
    "TUN": "Tunesien",
    "TUR": "Türkei",
    "TUV": "Tuvalu",
    "UAE": "Vereinigte Arabische Emirate",
    "UGA": "Uganda",
    "UKR": "Ukraine",
    "URU": "Uruguay",
    "USA": "Vereinigte Staaten von Amerika",
    "UZB": "Usbekistan",
    "VAN": "Vanuatu",
    "VEN": "Venezuela",
    "VIE": "Vietnam",
    "VIN": "St. Vincent und die Grenadinen",
    "YEM": "Jemen",
    "ZAM": "Sambia",
    "ZIM": "Simbabwe",
    # the following codes are not defined
    "RPC": None
}
# Constants for race_data pdfs
DIST_INTERVALS = ["10", "25", "50"]
RACE_DIST = "2000"

"""
################################################################
General Utils
################################################################
"""


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df_regex = [
        r'\s+$',  # one or more whitespaces from end
        r'^\s+',  # one or more whitespaces from start
        r'\n'  # linebreak
    ]
    new_df = df.replace(df_regex, ['' for _ in df_regex], regex=True)
    return new_df


def print_stats(total: int, errors: int, empties: int, rate: str) -> None:
    """ Prints basic statistics for the pdf reading process. """
    logger.debug("{txt:-^25}".format(txt=f"\nRead: {total - errors}/{total} PDFs | ({rate}%)"))
    logger.debug("{txt:-^25}".format(txt=f" Empty Files: {empties} "))


def check_speed_stroke(df: pd.DataFrame, lb: float = 0.0, ub: float = float('inf')) -> list:
    """
    Removes linebreaks, fills non-numeric values with 0, returns: list
    Parameters:
    * lb:   defines lower bound for given float values
    * ub:   defines upper bound for given float values
    """
    if df.empty:
        return []
    df = df.replace('\\n', ' ', regex=True)
    df = df.apply(pd.to_numeric, errors='coerce').astype(float).fillna(0)
    return [x if (lb <= x <= ub) else 0 for x in list(np.concatenate(np.array(df)))]


'''
################################################################
WorldRowing Utils
################################################################
'''


def get_string_loc(df: pd.DataFrame, *args: str, country: bool = False, rank: bool = False, first: bool = False,
                   column: int = -1, results: bool = 0) -> dict:
    """ Returns: dict with string locations
    ------------
    Parameters:
    * df:           pandas DataFrame
    * *args:        option to search for arbitrary number of strings
    * country:      true/false if country row should be identified
    * rank:         true/false if rank row should be identified
    * first_loc:    true/false whether only the first occurrence should be checked (only relevant for random str and Rank)
    * column:       option to specify column
    * results:      0 = race_data.pdf | 1 = results.pdf
    ------------
    Return: dict with row, col indices for string args, country and rank
    """
    cntry_str, rank_str = "Country", "Rank"
    codes = COUNTRY_CODES.keys()

    locs: dict = {
        "str": {"row": [], "col": []},
        "cntry": {"row": [], "col": []},
        "rank": {"row": [], "col": []}
    }

    if args:
        if column == -1:
            col_list = []
            for search_str in args:
                for col in df.columns:
                    if df[col].str.contains(search_str).any():
                        col_list.append(col)
            col_list = list(set(col_list))  # remove duplicates
            col_list.sort()
            if col_list:
                locs["str"]["col"] = col_list[0] if first else col_list
        else:
            assert args[0] in df.values, "First arg not in DataFrame"
            locs["str"]["row"] = df.index[df[column] == args[0]].values[:1]

    if country and not results:
        # For race data pdfs we want to find either the row that contains the word "Country"
        # or the row that has most country code occurrences.
        cntry_str_found = df.isin([cntry_str]).any().any()
        if cntry_str_found:
            locs["cntry"]["row"] = [df.index[df[0] == cntry_str].values[0]]
        else:
            row_lst = []
            for col in df.columns:
                contains_code = df[col].str.contains('|'.join(codes), na=False)
                occurrence = df.loc[contains_code]
                row = int(occurrence.index[0]) if occurrence.size > 0 else None
                if isinstance(row, int):
                    row_lst.append(row)
            if row_lst:
                locs["cntry"]["row"] = [max(set(row_lst), key=row_lst.count)]

    elif country and results:
        # for results pdfs find all row-wise occurrences of country codes even if in multiple columns
        country_rows, country_codes = [], '|'.join(codes)
        for row in range(df.shape[0]):
            row_data = df.iloc[row].values.reshape(-1)
            country_code_regex = r"(?<![A-Z])[A-Z]{3}(?![A-Z])(?!\s)"
            data_el = list(filter(None, [re.findall(country_code_regex, str(data)) for data in row_data]))
            if any([str(el[0]) in country_codes for el in data_el if el]):
                country_rows.append(row)
        locs["cntry"]["row"] = country_rows

    if rank and not column == -1 and not df.empty:
        rank_loc = df[column].str.contains(rank_str, na=False)
        if not rank_loc.any() and df.shape[1] > 1:
            rank_loc = df[column+1].str.contains(rank_str, na=False)
        if rank_loc.any():
            rank_row = df.index[rank_loc][0]
            locs["rank"]["row"], locs["rank"]["col"] = rank_row, 0

    country_row_data = list(set(locs["cntry"]["row"]))
    country_row_data.sort()
    locs["cntry"]["row"] = country_row_data

    return locs


def find_distance_column(df: pd.DataFrame) -> int:
    differences = df.apply(pd.to_numeric, errors="coerce").diff().mode().fillna(0).astype(int).astype(str)
    mask = [differences[col].str.contains("|".join(DIST_INTERVALS)) for col in differences]
    dist_list = [el.name for el in mask if any(el)]
    return int(dist_list[0]) if dist_list else 0


def get_data_loc(df: pd.DataFrame, cust_str: str = '') -> tuple[int, int]:
    """ Find indices of race data (only speed and stroke in the table).
    --------------
    Parameters:
    * cust_str:     If provided: Search for individual start and end.
    *               If not provided: Final data value is expected to be at 2000.
    -------------
    Returns:        tuple of row indices (start, end) of race data.
    """
    start, end = 0, 0

    distance_column = find_distance_column(df)
    first_column = df[distance_column].values.flatten().tolist()
    dists = [re.sub(r"\n.*", "", str(x)) for x in first_column]

    try:
        if cust_str and cust_str in df.values:
            start = get_string_loc(df, cust_str, column=distance_column)["str"]["row"]
        elif cust_str and cust_str in dists:
            start = dists.index(cust_str)
        else:
            for i in DIST_INTERVALS:
                if i in df.values:
                    start = get_string_loc(df, i, column=distance_column)["str"]["row"]
                    break
            if start == 0 and end == 0:
                for i in DIST_INTERVALS:
                    if i in dists:
                        start = dists.index(i)
                        break
        end = last_num_idx(df, col=distance_column)

    except Exception as e:
        logging.error(f"Error finding data start/end: \n{e}")

    return int(start), int(end)


def remove_empty_columns(df: pd.DataFrame, data_loc: str = "") -> pd.DataFrame:
    """
    Remove columns that contain no data values.
    """
    data_start = int(get_data_loc(df, cust_str=data_loc)[0])
    if not data_start:
        return pd.DataFrame()
    data_row_len = df.shape[0]
    # find empty columns, i.e. the ones that contain no relevant information
    empty_cols = []
    for col in df.columns:
        if set(df[col].iloc[data_start:data_row_len].values).issubset(["", None]):
            empty_cols.append(col)
    # get groups of consecutive cols
    for k, g in groupby(enumerate(empty_cols), lambda x: x[0] - x[1]):
        group = list(map(int, (map(itemgetter(1), g))))

        # if there are two consecutive empty columns delete columns
        if len(group) == 2:
            df.drop(df.iloc[:, group[0]:group[-1]+1], axis=1)

        elif not len(group) == 2 and group[0] != 0:
            new_cols = df.iloc[:, group[0]:group[-1] + 1]
            df[group[0] - 1] = df[group[0] - 1].str.cat(new_cols, na_rep=" ")
    df = reset_axis(df.drop(empty_cols, axis=1), axes=[1])
    return df


def preprocess_raw_race_data_df(df: pd.DataFrame, nxt: int = 0):
    """
    Preprocessing includes:
    * find column with distance values and get distance interval
    * find last value as start point for subsequent tables
    * remove rows below data values, e.g. sponsorship information etc.
    ---------------------------
    Returns:
    * df:               processed dataframe
    * last_dist_value:  int of last distance value that occurred in the file
    * dist_interval:    interval of distances, i.e. 10, 25, 50
    """
    # identify column containing distance values
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    dist_col_idx = 1 if df_numeric[0].isnull().values.all() else 0

    # get distance interval, i.e. 10, 25 or 50
    dist_interval = int(df_numeric[dist_col_idx].diff().mode().get(0, 0))

    # get index of last distance value and last distance value
    last_dist_idx = last_num_idx(df, col=dist_col_idx)
    last_dist_value = df.iat[last_dist_idx, dist_col_idx]
    last_dist_value = int(last_dist_value) if last_dist_value.isdigit() else 0

    # drop all rows below last distance value and remove empty columns
    df = df.drop(df.index[last_dist_idx + 1:])
    df = remove_empty_columns(df, data_loc=str(nxt if nxt != 0 else ''))

    # only apply the following if not first dataframe
    if nxt != 0:
        next_loc = get_data_loc(df=df, cust_str=str(nxt))
        # exclude table head for subsequent dataframes
        df = df.iloc[next_loc[0]:next_loc[1] + 1]

    return df, last_dist_value, dist_interval


def handle_table_partitions(tables, results: bool = False):
    """ Camelot may create multiple table objects, e.g. when data is spread across multiple pages.
    This function should aggregate all tables to a single df.
    ----------
    Parameters:
    * tables:       table list from camelot-py
    * results:      0 = race_data.pdf, 1 = results.pdf
    ----------
    Returns:        pd.DataFrame containing all subframes
    """
    df = pd.DataFrame()
    # store interval and previous table end to keep track of where to join the data frames
    interval, table_end, previous_table_end = 0, 0, 0
    # edge case check, only keep dataframes that contain relevant data

    raw_dataframes = [split_column_at_string(handle_edge_cases(table.df, results=results)) for table in tables
                      if not handle_edge_cases(table.df, results=results).empty]

    # if no relevant data is extracted return empty dataframe
    if not raw_dataframes:
        return df

    # loop over dataframes and apply merging logic
    for idx, data_frame in enumerate(raw_dataframes):
        # if first table and dataframe is not empty
        if idx == 0 and not data_frame.empty:
            if results:
                pass  # result pdfs can just be appended
            else:  # race data pdfs have to be preprocessed
                data_frame, table_end, interval = preprocess_raw_race_data_df(data_frame)
                previous_table_end = table_end
            # append (sub)dataframe to main dataframe
            df = pd.concat([df, data_frame], ignore_index=True)

        # when there are more tables (and for race data pdfs final value for table_end (2000) is not reached)
        elif idx > 0 if results else (idx > 0 and table_end != int(RACE_DIST)):

            if not data_frame.empty:
                if results:
                    # table head can be ignored --> remove everything above the rank row
                    rank_row = get_string_loc(data_frame, rank=True, column=0)["rank"]["row"]
                    data_frame = data_frame.iloc[rank_row:]
                else:
                    previous_table_end = table_end
                    next_start = table_end + interval
                    data_frame, table_end, interval = preprocess_raw_race_data_df(data_frame, nxt=next_start)
                    if previous_table_end == table_end:
                        data_frame = pd.DataFrame()
                # append (sub)dataframe to main dataframe
                df = pd.concat([df, data_frame], ignore_index=True)
    return df


def apply_regex_sub(reg_exs: list, repl: str = '', input_string: str = ''):
    """ applies regex sub on input string and returns resulting string. """
    new_str = input_string
    for regex in reg_exs:
        new_str = re.sub(regex, repl, new_str)
    return new_str


def clean_str(str_list: list, style: str):
    """ Handles regular expressions to filter for specific data formats.
    -----------
    Parameters:
    * string:   input string
    * style:    time/name/country/number depending on the desired format
    -----------
    Returns:    filtered string
    """
    type_dict = {
        "time": [r"\(.*?\)", r"[^0-9.:]"],
        "name": [r"[0-9.:]", r"\(.*?\)", r"[A-Z]{3}$", r"^\s[A-Z][a-z]+", r"^dna$", r"^\*$"],
        "country": [r"\(.*?\)", r"[A-Z]{1,2}[a-z]+", r"[A-Z]{4,}"],
        "number": [r"\d+$", r"\D"],
        "dist": [r"\d*\.\d+", r"\n", r"[^0-9,]", r"\n.*"]
    }
    # for each input string apply specified regular expressions from list
    edited_strings = [apply_regex_sub(reg_exs=type_dict.get(style), repl='', input_string=str(el)) for el in str_list]
    # remove None, "0" and empty strings from list
    final_list = list(filter(lambda x: x not in [None, "0", ""], edited_strings))

    if style == "dist":
        # convert distance values to ints
        final_list = list(map(int, final_list))
    if style == "country":
        # only include valid country codes
        codes_regex = '^(' + '|'.join(COUNTRY_CODES.keys()) + ')\d?$'
        final_list = [country for country in final_list if re.match(codes_regex, str(country))]
    if style == "name":
        # remove 0 and remaining whitespaces
        final_list = list(filter(lambda x: x not in [0, " "], final_list))
    return final_list


def handle_edge_cases(df: pd.DataFrame, results=0) -> pd.DataFrame:
    """
    This function handles edge cases, e.g. dataframe contains no race data.
    Takes dataframe and returns corrected df. In error cases empty df.should be returned.
    Parameters:
    * results:     0 = race_data.pdf | 1 = results.pdf
    """
    country_row_idx = get_string_loc(df, country=True)["cntry"]["row"]
    rank_row_idx = get_string_loc(df, rank=True, column=0)["rank"]["row"]

    # Edge Case 1: Dataframe contains no country and no rank (often the table head)
    # if no country found and no rank found discard table by returning empty dataframe
    if results and country_row_idx and rank_row_idx:
        return df
    elif not results and country_row_idx:
        data_start, data_end = get_data_loc(df)
        if data_start != 0 or data_end != 0:
            return df
    return pd.DataFrame()


'''
################################################################
Pandas Utils
################################################################
'''


def last_num_idx(df: pd.DataFrame, col: int = 0, min_len: int = 3) -> int:
    """ Finds index of last numeric value of a minimum length in dataframe"""
    values = list(reversed(df[col].values))
    for idx, el in enumerate(values):
        if el and el.isdigit() and len(el) >= min_len:
            return (len(values) - 1) - idx
    return 0


def reset_axis(df: pd.DataFrame, axes: list) -> pd.DataFrame:
    """ Resets axes of dataframe starting from zero"""
    for axis in axes:
        df = df.set_axis(list(np.arange(0, df.shape[axis])), axis=axis)
    return df


def clean_df(df: pd.DataFrame):
    df.replace(r"^\s*$", np.nan, regex=True, inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df.fillna(0, inplace=True)
    df = reset_axis(df, axes=[0, 1])
    return df


def split_column_at_string(df: pd.DataFrame, split_str: str = '\n'):
    """ Splits columns at occurrence of given string """
    placeholder_df = pd.DataFrame()

    for col in df.columns:
        # find indices of split string occurrences
        split_str_idx = df.index[df[col].str.contains(split_str, regex=False)].to_numpy()
        if split_str_idx.any():
            # add split string to every cell that does not already contain the string
            # workaround to force split content shift to right column
            row_indices = [x for x in range(len(df.index)) if x not in split_str_idx]
            df.iloc[row_indices, col] = split_str + df.iloc[row_indices, col].astype(str)
        if isinstance(df[col], pd.Series) and df[col].astype(str).str.contains(split_str).any():
            new_cols = df[col].astype(str).str.split(split_str, expand=True)
        else:
            new_cols = df[col]

        # Special Edge Case: If distance values are split across multiple columns due to linebreaks ignore file:
        # affected files:
        # https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/ECH_2010/ECH_2010_ROWMSCULL1------------HEAT000200--_MGPSX9133.pdf
        # https://d3fpn4c9813ycf.cloudfront.net/pdfDocuments/JWCH_2010/JWCH_2010_ROWWNOCOX2--J---------HEAT000100--_MGPSX2279.pdf
        if not isinstance(new_cols, pd.Series) and col == 0:
            diffs = new_cols.apply(pd.to_numeric, errors="coerce").diff().mode().fillna(0).astype(int).astype(str)
            cols_with_dist_values = diffs.columns[diffs.isin(DIST_INTERVALS).any()].tolist()
            if len(cols_with_dist_values) > 1:
                break

        # add columns to placeholder dataframe
        placeholder_df = pd.concat([placeholder_df, new_cols], axis=1)

    new_df = reset_axis(df=placeholder_df, axes=[1])

    return new_df
