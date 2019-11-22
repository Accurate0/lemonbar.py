import time
from datetime import datetime
from pydbus import SessionBus
from gi.repository import GLib
from .Model import DataStore, Type
from .InfoThread import InfoThread

START_TIME=time.time()

class DBusDesktop(object):
    pass

class DBusManager(object):
    """
    <node>
        <interface name='com.yeet.bard.Manager'>
            <method name='refresh'>
                <arg type='s' name='response' direction='out'/>
            </method>
            <method name='stop'/>
            <method name='status'>
                <arg type='s' name='response' direction='out'/>
            </method>
        </interface>
    </node>
    """
    def __init__(self, q, l):
        super().__init__()
        self._q = q
        self._l = l

    def refresh(self):
        # self._q.put(DataStore(Type.DBUS, 'stop'))
        return 'success'

    def stop(self):
        self._l.quit()
        self._q.put(DataStore(Type.STOP))

    def status(self):
        return 'running time: {}' \
                .format(
                        datetime.utcfromtimestamp(
                            time.time() - START_TIME
                        ).strftime('%H:%M:%S:%f')
                )

class DBusThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)
        self._loop = GLib.MainLoop()
        self._bus = SessionBus()

    def run(self):
        self._bus.publish('com.yeet.bard', DBusManager(self.queue, self._loop))
        self._loop.run()
