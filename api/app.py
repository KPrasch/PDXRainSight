from apistar import Include, Route
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.handlers import docs_urls, static_urls
import sys

sys.path.append('../')
from collector import RainCollector

raincollector = RainCollector()


def welcome():
    return {'message': 'Welcome to the PDXRainSight powered by API Star'}


def start_daemon():
    raincollector()
    return {'message': 'started rain collection daemon'}


def daemon_status():
    return {'message': raincollector.describe()}


def station_status(query: str):
    stations = raincollector.search(query)
    if stations:
        data = [{f'{rs.name}': rs.describe()} for rs in stations]
    else:
        data = []
    return {'results': data}



routes = [
    Route('/', 'GET', welcome),
    Route('/raincollector/start', 'GET', start_daemon),
    Route('/raincollector/status', 'GET', daemon_status),
    Route('/station/{query}', 'GET', station_status),
    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

app = App(routes=routes)


if __name__ == '__main__':
    app.main()