from apistar import Include, Route
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
import sys

sys.path.append('../')
from collector import RainCollector

raincollector = RainCollector()

BASE_URL = '../pages/index.html'


def welcome():
    with open(BASE_URL, 'r') as f:
        return f.read()


def start_daemon():
    raincollector()
    return {'message': 'started rain collection daemon'}


def daemon_status():
    return {'message': raincollector.describe()}


def station_status(query: str):
    stations = raincollector.search(query)
    if stations:
        data = [{f'{rs.name}': rs.describe()} for rs in stations]
    return {'results': data}


def list_stations():
    stations = [s.to_dict() for s in raincollector.stations]
    return {'results': stations}


routes = [
    Route('/', 'GET', welcome),
    Route('/daemon/start', 'POST', start_daemon),
    Route('/daemon/status', 'GET', daemon_status),
    Route('/stations/', 'GET', list_stations),
    Route('/stations/{query}', 'GET', station_status),
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

app = App(routes=routes)


if __name__ == '__main__':
    app.main()