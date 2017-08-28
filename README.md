# PDXRainSight
A tool for scraping live rain data from USGS and serving the data over a Websocket.


## Usage

### REST API

To run the api locally:
```
$ apistar run
Running at http://localhost:8080/
$ open http://localhost:8080/docs/
```

## Implementation details

#### RainStation.describe()
```
Name: Open Meadows School Rain Gage
Location: 7602 N. Emerald Ave.
Position: GeoCoords(lat=45.5778805, lng=-122.6994765)
Date Range: Wed Aug 26 00:00:00 1998 through Sat Aug 26 00:00:00 2017
Duration: 19 Years 5 Days
URL: https://or.water.usgs.gov/precip/open_meadows.rain

Total: 0 100/In.
Current: RainHour(hour=23, rain=0) 100/In.
Today: RainDay(date=datetime.datetime(2017, 8, 26, 0, 0), total=0, data=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
Record Day: None
Last Update: 2017-08-27 01:23:54.418359

```