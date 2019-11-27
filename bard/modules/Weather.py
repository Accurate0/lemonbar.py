import math
import json
import requests

from .Model import DataStore, Type
from .InfoThread import InfoThread

class WeatherThread(InfoThread):
    LOC = 'Australind,au'
    URL = "https://api.openweathermap.org/data/2.5/weather"
    WEATHER_COLOR = {
        'sunny' : '#F0C674',
        'cloudy' : '#707880'
    }
    KELVIN_CONST = 273.15

    def __init__(self, q, key, font_col):
        super().__init__(q, 'Weather')
        self._api_key = key
        self.font_col = font_col

    @staticmethod
    def get_icon(id, sunset):
        if id < 500:
            icon = ''
            color = WeatherThread.WEATHER_COLOR['rain']
        elif id == 800:
            icon = ''
            color = WeatherThread.WEATHER_COLOR['sunny']
        elif id > 800:
            icon = ''
            color = WeatherThread.WEATHER_COLOR['cloudy']

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
            s = ' %{{F{color}}}{desc}, {temp}°%{{F}} {icon} '.format(color=self.font_col,
                                                        desc=desc,
                                                        temp=temp,
                                                        icon=self.get_icon(id, sunset))
        else:
            print(f'Could not connect to OWM API: {r.status_code}, {r.reason}')

        return s if self._loaded else ''

    def put_new(self):
        super().put_new()
        s = self.get()
        self.queue.put(DataStore(Type.WEATHER, s))
        return s

    def run(self):
        while not self._stopping.is_set():
            self.put_new()
            self._stopping.wait(600)
