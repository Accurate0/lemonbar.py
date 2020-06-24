import math
import json
import requests
import logging

from bard import Utilities
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

logger = logging.getLogger(__name__)

class Weather(Module):
    dbus = '<node> \
                <interface name=\'{name}\'> \
                    <method name=\'refresh\'/> \
                </interface> \
            </node>'

    LOC = 'Australind,au'
    URL = 'https://api.openweathermap.org/data/2.5/weather'
    WEATHER_COLOR = {
        'sunny' : '#F0C674',
        'cloudy' : '#FFFFFF',
        'rain' : '#FFFFFF'
    }
    KELVIN_CONST = 273.15

    def __init__(self, q, conf, name):
        super().__init__(q, conf, name)
        self._api_key = conf['key']
        self.font_col = conf['font_color']

    @property
    def position(self):
        return Position.RIGHT

    @property
    def priority(self):
        return 0

    def callback(self, iterable):
        pass

    @staticmethod
    def get_icon(id, sunset):
        if id <= 500:
            icon = ''
            color = Weather.WEATHER_COLOR['rain']
        elif id == 800:
            icon = ''
            color = Weather.WEATHER_COLOR['sunny']
        elif id > 800:
            icon = ''
            color = Weather.WEATHER_COLOR['cloudy']

        return '%{{F{color}}}{icon}%{{F}}'.format(icon=icon, color=color)

    def get(self):
        s = str()
        r = requests.get(self.URL, params={'APPID' : self._api_key, "q" : self.LOC })
        j = r.json()
        if r.status_code == requests.codes.ok:
            temp = math.ceil(float(j['main']['temp'])) - int(self.KELVIN_CONST)
            sunset = int(j['sys']['sunset'])
            id = int(j['weather'][0]['id'])
            desc = j['weather'][0]['description'].title()
            s = Utilities.f_colour('{}, {}°'.format(desc, temp), self.font_col)
            s = f'{s} {self.get_icon(id, sunset)}'

        else:
            logger.error(f'Could not connect to OWM API: {r.status_code}, {r.reason}')

        return s

    def refresh(self):
        super().refresh()
        try:
            s = self.get()
        except requests.exceptions.ConnectionError as ce:
            s = ce.__doc__

        self._queue.put(DataStore(self.name, s, self.position, self.priority))
        return s

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(600)
            self.refresh()
