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

import bard.Config as cf
import bard.ModuleLoader as md

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
    parser.add_argument('config', action='store', nargs=1, metavar='config.ini',
                        help='config file to use to run the bar')
    parser.add_argument('--log', action='store', nargs='?', metavar='level',
                        help='possible levels: debug, info, warning, error, critical',
                        default='INFO')
    args = parser.parse_args()

    return args

def event_loop(c, queue, p, mm):
    left_pad = int(c.lemonbar.padding_left)
    right_pad = int(c.lemonbar.padding_right)
    # set div to color
    div = Utilities.f_colour(c.lemonbar.divider, c.lemonbar.font_color)
    data = { t : DataStore(t, pos=m.position, priority=m.priority) for t, m in mm.modules.items() }

    lemonbarpos = {
        Position.RIGHT : '%{r}',
        Position.LEFT : '%{l}',
        Position.CENTER : '%{c}',
        None : '',
    }

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

        s = []
        for pos, lis in v.items():
            position = lemonbarpos[pos]
            s.append(position)
            for i, k in enumerate(sorted(lis, key=lambda val: val.priority)):
                s.append(Utilities.add_padding(data[k.id].data, left_pad, right_pad))
                if i != len(lis) - 1:
                    s.append(div)
            s.append(position)

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
        filename='/tmp/bard.log'
    )

    c = cf.parse(args.config)
    queue = Queue()
    mm = ModuleManager(queue)

    mod_thread = threading.Thread(target=md.load_modules, args=[c, mm, queue])
    mod_thread.start()

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

    p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
    essential_threads = {
                            'dbus'     : DBusThread(queue, mm, c),
                            'callback' : CallbackThread(queue, mm, c, p)
                        }

    mod_thread.join()

    for _, thread in essential_threads.items():
        thread.daemon = True
        thread.start()

    # dbus = essential_threads['dbus']
    # cb = essential_threads['callback']
    # logger.critical('-'*17 + ' Log Start ' + '-'*17)
    # logger.info('logger configured, starting..')
    # logger.info('main'.ljust(18) + f'id={os.getpid()}')
    # logger.info('lemonbar running'.ljust(18) + f'id={p.pid}')
    # logger.info('dbus loaded'.ljust(18) + f'id={dbus.native_id}')
    # logger.info('callback loaded'.ljust(18) + f'id={cb.native_id}')
    # logger.info('loaded modules:')
    # for name, mod in mm.modules.items():
    #     logger.info(f'\t\t{name.ljust(25)} id={mod.native_id}')
    # logger.info('loaded config')
    # c.log()

    try:
        event_loop(c, queue, p, mm)
    except KeyboardInterrupt as kb:
        logger.warning('Signal received, exitting')

if __name__ == '__main__':
    main()
