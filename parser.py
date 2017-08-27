from datetime import datetime
from typing import Tuple

from station import RainHour, RainDay


def parse_row(row: str):
    data = tuple(row.split())
    date = datetime.strptime(data[0], '%d-%b-%Y')
    rainfall = list()
    for n in data[2:]:
        try:
            datum = int(n)
        except ValueError as err:
            if n == '-':
                datum = 0
            else:
                raise err
        rainfall.append(datum)

    rainday = RainDay(date=date, total=int(data[1]), data=tuple(rainfall))
    return rainday


def parse_daterange(request) -> tuple:
    lines = remove_header(request)
    item = None
    last_rainday = parse_row(next(lines).decode())
    for item in request.iter_lines():
        pass
    first_rainday = parse_row(item.decode())
    return first_rainday.date, last_rainday.date



def remove_header(request):
    'removes the header of the files payload by advancing....'
    lines = request.iter_lines()
    for _ in range(11):
        next(lines)
    return lines


def extract_header(request) -> Tuple[str, str]:
    'Parses a rain dataset request for name and location info'
    first_line = next(request.iter_lines()).decode()
    rain_gauge, location = tuple(map(str.strip, first_line.split('-')))
    return rain_gauge, location


def fetch_today(request):
    lines = remove_header(request)
    data_str = next(lines).decode()
    rainday = parse_row(data_str)
    return rainday


def fetch_date(request, start, end=None):
    lines = remove_header(request)

    start_date_str = datetime.strftime(start, '%d-%b-%Y').encode()
    raindays = list()
    if start and end:
        end_date_str = datetime.strftime(end, '%d-%b-%Y').encode()
        for row in lines:
            if row[:11] == end_date_str:
                break
        else:
            return None

    for row in lines:
        rainday = parse_row(row.decode())
        raindays.append(rainday)
        if row[:11] == start_date_str:
            break
    else:
        result = None

    result = raindays
    return result