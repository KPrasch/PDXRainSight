import logging
import threading
import time

from populate import spool_stations, BASE_URL

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("RainCollector")

url = str


class RainCollector(object):
    def __init__(self, interval=(60*60), retry=120):
        self.interval = interval
        self.retry = retry

        self.stations = spool_stations()

        self.daemon = threading.Thread(target=self._start, daemon=True)
        self.workers = list()

    def __repr__(self):
        result = f'{self.__class__.__name__}({self.interval}, {self.retry})'
        return result

    def __len__(self):
        return len(self.stations)

    def __getitem__(self, item):
        return self.stations[item]

    def __call__(self):
        self.daemon.start()
        return

    def spool(self):
        for s in self.stations:
            t = threading.Thread(target=s.refresh)
            t.start()
            self.workers.append(t)
        return

    def join(self):
        for i, t in enumerate(self.workers, start=1):
            t.join()
            self.workers.pop(t)  # Clean up
        return

    def stop(self):
        self.daemon.join()
        return

    def _start(self):
        """Data collection daemon"""
        logger.info(f'Starting rain data collector on {self.interval}s interval.')
        time.sleep(3)

        while True:
            # Check for update
            update = self.check_for_update()
            if not update:
                logger.debug(f'No Update needed. Retrying in {self.retry} seconds.')
                time.sleep(self.retry)
                continue
            else:
                logger.info('Fetching Stations')

            # Fetch data in worker threads
            self.spool()
            logger.debug(f'Spawned {len(self.stations)} threads.')
            logger.debug('Cleaning up...')

            self.join()
            logger.debug(f'All threads joined. Waiting for {self.interval} seconds.')
            time.sleep(self.interval)

    def check_for_update(self):
        logger.info('Fetching update data.')
        check = self.stations[0].refresh()    #TODO: use HEAD request for modified date from GMT
        if check:
            return True
        else:
            return False


if __name__ == '__main__':
    raincollector = RainCollector()
    raincollector()
    import pdb;pdb.set_trace()