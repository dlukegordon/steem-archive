from contextlib import contextmanager
from datetime import datetime, timedelta
from termcolor import colored

from dateutil.parser import parse as dateutil_parse

# Context manager to report the time it takes to run something
@contextmanager
def timer(message):
    start_time = datetime.now()
    print_with_timestamp(f'{message}')
    try:
        yield
    finally:
        end_time = datetime.now()
        delta = end_time - start_time
        print_with_timestamp(f'{message}: {colored(get_timedelta_str(delta), "cyan")}')

def print_with_timestamp(message):
    datetime_str = colored(get_datetime_str(datetime.now()), 'cyan')
    print(f'[{datetime_str}] {message}')

def get_datetime_str(time):
    return str(time)[:-4]

# Return a pretty string representation of a timedelta
def get_timedelta_str(delta):
    s = str(timedelta(seconds = round(delta.total_seconds(), 2)))
    colon_indexes = [i for i, c in enumerate(s) if c == ':']
    if '.' in s:
        s = s[:s.index('.') + 3]
    s = s + 's'
    s = string_insert(s, colon_indexes[1], 'm')
    s = string_insert(s, colon_indexes[0], 'h')
    s = s.replace('0h:', '').replace('00m:', '')
    if s[0] == '0':
        s = s[1:]
    s = s.replace(':0', ' ')
    return s.replace(':', ' ')

def string_insert(s, index, to_insert):
    return s[:index] + to_insert + s[index:]

def parse_datetime(string):
    return dateutil_parse(string)

def parse_date(string):
    return dateutil_parse(string).date()

def get_header_string(message, width=150):
    header = f'===== {message} ====='
    return header + '=' * (width - len(header))

def get_link_string(author, permlink):
    return f'@{author}/{permlink}'
