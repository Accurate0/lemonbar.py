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
    data = { t:('', m.position, m.priority) for t, m in mm.modules.items() }

    lemonbarpos = {
        Position.RIGHT : '%{r}',
        Position.LEFT : '%{l}',
        Position.CENTER : '%{c}',
        None : '',
    }

    # print(data)

    while d := queue.get():
        if d.id == Type.STOP:
            p.terminate()
            break

        data[d.id] = (d.data, d.pos, d.priority)

        # quite epic
        # create a dict of position to a list of ids
        # eg. {
        #       <Position.LEFT: 3>: ['com.yeet.bard.Desktop'],
        #       <Position.RIGHT: 1>: ['com.yeet.bard.Time', 'com.yeet.bard.Weather']
        # }
        v = {}
        for key, value in sorted(data.items()):
            v.setdefault(value[1], []).append((key, value[2]))

        # the idea is to force only a singular %{r}
        # formatting tag on each side of things
        # for that location
        s = []
        for pos, lis in v.items():
            position = lemonbarpos[pos]
            s.append(position)
            for i, k in enumerate(sorted(lis, key=lambda tup: tup[1])):
                s.append(Utilities.add_padding(data[k[0]][0], int(left_pad), int(right_pad)))
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

    event_loop(c, queue, p, mm)

if __name__ == '__main__':
    main()
