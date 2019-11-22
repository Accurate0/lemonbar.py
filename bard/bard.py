#!/usr/bin/env python3
import sys
import time

from modules.Model import Type
from modules.Time import TimeThread
from modules.Model import DataStore
from modules.InfoThread import InfoThread
from modules.Desktop import DesktopThread
from modules.Weather import WeatherThread
from modules.DBus import DBusThread
from modules.Constants import LEMONBAR_CMD, DIVIDER

from Xlib.display import Display
from ewmh.ewmh import EWMH
from queue import Queue
from signal import signal, SIGINT, SIGTERM
from subprocess import Popen, PIPE, DEVNULL

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
