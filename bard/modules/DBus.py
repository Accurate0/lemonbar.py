import time
from datetime import datetime
from pydbus import SessionBus
from gi.repository import GLib
from .Model import DataStore, Type
from .InfoThread import InfoThread

START_TIME=time.time()

class DBusWeather(object):
    """
    <node>
        <interface name='com.yeet.bard.Weather'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, thread):
        super().__init__()
        self._thread = thread

    def refresh(self):
        self._thread.put_new()

    def load(self):
        self._thread.load()
        self._thread.put_new()

    def unload(self):
        self._thread.unload()
        self._thread.put_new()

class DBusDesktop(object):
    """
    <node>
        <interface name='com.yeet.bard.Desktop'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, thread):
        super().__init__()
        self._thread = thread

    def refresh(self):
        self._thread.put_new()

    def load(self):
        self._thread.load()
        self._thread.put_new()

    def unload(self):
        self._thread.unload()
        self._thread.put_new()

class DBusTime(object):
    """
    <node>
        <interface name='com.yeet.bard.Time'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, thread):
        super().__init__()
        self._thread = thread

    def refresh(self):
        self._thread.put_new()

    def load(self):
        self._thread.load()
        self._thread.put_new()

    def unload(self):
        self._thread.unload()
        self._thread.put_new()

class DBusManager(object):
    """
    <node>
        <interface name='com.yeet.bard.Manager'>
            <method name='refresh'/>
            <method name='stop'/>
            <method name='status'>
                <arg type='s' name='response' direction='out'/>
            </method>
        </interface>
    </node>
    """
    def __init__(self, q, l, t):
        super().__init__()
        self._q = q
        self._l = l
        self._t = t

    def refresh(self):
        for _, thread in self._t.items():
            thread.put_new()

    def stop(self):
        self._l.quit()
        self._q.put(DataStore(Type.STOP))

    def status(self):
        t = datetime.utcfromtimestamp(
                            time.time() - START_TIME
                        ).strftime('%H:%M:%S:%f')

        s = ['Loaded Modules: \n']
        for _, thread in self._t.items():
            s.append(f'   {thread.name.ljust(8)} : {thread.is_loaded()}\n')

        s.append(f'Running Time: {t}')

        return ''.join(s)

class DBusThread(InfoThread):
    def __init__(self, q, threads):
        super().__init__(q, 'DBus')
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()
        self._threads = threads

    def run(self):
        self._bus.publish('com.yeet.bard', DBusManager(self.queue, self._loop, self._threads))
        self._bus.publish('com.yeet.bard.Weather', DBusWeather(self._threads[Type.WEATHER]))
        self._bus.publish('com.yeet.bard.Desktop', DBusDesktop(self._threads[Type.DESKTOP]))
        self._bus.publish('com.yeet.bard.Time', DBusTime(self._threads[Type.TIME]))
        self._loop.run()
