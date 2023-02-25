import re
from datetime import datetime

def get_(data, key, default=None):
    if data == None:
        return default
    
    if not isinstance(data, dict):
        raise ValueError("data Parameter is not dict type")
    
    return data.get(key, default)


def int_(s):
    is_digit_str = isinstance(s, str) and s.isdigit()
    is_int = isinstance(s, int)
    if is_digit_str or is_int:
        return int(s)
    return 0


class Timedelta_Parser:
    regex = re.compile( r"^(((\d*):)?((\d*):)?(\d*))(\.(\d*))?$" )
    
    def to_microseconds(delta_str: str) -> int:
        if not isinstance(delta_str, str):
            raise TypeError("Not a string")

        parsed = datetime.strptime(delta_str.strip(), '%H:%M:%S.%f')

        SECOND_IN_MICROSEC = 1000000
        MINUTE_IN_MICROSEC = 60 * SECOND_IN_MICROSEC
        HOUR_IN_MICROSEC   = 60 * MINUTE_IN_MICROSEC

        sum_us  = parsed.microsecond
        sum_us += parsed.second * SECOND_IN_MICROSEC
        sum_us += parsed.minute * MINUTE_IN_MICROSEC
        sum_us += parsed.hour * HOUR_IN_MICROSEC

        return sum_us

    def to_millis(delta_str: str) -> int:
        us = Timedelta_Parser.to_microseconds(delta_str=delta_str)
        ms = round(us/1000)
        return ms

    def to_millis__deprecated_(delta_str: str) -> int:
        """returns int in milliseconds
        
        Input format 'HH:MM:SS.mmm'. Examples: 
        '00:01:53.920', '00:07:59.75', '59.920', '::59.920', '::.', '::1.'
        """
        error = ValueError("Timedelta string does not match the format 'HH:MM:SS.mmm'")

        if not isinstance(delta_str, str):
            raise TypeError("Not a string")

        SECOND_IN_MILLIS = 1000
        MINUTE_IN_MILLIS = 60 * SECOND_IN_MILLIS
        HOUR_IN_MILLIS   = 60 * MINUTE_IN_MILLIS
        
        result = Timedelta_Parser.regex.match(delta_str)
        
        if result == None:
            raise error

        parsed = dict(hours=None, minutes=None, seconds=None, milliseconds=None)
        left_part, milliseconds_raw = result.group(1,8)
        
        # strip trailing zeros
        parsed['milliseconds'] = milliseconds_raw.rstrip('0')

        # Now split colon separated left part

        left_part_split = left_part.split(':')
        
        if len(left_part_split) > 3:
            raise error

        for unit, string in zip(('seconds','minutes','hours'), reversed(left_part_split)):
            parsed[unit] = string

        sum_ms  = int_(parsed['milliseconds'])
        sum_ms += int_(parsed['seconds']) * SECOND_IN_MILLIS
        sum_ms += int_(parsed['minutes']) * MINUTE_IN_MILLIS
        sum_ms += int_(parsed['hours']) * HOUR_IN_MILLIS

        return sum_ms


__wr_distance_regex = re.compile( r"^d(\d+)m$" )
def parse_wr_intermediate_distance_key(distancy_key: str) -> int:
    """Input: "d2000m" -> Output: int(2000)"""

    if not isinstance(distancy_key, str):
        raise TypeError("Not a string")

    result = __wr_distance_regex.match(distancy_key)
    if result == None:
        raise ValueError("distancy_key does not look like e.g. 'd1234m'")

    meters = result.group(1)
    return int(meters)

def make_keys_lowercase(dict_: dict) -> dict:
    return {k.lower():v for k,v in dict_.items()}

def is_number(obj):
    return isinstance(obj, int) or isinstance(obj, float)

def select_first(iterable, condition_func, default_value=None):
    """ Return first element in iterable fullfilling condition_func(element)
    https://stackoverflow.com/a/2364277 """
    return next((x for x in iterable if condition_func(x)), default_value)

def stepfunction(x, stepsize=500):
    """ uniform stepfunction:
    [1 ....... 500] -> 500
    [501 .... 1000] -> 1000
    [1001 ... 1500] -> 1500
    etc.
    """
    stepsize = int(stepsize)
    return (((int(x)-1)//stepsize)+1) * stepsize 