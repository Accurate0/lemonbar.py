import time
import logging
from threading import Thread
from datetime import datetime
from pydbus import SessionBus
from gi.repository import GLib

import bard.ModuleLoader as md
from bard.Model import DataStore, Type

START_TIME=time.time()
logger = logging.getLogger(__name__)

class DBusManager(object):
    """
    <node>
        <interface name='com.yeet.bard.Manager'>
            <method name='refresh'/>
            <method name='stop'/>
            <method name='status'>
                <arg type='s' name='response' direction='out'/>
            </method>
            <method name='list_mod'>
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
    def __init__(self, q, l, mm, c, bus, pub):
        super().__init__()
        self._q = q
        self._l = l
        self._mm = mm
        self._published_map = pub
        self._c = c
        self._bus = bus

    def add(self, t, module):
        pub = self._bus.publish(module.name, module)
        self._published_map[t] = pub

    def remove(self, t):
        self._published_map[t].unpublish()
        del self._published_map[t]

    def load(self, name):
        m = md.load_module(name, self._c, self._mm, self._q)
        if m:
            name = m.name
            self.add(name, m)
            logger.info(f'loaded module {name} id={m.native_id}')

    def unload(self, name):
        self.remove(name)
        self._mm.remove(name)
        logger.info(f'unloaded module {name}')

    def refresh(self):
        l = ', '.join(list(self._mm.modules.keys()))
        logger.info(f'refreshing {l}')
        for _, module in self._mm.modules.items():
            module.refresh()

    def stop(self):
        logger.info('stop message received over dbus')
        for _, module in self._mm.modules.items():
            module.join(1)
        self._q.put(DataStore('', type=Type.STOP))
        self._l.quit()

    def list_mod(self):
        s = []
        for _, module in self._mm.modules.items():
            s.append(f'{module.name}\n')
        return ''.join(s)

    def status(self):
        t = datetime.utcfromtimestamp(
                            time.time() - START_TIME
                        ).strftime('%H:%M:%S:%f')

        s = ['Loaded Modules: \n']
        for _, module in self._mm.modules.items():
            s.append(f'   {module.name.ljust(8)}\n')

        s.append(f'Running Time: {t}\n')
        return ''.join(s)

class DBusThread(Thread):
    def __init__(self, q, mm, c):
        super().__init__(name='DBus')
        self._queue = q
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()
        self._mm = mm
        self._c = c

    def run(self):
        pub = {}
        for t, module in self._mm.modules.items():
            try:
                pub[t] = self._bus.publish(module.name, (module))
            except GLib.Error as e:
                logger.error(f'error publishing {t} because {e}')
                logger.error('dbus string is likely empty, this can be safely ignored')

        self._bus.publish(self._c.dbus.prefix, DBusManager(self._queue,
                                                       self._loop,
                                                       self._mm,
                                                       self._c,
                                                       self._bus,
                                                       pub))
        self._loop.run()
