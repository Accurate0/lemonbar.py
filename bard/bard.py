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

def event_loop(div, queue, p):
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
                                                            div=div)
                                                    .encode())
        p.stdin.flush()
        queue.task_done()

#TODO Replace file hack with config file parsing

def main():
    args = run_argparse()
    c = cf.parse(args.config)

    queue = Queue()
    workers = [
        DesktopThread(queue, EWMH(), Display(),
                        c.lemonbar.desktop_inactive_color,
                        c.lemonbar.desktop_active_color),
        TimeThread(queue, c.lemonbar.font_color),
        WeatherThread(queue, c.weather.key, c.lemonbar.font_color),
        DBusThread(queue),
    ]

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

    for worker in workers:
        worker.daemon = True
        worker.start()

    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    try:
        div = f'%{{F{c.lemonbar.font_color}}}{c.lemonbar.divider}%{{F}}'
        event_loop(div, queue, p)
    except Exception as e:
        print(e)
        for worker in workers:
            worker.join()

if __name__ == '__main__':
    main()
