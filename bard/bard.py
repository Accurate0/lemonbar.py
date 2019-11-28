#!/usr/bin/env python3
import os
import sys
import time
import types
import argparse
from glob import glob
from os import path
import importlib, importlib.machinery
from queue import Queue
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

import bard.Config as cf
from bard.DBus import DBusThread
from bard.Model import Type, DataStore, Position
from bard.Module import ModuleManager, Module

from ewmh.ewmh import EWMH
from Xlib.display import Display

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', action='store', nargs=1, metavar='config.ini',
                        help='config file to use to run the bar')
    args = parser.parse_args()

    return args

def event_loop(div, queue, p, mm):
    data = {}
    for t, _ in mm.modules.items():
        data[t] = ''

    divider = div

    while d := queue.get():
        data[d.id] = d.data

        print(data)

        s = []
        for t, dat in data.items():
            s.append(dat)

        s.append('\n')
        # print(''.join(s))
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
    # workers = {
        # Type.DESKTOP : DesktopThread(queue, EWMH(), Display(),
        #                 c.lemonbar.desktop_inactive_color,
        #                 c.lemonbar.desktop_active_color),
        # Type.BATTERY : BatteryThread(queue, c.lemonbar.font_color),
        # Type.WEATHER : WeatherThread(queue, c.weather.key, c.lemonbar.font_color),
        # Type.TIME : TimeThread(queue, c.lemonbar.font_color),
    # }

    mm = ModuleManager(queue)
    # importlib.import_module('modules/Time')

    modules = c.modules.load.replace('\n', ' ').split(' ')
    # modules = [ file for file in glob('modules/*') if path.isfile(file) ]
    for module in modules:
        # print(module)
        loader = importlib.machinery.SourceFileLoader(path.basename(module), module)
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)
        cl = getattr(mod, mod.CLASSNAME)
        mm.add(mod.NAME, cl(queue, c))

    dbus = DBusThread(queue, mm)

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

    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

    div = f'%{{F{c.lemonbar.font_color}}}{c.lemonbar.divider}%{{F}}'
    event_loop(div, queue, p, mm)

if __name__ == '__main__':
    main()
