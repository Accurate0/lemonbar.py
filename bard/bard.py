#!/usr/bin/env python3
import os
import sys
import time
import types
import logging
import argparse
import textwrap
import threading

from queue import Queue
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

import bard.ModuleLoader as md

from bard import Config
from bard import Utilities
from bard.DBus import DBusThread
from bard.Logger import DuplicateFilter
from bard.Callback import CallbackThread
from bard.Module import ModuleManager, Module
from bard.Model import Type, DataStore, Position

# TODO: Create a callback thread to read from lemonbar stdout
# TODO: Increase DBUS capabilities
# TODO: Better commenting

logger = logging.getLogger(__name__)

def run_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', action='store', nargs='?', metavar='config.ini',
                        help='config file to use to run the bar', default='config.ini')
    parser.add_argument('--log', action='store', nargs='?', metavar='level',
                        help='possible levels: debug, info, warning, error, critical',
                        default='INFO', const='INFO')
    parser.add_argument('--disable-dbus', action='store_true',
                        help='disable exposing interface over dbus',
                        default=False)
    parser.add_argument('--disable-clickable', action='store_true',
                        help='make the bar ignore mouse actions',
                        default=False)
    args = parser.parse_args()

    return args

def construct_string(c, v, data):
    lemonbarpos = {
        Position.RIGHT : '%{r}',
        Position.LEFT : '%{l}',
        Position.CENTER : '%{c}',
        None : '',
    }

    div = Utilities.f_colour(c['Lemonbar']['divider'], c['Lemonbar']['font_color'])
    left_pad = int(c['Lemonbar']['padding_left'])
    right_pad = int(c['Lemonbar']['padding_right'])
    div = Utilities.add_padding(div, left_pad, right_pad)

    s = []
    for pos, lis in v.items():
        position = lemonbarpos[pos]
        s.append(position)
        for i, k in enumerate(sorted(lis, key=lambda val: val.priority)):
            s.append(Utilities.add_padding(data[k.id].data, left_pad, right_pad))
            if i != len(lis) - 1:
                s.append(div)
        s.append(position)

    return s

def event_loop(c, queue, p, mm):
    data = { t : DataStore(
                        t,
                        pos=m.position,
                        priority=m.priority) for t, m in mm.modules.items() }

    while d := queue.get():
        logger.debug(f'updating {d.id.ljust(10)}')
        logger.debug(f'\'{d.data}\'')

        if d.type == Type.STOP:
            return

        if d.type == Type.CALLBACK:
            mm.modules[d.id].callback(d.data)
            continue

        data[d.id] = d

        v = {}
        for key, value in data.items():
            v.setdefault(value.pos, []).append(data[key])

        s = construct_string(c, v, data)

        s = ''.join(s).encode()
        p.stdin.write(s)
        p.stdin.flush()
        queue.task_done()

def main():
    args = run_argparse()

    logger.addFilter(DuplicateFilter())
    logging.basicConfig(
        format='%(asctime)s %(name)-20s %(threadName)-10s %(levelname)-8s %(message)s',
        datefmt='%d-%m %H:%M:%S',
        level=getattr(logging, args.log.upper()),
        handlers=[logging.StreamHandler(), logging.FileHandler('/tmp/bard.log')]
    )

    c = Config.parse(args.config)
    queue = Queue()
    mm = ModuleManager(queue)

    # load the modules in the background while
    # lemonbar is loaded
    mod_thread = threading.Thread(target=md.load_modules, args=[c, mm, queue])
    mod_thread.start()

    LEMONBAR_CMD = [
                        'lemonbar',
                        '-B', c['Lemonbar']['background_color'],
                        '-o', '-3',
                        '-f', c['Lemonbar']['font_awesome'],
                        '-o', '-1',
                        '-f', c['Lemonbar']['font'],
                        '-g', c['Lemonbar']['geometry'],
                        '-n', __file__
                    ]

    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
    essential_threads = {
                            'dbus'
                                : DBusThread(queue, mm, c)
                                    if not args.disable_dbus else None,
                            'callback'
                                : CallbackThread(queue, mm, c['Callback'], p)
                                    if not args.disable_clickable else None
                        }

    # make sure all modules are loaded
    # this allows the dbus thread
    # publish right away
    mod_thread.join()

    for _, thread in essential_threads.items():
        if thread is not None:
            thread.daemon = True
            thread.start()

    try:
        event_loop(c, queue, p, mm)
    except KeyboardInterrupt as kb:
        logger.warning('Signal received, exitting')
    except BaseException as e:
        logger.critical(f'unexpected error: {e}')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f'unexpected error: {e}')
