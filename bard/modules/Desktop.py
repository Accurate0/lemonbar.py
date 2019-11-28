import Xlib
import Xlib.X
import asyncio

from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

from Xlib.display import Display, X
from ewmh.ewmh import EWMH

NAME = 'com.yeet.bard.Desktop'
CLASSNAME = 'DesktopThread'

DESKTOPS = [
                '%{{F{da}}}firefox%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{di}}}dota2%{{F}}',
                '%{{F{di}}}firefox%{{F}}    %{{F{da}}}discord%{{F}}    %{{F{di}}}dota2%{{F}}',
                '%{{F{di}}}firefox%{{F}}    %{{F{di}}}discord%{{F}}    %{{F{da}}}dota2%{{F}}'
           ]

class DesktopThread(Module):
    """
    <node>
        <interface name='com.yeet.bard.Desktop'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, conf):
        super().__init__(q, NAME)
        self.ewmh = EWMH()
        self.x = Display()
        self.desk_inactive = conf.lemonbar.desktop_inactive_color
        self.desk_active = conf.lemonbar.desktop_active_color

        self.x.screen().root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self.put_new()

    @property
    def position(self):
        return Position.LEFT

    def put_new(self):
        super().put_new()
        self._queue.put(DataStore(self.name, self.current_desktop(), self.position))

    def run(self):
        while not self._stopping.is_set() and self.x.next_event():
            self.put_new()

    def current_desktop(self):
        if self._loaded:
            d = self.ewmh.getCurrentDesktop()
            s = DESKTOPS[d].format(di=self.desk_inactive, da=self.desk_active)
        else:
            s = ''

        return s
