import Xlib
import Xlib.X
import asyncio

from .Model import DataStore, Type
from .InfoThread import InfoThread

from Xlib.display import Display, X
from ewmh.ewmh import EWMH

DESKTOPS = [
                '%{{F{da}}}firefox%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{di}}}dota2%{{F}}',
                '%{{F{di}}}firefox%{{F}}    %{{F{da}}}discord%{{F}}    %{{F{di}}}dota2%{{F}}',
                '%{{F{di}}}firefox%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{da}}}dota2%{{F}}'
           ]


class DesktopThread(InfoThread):
    def __init__(self, q, e, x, di, da):
        super().__init__(q)
        self.ewmh = e
        self.x = x
        self.desk_inactive = di
        self.desk_active = da

        x.screen().root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def run(self):
        while not self._stopping.is_set() and self.x.next_event():
            self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def current_desktop(self):
        d = self.ewmh.getCurrentDesktop()
        return f'   {DESKTOPS[d].format(di=self.desk_inactive, da=self.desk_active)}'