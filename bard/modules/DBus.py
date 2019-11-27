import time
from datetime import datetime
from pydbus import SessionBus
from gi.repository import GLib
from .Model import DataStore, Type
from .InfoThread import InfoThread

START_TIME=time.time()

class DBus(object):
    def __init__(self, q, thread):
        super().__init__()
        self._q = q
        self._thread = thread

    def refresh(self):
        self._thread.put_new()
        self._q.put(DataStore(Type.DBUS))

    def load(self):
        self._thread.load()
        self._thread.put_new()
        self._q.put(DataStore(Type.DBUS))

    def unload(self):
        self._thread.unload()
        self._thread.put_new()
        self._q.put(DataStore(Type.DBUS))

class DBusBattery(DBus):
    """
    <node>
        <interface name='com.yeet.bard.Battery'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, thread):
        super().__init__(q, thread)

class DBusWeather(DBus):
    """
    <node>
        <interface name='com.yeet.bard.Weather'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, thread):
        super().__init__(q, thread)

class DBusDesktop(DBus):
    """
    <node>
        <interface name='com.yeet.bard.Desktop'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, thread):
        super().__init__(q, thread)

class DBusTime(DBus):
    """
    <node>
        <interface name='com.yeet.bard.Time'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, thread):
        super().__init__(q, thread)

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
        self._q.put(DataStore(Type.DBUS, 'stop'))

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

    def put_new(self):
        return super().put_new()

    def run(self):
        self._bus.publish('com.yeet.bard', DBusManager(self.queue, self._loop, self._threads))
        self._bus.publish('com.yeet.bard.Weather', DBusWeather(self.queue, self._threads[Type.WEATHER]))
        self._bus.publish('com.yeet.bard.Desktop', DBusDesktop(self.queue, self._threads[Type.DESKTOP]))
        self._bus.publish('com.yeet.bard.Time', DBusTime(self.queue, self._threads[Type.TIME]))
        self._bus.publish('com.yeet.bard.Battery', DBusBattery(self.queue, self._threads[Type.BATTERY]))
        self._loop.run()
