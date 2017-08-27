from datetime import datetime
from collections import namedtuple

import requests
import geopy

RainDay = namedtuple('RainDay', ['date', 'total', 'data'])
RainHour = namedtuple('RainHour', ['hour', 'rain'])
GeoCoords = namedtuple('GeoCoords', ['lat', 'lng'])

import parser


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

    @classmethod
    def from_http_request(cls, request):
        'Creates a new RainStation from a scraped request object'
        first_line = next(request.iter_lines()).decode()
        name, location = list(map(str.strip, first_line.split('-')))
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
        Total: {self.daily_total} 100/In.
        Current: {self.now} 100/In.
        Today: {self.today}
        Last RainDay: {self.last_rain}
        Record Day: {self.max_rainday}
        Last Update: {self.last_fetch.ctime()}
        --------------------------------
        '''
        print(message)
        return

    def daterange(self, start_date=None, end_date=None):
        r = requests.get(self.url)
        if start_date and end_date:
            result = parser.fetch_date(r, start_date, end_date)
        else:
            result = parser.fetch_today(r)
        return result

    def dumpdata(self):
        r = requests.get(self.url)
        data_str = r.text
        return data_str