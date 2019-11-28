import time
from threading import Thread
from datetime import datetime
from pydbus import SessionBus
from gi.repository import GLib
from .Model import DataStore, Type
from .ModuleLoader import ModuleLoader

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
            <method name='load'>
                <arg type='s' name='name' direction='in' />
            </method>
            <method name='unload'>
                <arg type='s' name='name' direction='in' />
            </method>
        </interface>
    </node>
    """
    def __init__(self, q, l, mm, c):
        super().__init__()
        self._q = q
        self._l = l
        self._mm = mm
        self._published_map = {}
        self._c = c

        for t, module in self._mm.modules.items():
            self._published_map[t] = module

    def add(self, t, module):
        self._bus.publish(module.name, module)
        self._published_map[t] = module

    def remove(self, t):
        self._published_map[t].unpublish()
        del self._published_map[t]

    def load(self, name):
        m, name = ModuleLoader.load_module(name, self._c, self._mm, self._q)
        self.add(name, m)

    def unload(self, name):
        # testing
        self._mm.remove(name)
        self.remove(name)

    def refresh(self):
        for _, module in self._mm.modules.items():
            module.put_new()

    def stop(self):
        self._l.quit()

    def status(self):
        t = datetime.utcfromtimestamp(
                            time.time() - START_TIME
                        ).strftime('%H:%M:%S:%f')

        s = ['Loaded Modules: \n']
        for _, module in self._mm.modules.items():
            s.append(f'   {module.name.ljust(8)} : {module.is_loaded()}\n')

        s.append(f'Running Time: {t}')

        return ''.join(s)

class DBusThread(Thread):
    def __init__(self, q, mm, c):
        super().__init__()
        self._queue = q
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()
        self._mm = mm
        self._c = c

    def run(self):
        self._bus.publish('com.yeet.bard', DBusManager(self._queue, self._loop, self._mm, self._c))
        for _, module in self._mm.modules.items():
            # print(module.name)
            self._bus.publish(module.name, module)

        self._loop.run()
