#!/usr/bin/env python3
import time
import Xlib
import Xlib.X

from queue import Queue
from ewmh.ewmh import EWMH
from enum import Enum, auto
from pydbus import SessionBus
from datetime import datetime
from gi.repository import GLib
from threading import Thread, Event
from Xlib.display import Display, X
from subprocess import Popen, PIPE, DEVNULL

DESKTOP_INACTIVE = '#707880'
DESKTOP_ACTIVE = '#d25050'
CLOCK = '#8f9ba8'
BACKGROUND = '#282a2e'
FONT_AWESOME = 'Font Awesome 5 Free:style=Solid:size=10'
MAIN_FONT = 'Roboto:style=Medium:size=11'
GEOMETRY = '1920x32'
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

class Type(Enum):
    DESKTOP = auto()
    TIME = auto()

class DataStore():
    def __init__(self, id, data):
        self.id = id
        self.data = str(data)

class InfoThread(Thread):
    def __init__(self, q):
        super().__init__()
        self.queue = q
        self._stopping = Event()

    def stop(self):
        self._stopping.set()

    def stopped(self):
        return self._stopping.is_set()

class TimeThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)

    def run(self):
        while True:
            if self.stopped(): return
            t = datetime.now().strftime('%e %B, %I:%M %p')
            t = '%{{F{color}}}{time}  %{{F}}'.format(time=t, color=CLOCK)
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
        while self.x.next_event():
            if self.stopped(): return
            self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def current_desktop(self):
        d = self.ewmh.getCurrentDesktop()
        return '   {}'.format(DESKTOPS[d].format(active=DESKTOP_ACTIVE, inactive=DESKTOP_INACTIVE))

class DBusCommunication(object):
    """
    <node>
        <interface name='com.yeet.bard'>
            <method name='lmao'>
                <arg type='s' name='response' direction='out'/>
            </method>
        </interface>
    </node>
    """
    def lmao(self):
        print('hello')
        return 'hello'

class DBusThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()

    def run(self):
        self._bus.publish('com.yeet.bard', DBusCommunication())
        self._loop.run()

def main():
    try:
        queue = Queue()
        p = Popen(LEMONBAR_CMD, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)
        workers = [
            DesktopThread(queue, EWMH(), Display()),
            TimeThread(queue),
            DBusThread(queue)
        ]

        for worker in workers:
            worker.daemon = True
            worker.start()

        desk = b''
        time = b''

        while True:
            d = queue.get()

            if d.id == Type.DESKTOP:
                desk = d.data
            elif d.id == Type.TIME:
                time = d.data

            p.stdin.write('%{{l}}{desktop}%{{l}}%{{r}}{time}%{{r}}'
                                                        .format(desktop=desk, time=time)
                                                        .encode())
            p.stdin.flush()
            queue.task_done()

    except KeyboardInterrupt as k:
        p.terminate()
        for worker in workers:
            worker.stop()
            worker.join()

if __name__ == '__main__':
    main()
