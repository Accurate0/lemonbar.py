#!/usr/bin/env python3
import os
import sys
import time
import types
import argparse
from queue import Queue
from collections import defaultdict
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

import bard.Config as cf
from bard.DBus import DBusThread
from bard.ModuleLoader import ModuleLoader
from bard.Module import ModuleManager, Module
from bard.Model import Type, DataStore, Position

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', action='store', nargs=1, metavar='config.ini',
                        help='config file to use to run the bar')
    args = parser.parse_args()

    return args

def event_loop(c, queue, p, mm):
    div = f'%{{F{c.lemonbar.font_color}}}{c.lemonbar.divider}%{{F}}'
    data = {}
    for t, m in mm.modules.items():
        data[t] = ('', m.position)

    lemonbarpos = {
        Position.RIGHT : '%{r}',
        Position.LEFT : '%{l}',
        Position.CENTER : '%{c}',
    }

    while d := queue.get():
        data[d.id] = (d.data, data[d.id][1])

        # quite epic
        # create a dict of position to a list of ids
        # eg. {
        #       <Position.LEFT: 3>: ['com.yeet.bard.Desktop'],
        #       <Position.RIGHT: 1>: ['com.yeet.bard.Time', 'com.yeet.bard.Weather']
        # }
        v = {}
        for key, value in sorted(data.items()):
            v.setdefault(value[1], []).append(key)

        # the idea is to force only a singular %{r}
        # formatting tag on each side of things
        # for that location
        s = []
        for pos, lis in v.items():
            position = lemonbarpos[pos]
            s.append(position)
            for k in lis:
                s.append(data[k][0])
            s.append(position)

        s = ''.join(s)
        # print(s)
        p.stdin.write(s.encode())
        p.stdin.flush()
        queue.task_done()

def main():
    args = run_argparse()
    c = cf.parse(args.config)
    queue = Queue()
    mm = ModuleManager(queue)
    ModuleLoader.load_modules(c, mm, queue)
    dbus = DBusThread(queue, mm, c)

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

    event_loop(c, queue, p, mm)

if __name__ == '__main__':
    main()
