import json
from collections import namedtuple
from datetime import datetime

import geopy
import requests

from parsers.exceptions import RainParserError

RainDay = namedtuple('RainDay', ['date', 'total', 'data'])
RainHour = namedtuple('RainHour', ['hour', 'rain'])
GeoCoords = namedtuple('GeoCoords', ['lat', 'lng'])

import parsers.http as parser


class RainStation(object):
    def __init__(self, url, name, location):
        self.name = name
        self.location = location
        self.url = url

        # Metadata
        self.created = datetime.now()
        self.start_date = None     # datetime
        self.end_date = None       # datetime
        self.duration = None       # timedelta
        self.geocoords = None      # GeoCoord
        self.last_rain = None      # RainDay
        self.last_fetch = None     # datetime object
        self.max_rainday = None    # RainDay
        self.fetch_metadata()

        # Live data
        self.now = None            # hour int, rain int
        self.today = None          # RainDay
        self.daily_total = None    # int
        self.refresh()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.location})'

    def to_dict(self):
        lat, lng = self.geocoords
        years, days = divmod(self.duration.days, 365)
        hour, rain = self.now
        payload = {'name': self.name,
                   'location': self.location,
                   'position': [lat, lng],
                   'duration': f'{years} years, {days}, days',
                   'url': self.url,
                   'today': self.daily_total,
                   'now': {'hour': hour, 'rain': rain},
                   }
        return payload

    def to_json(self):
        d = self.to_dict()
        payload = json.dumps(d)
        return payload

    @classmethod
    def from_http_request(cls, request):
        'Creates a new RainStation from a scraped request object'
        first_line = next(request.iter_lines()).decode()
        try:
            name, location = list(map(str.strip, first_line.split('-')))
        except ValueError:
            raise RainParserError(f'Invalid location string: {first_line}')
        instance = cls(name=name, location=location, url=request.url)
        return instance

    def fetch_metadata(self):
        """
        Populates initial station metadata.

        self.start_date = None     # datetime
        self.end_date = None       # datetime
        self.duration = None       # timedelta
        self.geocoords = None      # GeoCoord
        self.last_rain = None      # RainDay
        self.last_fetch = None     # datetime object
        self.max_rainday = None    # RainDay

        """
        r = requests.get(self.url)

        # Time
        start, end = parser.parse_daterange(r)
        delta = end - start

        self.start_date = start
        self.end_date = end
        self.duration = delta

        # Geocoding
        geocoder = geopy.geocoders.GoogleV3()
        location = geocoder.geocode(query=f'{self.location}, Portland, OR')
        geocoords = GeoCoords(lat=location.latitude, lng=location.longitude)

        self.geocoords = geocoords
        return

    def refresh(self):
        r = requests.get(self.url, stream=True)
        today = parser.fetch_today(r)

        if today == self.today:
            return False

        self.today = today
        self.now = RainHour(hour=(len(self.today.data)-1), rain=self.today.data[-1])
        self.daily_total = self.today.total
        self.last_fetch = datetime.now()
        return True

    def describe(self):
        message = f'''
        --------------------------------
        ### {self.name} ###
        Location: {self.location}
        Position: {self.geocoords}
        Date Range: {self.start_date.ctime()} through {self.end_date.ctime()}
        Duration: {self.duration.days//365} Years {self.duration.days%365} Days
        URL: {self.url}
        --------------------------------
        Daily Total: {self.daily_total} 100/In.
        Current: {self.now} 100/In.
        Last RainDay: {self.last_rain}
        Record Day: {self.max_rainday}
        Last Update: {self.last_fetch.ctime()}
        --------------------------------
        '''
        # print(message)
        return message

    def daterange(self, start_date=None, end_date=None):
        r = requests.get(self.url)
        if start_date and end_date:
            result = parser.fetch_date(r, start_date, end_date)
        else:
            result = parser.fetch_today(r)
        return result

    def dumpdata(self):
        r = requests.get(self.url)
        dataset = r.text
        return dataset
