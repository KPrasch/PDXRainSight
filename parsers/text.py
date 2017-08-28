from datetime import datetime

from parsers.exceptions import RainParserError
from station import RainHour, RainDay


def raindate(date_str):
    raindate = datetime.strptime(date_str, '%d-%b-%Y')
    return raindate


def parse_total(total_str: str) -> int:
    try:
        total = int(total_str)
    except ValueError:
        if total_str == '-':
            total = 0
        else:
            message = f'Got in valid value "{total}" for total rainfall amount.'
            raise RainParserError(message)
    return total


def parse_hourly(hourly: list) -> tuple:
    'parses the hourly data'
    rainfall = list()
    for hour, rain in enumerate(hourly):
        try:
            datum = int(rain)
        except ValueError:
            if rain == '-':
                datum = 0
            else:
                message = f'Got in valid value "{total}" for hourly rainfall amount.'
                raise RainParserError(message)
        finally:
            rainhour = RainHour(hour=hour, rain=datum)
            rainfall.append(rainhour)
    return tuple(rainfall)


def parse_row(row: str):
    'Controls the helper function above'
    try:
        date_str, total_str, *hourly = row.split()
    except ValueError:
        raise RainParserError(f'Invalid raw data "{row}"')

    date = raindate(date_str)
    total = parse_total(total_str)
    rainfall = parse_hourly(hourly)

    rainday = RainDay(date=date, total=total, data=tuple(rainfall))
    return rainday


