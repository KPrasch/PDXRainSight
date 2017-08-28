import logging
import os
import threading

import requests
from bs4 import BeautifulSoup, SoupStrainer

from parsers.exceptions import RainParserError
from station import RainStation

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("collector")

url = str

BASE_URL = 'https://or.water.usgs.gov/precip/'


def spawn_station(url: str, stations):
    'worker thread'
    r = requests.get(url)
    try:
        rs = RainStation.from_http_request(r)
    except RainParserError:
        pass #TODO
    else:
        stations.append(rs)


def fetch_links(quantity=3):
    'Generates a list of station datasheet urls.'
    logger.info(f'Fetching {quantity} urls from {BASE_URL}')
    r = requests.get(BASE_URL)
    strainer = SoupStrainer('a')
    soup = BeautifulSoup(r.text, 'html.parser', parse_only=strainer)

    i = 0
    while quantity > 0:
        href = soup.contents[i]['href']
        if '.rain' in href:
            logger.debug(f'Found {href}')
            yield os.path.join(BASE_URL, href)
            quantity -= 1
        i += 1


def spool_stations():
    logger.info('Fetching links.')
    station_urls = fetch_links()
    logger.info('Building Station objects.')
    stations, pool = list(), list()
    for i, surl in enumerate(station_urls):
        t = threading.Thread(target=spawn_station, args=(surl, stations))
        t.start()
        pool.append((i, t))

    # Wait, then return
    for i, t in pool:
        t.join()
        logger.debug(f'Joined thread {i}')
    return stations
