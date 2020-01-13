#!/usr/bin/env python3
import os
import sys
import time
import types
import argparse
from queue import Queue
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

from bard import Utilities
import bard.ModuleLoader as md
import bard.Config as cf
from bard.DBus import DBusThread
from bard.Module import ModuleManager, Module
from bard.Model import Type, DataStore, Position
from bard.Constants import SPACE

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', action='store', nargs=1, metavar='config.ini',
                        help='config file to use to run the bar')
    args = parser.parse_args()

    return args

def event_loop(c, queue, p, mm):
    left_pad = c.lemonbar.padding_left
    right_pad = c.lemonbar.padding_right
    # set div colour
    div = Utilities.wrap_in_f_colour(c.lemonbar.divider, c.lemonbar.font_color)
    data = { t : DataStore(t, pos=m.position, priority=m.priority) for t, m in mm.modules.items() }

    lemonbarpos = {
        Position.RIGHT : '%{r}',
        Position.LEFT : '%{l}',
        Position.CENTER : '%{c}',
        None : '',
    }

    while d := queue.get():
        if d.id == Type.STOP:
            p.terminate()
            break

        data[d.id] = d

        # data[d.id].data = d.data
        # data[d.id].priority = d.priority
        # data[d.id].pos = d.pos

        # print(data)

        # quite epic
        # create a dict of position to a list of ids
        # eg. {
        #       <Position.LEFT: 3>: ['com.yeet.bard.Desktop'],
        #       <Position.RIGHT: 1>: ['com.yeet.bard.Time', 'com.yeet.bard.Weather']
        # }
        v = {}
        for key, value in data.items():
            v.setdefault(value.pos, []).append(data[key])

        # print(v)
        # continue
        # the idea is to force only a singular %{r}
        # formatting tag on each side of things
        # for that location
        s = []
        for pos, lis in v.items():
            position = lemonbarpos[pos]
            s.append(position)
            for i, k in enumerate(sorted(lis, key=lambda val: val.priority)):
                s.append(Utilities.add_padding(data[k.id].data, int(left_pad), int(right_pad)))
                if i != len(lis) - 1:
                    s.append(div)
            s.append(position)

        s = ''.join(s).encode()
        # print(s)
        p.stdin.write(s)
        p.stdin.flush()
        queue.task_done()

def main():
    args = run_argparse()
    c = cf.parse(args.config)
    queue = Queue()
    mm = ModuleManager(queue)
    md.load_modules(c, mm, queue)
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

    try:
        event_loop(c, queue, p, mm)
    except KeyboardInterrupt as kb:
        print('Signal received, exitting')

if __name__ == '__main__':
    main()
