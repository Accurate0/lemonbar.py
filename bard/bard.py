#!/usr/bin/env python3
import os
import sys
import time
import argparse
from queue import Queue
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

import modules.Config as cf
from modules.Model import Type
from modules.Time import TimeThread
from modules.Model import DataStore
from modules.DBus import DBusThread
from modules.Battery import BatteryThread
from modules.InfoThread import InfoThread
from modules.Desktop import DesktopThread
from modules.Weather import WeatherThread

from ewmh.ewmh import EWMH
from Xlib.display import Display

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', action='store', nargs=1, metavar='config.ini',
                        help='config file to use to run the bar')
    args = parser.parse_args()

    return args

def event_loop(div, queue, p, workers):
    data = {
        Type.DESKTOP : '',
        Type.BATTERY : '',
        Type.WEATHER : '',
        Type.TIME : '',
    }

    divider = div

    while d := queue.get():
        if d.id == Type.DBUS and d.data == 'stop':
            break

        data[d.id] = d.data
            # print(data[d.id])

        # initial, all other modules go to right side
        s = ['%{{l}}{desktop}%{{l}}%{{r}}'.format(desktop=data[Type.DESKTOP])]

        # TODO :  handle left most still leaving a div on the right side
        for i, (t, worker) in enumerate(workers.items()):
            if t != Type.DESKTOP:
                if worker.is_loaded() and i != 1:
                    s.append(div)
                s.append(data[t])

                if worker.is_loaded():
                    if i != len(workers) - 1:
                        pass

        s = ''.join(s)
        p.stdin.write(s.encode())
        p.stdin.flush()
        queue.task_done()

#TODO Replace file hack with config file parsing

def main():
    args = run_argparse()
    # TODO : Add config parsing for modules to load
    c = cf.parse(args.config)

    queue = Queue()
    workers = {
        Type.DESKTOP : DesktopThread(queue, EWMH(), Display(),
                        c.lemonbar.desktop_inactive_color,
                        c.lemonbar.desktop_active_color),
        Type.BATTERY : BatteryThread(queue, c.lemonbar.font_color),
        Type.WEATHER : WeatherThread(queue, c.weather.key, c.lemonbar.font_color),
        Type.TIME : TimeThread(queue, c.lemonbar.font_color),
    }

    dbus = DBusThread(queue, workers)

    LEMONBAR_CMD = [
                        'lemonbar',
                        '-B', c.lemonbar.background_color,
                        '-o', '-3',
                        '-f', c.lemonbar.font_awesome,
                        '-o', '-1',
                        '-f', c.lemonbar.font,
                        '-g', c.lemonbar.geometry,
                        '-n', __file__
                    ]

    dbus.daemon = True
    dbus.start()
    for _, worker in workers.items():
        worker.daemon = True
        worker.start()

    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    div = f'%{{F{c.lemonbar.font_color}}}{c.lemonbar.divider}%{{F}}'
    event_loop(div, queue, p, workers)

if __name__ == '__main__':
    main()
