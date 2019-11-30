import math
import json
import requests

from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

NAME = 'com.yeet.bard.Weather'
CLASSNAME = 'WeatherThread'

class WeatherThread(Module):
    """
    <node>
        <interface name='com.yeet.bard.Weather'>
            <method name='refresh'/>
        </interface>
    </node>
    """
    LOC = 'Australind,au'
    URL = "https://api.openweathermap.org/data/2.5/weather"
    WEATHER_COLOR = {
        'sunny' : '#F0C674',
        'cloudy' : '#707880'
    }
    KELVIN_CONST = 273.15

    def __init__(self, q, conf):
        super().__init__(q, NAME)
        self._api_key = conf.weather.key
        self.font_col = conf.lemonbar.font_color

    @property
    def position(self):
        return Position.RIGHT

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

    def refresh(self):
        self.put_new()

    def get(self):
        s = str()
        r = requests.get(self.URL, params={'APPID' : self._api_key, "q" : self.LOC })
        j = r.json()
        if r.status_code == requests.codes.ok:
            temp = math.ceil(float(j['main']['temp'])) - int(self.KELVIN_CONST)
            sunset = int(j['sys']['sunset'])
            id = int(j['weather'][0]['id'])
            desc = j['weather'][0]['description'].title()
            s = '%{{F{color}}}{desc}, {temp}°%{{F}} {icon}'.format(color=self.font_col,
                                                        desc=desc,
                                                        temp=temp,
                                                        icon=self.get_icon(id, sunset))
        else:
            print(f'Could not connect to OWM API: {r.status_code}, {r.reason}')

        return s

    def put_new(self):
        super().put_new()
        s = self.get()
        self._queue.put(DataStore(self.name, self.get(), self.position))
        return s

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(600)
            self.put_new()
