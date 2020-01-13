from datetime import datetime

from bard import Utilities
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

NAME = 'Time'
CLASSNAME = 'TimeThread'

class TimeThread(Module):
    dbus = '<node> \
                <interface name=\'{name}\'> \
                    <method name=\'refresh\'/> \
                </interface> \
            </node>'

    def __init__(self, q, conf, name):
        super().__init__(q, conf, name)
        self.font_col = conf.lemonbar.font_color
        self.time_format = conf.time.format

    @property
    def priority(self):
        return 1

    @property
    def position(self):
        return Position.RIGHT

    def refresh(self):
        self.put_new()

    def put_new(self):
        super().put_new()
        t = datetime.now().strftime(self.time_format)
        t = Utilities.wrap_in_f_colour(t, self.font_col)
        self._queue.put(DataStore(self.name, t, self.position, self.priority))

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(5)
            self.put_new()
