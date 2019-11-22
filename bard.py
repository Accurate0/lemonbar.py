#!/usr/bin/env python3
import sys
import time
import json
import math
import Xlib
import Xlib.X
import requests

from queue import Queue
from signal import signal
from ewmh.ewmh import EWMH
from enum import Enum, auto
from pydbus import SessionBus
from datetime import datetime
from gi.repository import GLib
from threading import Thread, Event
from Xlib.display import Display, X
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

START_TIME=time.time()

DESKTOP_INACTIVE = '#8f9ba8'
DESKTOP_ACTIVE = '#d25050'
FONT_COLOR = '#8f9ba8'
BACKGROUND = '#282a2e'
FONT_AWESOME = 'Font Awesome 5 Free:style=Solid:size=10'
MAIN_FONT = 'Roboto:style=Medium:size=11'
GEOMETRY = '1920x32'
DIVIDER = "%{{F{color}}}|%{{F}}".format(color=FONT_COLOR)
LEMONBAR_CMD = [
                    'lemonbar',
                    '-B', BACKGROUND,
                    '-o', '-3',
                    '-f', FONT_AWESOME,
                    '-o', '-1',
                    '-f', MAIN_FONT,
                    '-g', GEOMETRY,
                    '-n', 'pybar'
                ]
DESKTOPS = [
                '%{{F{active}}}firefox%{{F}}    %{{F{inactive}}}discord%{{F}}    %{{F{inactive}}}dota2%{{F}}',
                '%{{F{inactive}}}firefox%{{F}}    %{{F{active}}}discord%{{F}}    %{{F{inactive}}}dota2%{{F}}',
                '%{{F{inactive}}}firefox%{{F}}    %{{F{inactive}}}discord%{{F}}    %{{F{active}}}dota2%{{F}}'
           ]

# use logger at some point?

class Type(Enum):
    DESKTOP = auto()
    TIME = auto()
    WEATHER = auto()
    DBUS = auto()
    STOP = auto()

class DataStore():
    def __init__(self, id, data=None):
        self.id = id
        self.data = str(data)

class InfoThread(Thread):
    def __init__(self, q):
        super().__init__()
        self.queue = q
        self._stopping = Event()

    def join(self, timeout=None):
        self.queue.put(DataStore(Type.STOP))
        self._stopping.set()
        super(InfoThread, self).join(timeout)

class WeatherThread(InfoThread):
    LOC = 'Australind,au'
    URL = "https://api.openweathermap.org/data/2.5/weather"
    WEATHER_COLOR = {
        'sunny' : '#F0C674',
        'cloudy' : '#707880'
    }
    KELVIN_CONST = 273.15

    def __init__(self, q):
        super().__init__(q)
        with open('key.json') as f:
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
        return '%{{F{color}}}{temp}°, {desc}%{{F}} {icon}'.format(color=FONT_COLOR,
                                                        desc=desc,
                                                        temp=temp,
                                                        icon=self.get_icon(id, sunset))

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(600)
            self.queue.put(DataStore(Type.WEATHER, self.get()))

class TimeThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)

    def run(self):
        while not self._stopping.is_set():
            t = datetime.now().strftime('%e %B, %I:%M %p')
            t = '%{{F{color}}}{time}  %{{F}}'.format(time=t, color=FONT_COLOR)
            self.queue.put(DataStore(Type.TIME, t))
            self._stopping.wait(5)

class DesktopThread(InfoThread):
    def __init__(self, q, e, x):
        super().__init__(q)
        self.ewmh = e
        self.x = x

        x.screen().root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def run(self):
        while not self._stopping.is_set() and self.x.next_event():
            self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def current_desktop(self):
        d = self.ewmh.getCurrentDesktop()
        return '   {}'.format(DESKTOPS[d].format(active=DESKTOP_ACTIVE, inactive=DESKTOP_INACTIVE))

class DBusDesktop(object):
    pass

class DBusManager(object):
    """
    <node>
        <interface name='com.yeet.bard.Manager'>
            <method name='refresh'>
                <arg type='s' name='response' direction='out'/>
            </method>
            <method name='stop'/>
            <method name='status'>
                <arg type='s' name='response' direction='out'/>
            </method>
        </interface>
    </node>
    """
    def __init__(self, q, l):
        super().__init__()
        self._q = q
        self._l = l

    def refresh(self):
        # self._q.put(DataStore(Type.DBUS, 'stop'))
        return 'success'

    def stop(self):
        self._l.quit()
        self._q.put(DataStore(Type.STOP))

    def status(self):
        return 'running time: {}' \
                .format(
                        datetime.utcfromtimestamp(
                            time.time() - START_TIME
                        ).strftime('%H:%M:%S:%f')
                )

class DBusThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()

    def run(self):
        self._bus.publish('com.yeet.bard', DBusManager(self.queue, self._loop))
        self._loop.run()

def setup_workers(queue):
    workers = [
        DesktopThread(queue, EWMH(), Display()),
        TimeThread(queue),
        WeatherThread(queue),
        DBusThread(queue),
    ]

    for worker in workers:
        worker.daemon = True
        worker.start()

    return workers

def event_loop(queue, p):
    data = {
        Type.DESKTOP : "",
        Type.TIME : "",
        Type.WEATHER : "",
    }

    while d := queue.get():
        if d.id == Type.STOP:
            break

        if d.id == Type.DBUS:
            pass
        else:
            data[d.id] = d.data

        p.stdin.write('%{{l}}{desktop}%{{l}}%{{r}}{weather} {div} {time}%{{r}}'
                                                    .format(desktop=data[Type.DESKTOP],
                                                            time=data[Type.TIME],
                                                            weather=data[Type.WEATHER],
                                                            div=DIVIDER)
                                                    .encode())
        p.stdin.flush()
        queue.task_done()


def main():
    queue = Queue()
    workers = setup_workers(queue)
    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    try:
        event_loop(queue, p)
    except:
        for worker in workers:
            worker.join(0)

if __name__ == '__main__':
    main()
