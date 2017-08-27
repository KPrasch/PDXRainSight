import logging
import os
import threading
import time
from typing import List

import requests
from bs4 import BeautifulSoup, SoupStrainer

from station import RainStation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("collector")

url = str

BASE_URL = 'https://or.water.usgs.gov/precip/'


def spawn_station(url: str, stations):
    'worker thread'
    r = requests.get(url)
    rs = RainStation.from_http_request(r)
    stations.append(rs)


def spool_stations(station_urls: List[url]):
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


def fetch_links(quantity=10):
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


def check_for_update(stations):
    logger.info('Fetching update data.')
    check = stations[0].refresh()
    if check:
        return True
    else:
        return False


def collector(stations, interval=(60*60), retry=120):
    """Data collection daemon"""
    logger.info(f'Starting rain data collector on {interval}s interval.')
    time.sleep(3)
    pool = list()
    while True:
        # Check for update
        update = check_for_update(stations)
        if not update:
            logger.debug(f'No Update needed. Retrying in {retry} seconds.')
            time.sleep(retry)
            continue
        else:
            logger.info('Fetching Stations')

        # Fetch data in worker threads
        for s in stations:
            t = threading.Thread(target=s.refresh)
            t.start()
            pool.append(t)

        logger.debug(f'Spawned {len(stations)} threads.')
        logger.debug('Cleaning up...')

        #  Blocking - Gracefull exit.
        for i, t in enumerate(pool, start=1):
            t.join()
            pool.remove(t)    # Clean up

        logger.debug(f'All threads joined. Waiting for {interval} seconds.')
        time.sleep(interval)


def main():
    logger.info('Fetching links.')
    links = fetch_links()               # One-time use

    logger.info('Building Station objects.')
    stations = spool_stations(links)    # consume
    import pdb;pdb.set_trace()
    logger.info('Switching to damemon.')
    collector(stations)                 # listen


if __name__ == "__main__":
    main()