import Xlib
import Xlib.X
import asyncio

from bard import Utilities
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position
from bard.Constants import SPACE

from Xlib.display import Display, X
from ewmh.ewmh import EWMH

DESKTOPS = [
                '%{{F{da}}}chrome%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{di}}}spotify%{{F}}',
                '%{{F{di}}}chrome%{{F}}    %{{F{da}}}discord%{{F}}    %{{F{di}}}spotify%{{F}}',
                '%{{F{di}}}chrome%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{da}}}spotify%{{F}}'
           ]

class Desktop(Module):
    dbus = '<node> \
                <interface name=\'{name}\'> \
                    <method name=\'refresh\'/> \
                </interface> \
            </node>'

    def __init__(self, q, conf, name):
        super().__init__(q, conf, name)
        self.ewmh = EWMH()
        self.x = Display()
        self.desk_inactive = conf['desktop_inactive_color']
        self.desk_active = conf['desktop_active_color']
        self.conf = conf
        self.x.screen().root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

    def callback(self, iterable):
        pass

    @property
    def position(self):
        return Position.LEFT

    @property
    def priority(self):
        return 0

    def refresh(self):
        super().refresh()
        self._queue.put(DataStore(self.name, self.current_desktop(), self.position, self.priority))

    def run(self):
        while not self._stopping.is_set() and self.x.next_event():
            self.refresh()

    def current_desktop(self):
        d = self.ewmh.getCurrentDesktop()
        s = DESKTOPS[d].format(di=self.desk_inactive, da=self.desk_active)

        return Utilities.add_padding(s, int(self.conf['padding_left']), int(self.conf['padding_right']))
