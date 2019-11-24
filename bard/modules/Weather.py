import math
import json
import requests

from .Model import DataStore, Type
from .InfoThread import InfoThread
from .Constants import FONT_COLOR

class WeatherThread(InfoThread):
    LOC = 'Australind,au'
    URL = "https://api.openweathermap.org/data/2.5/weather"
    WEATHER_COLOR = {
        'sunny' : '#F0C674',
        'cloudy' : '#707880'
    }
    KELVIN_CONST = 273.15

    def __init__(self, q, file):
        super().__init__(q)
        with open(file) as f:
            data = json.load(f)
            self._api_key = data["key"]
        self.queue.put(DataStore(Type.WEATHER, self.get()))

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
        r = requests.get(self.URL, params={'APPID' : self._api_key, "q" : self.LOC })
        j = r.json()
        temp = math.ceil(float(j['main']['temp'])) - int(self.KELVIN_CONST)
        sunset = int(j['sys']['sunset'])
        id = int(j['weather'][0]['id'])
        desc = j['weather'][0]['description'].title()
        # print(self.get_icon(id))
        return '%{{F{color}}}{desc}, {temp}°%{{F}} {icon}'.format(color=FONT_COLOR,
                                                        desc=desc,
                                                        temp=temp,
                                                        icon=self.get_icon(id, sunset))

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(600)
            self.queue.put(DataStore(Type.WEATHER, self.get()))
