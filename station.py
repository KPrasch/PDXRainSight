

class RainStation(object):
    def __init__(self, url, name, location):
        self.name = name
        self.location = location
        self.url = url

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    @classmethod
    def from_string(cls, string):
        'Creates a new RainStation from a scraped string'

        return

    def listen(self):
        'Starts the listener on a clock.'

        return

