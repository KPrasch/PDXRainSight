import os

import itertools
import threading

import requests
from typing import List, Iterator
from bs4 import BeautifulSoup, SoupStrainer

from station import RainStation

url = str

BASE_URL = 'https://or.water.usgs.gov/precip/'

def station_fetcher(url: str, stations):
    r = requests.get(url, stream=True)
    name, location = str(next(r.iter_lines())).split('-')
    rs = RainStation(name=name, location=location, url=url)
    stations.append(rs)

def create_stations(station_urls: List[url]):
    stations = list()
    for surl in station_urls:
        t = threading.Thread(target=station_fetcher, args=(surl, stations))
        t.start()
    return stations

def fetch_links(quantity=3) -> Iterator[url]:
    'Generates a list of station datasheet urls.'

    r = requests.get(BASE_URL)
    strainer = SoupStrainer('a')
    soup = BeautifulSoup(r.text, 'html.parser', parse_only=strainer)
    i = 0
    while quantity > 0:
        href = soup.contents[i]['href']
        if '.rain' in href:
            yield os.path.join(BASE_URL, href)
            quantity -= 1
        i += 1

def main():
    links = fetch_links()
    stations = create_stations(links)

if __name__ == "__main__":
    main()