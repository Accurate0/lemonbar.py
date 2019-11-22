import Xlib
import Xlib.X

from .Model import DataStore, Type
from .InfoThread import InfoThread
from .Constants import DESKTOPS, DESKTOP_ACTIVE, DESKTOP_INACTIVE
from Xlib.display import Display, X
from ewmh.ewmh import EWMH

class DesktopThread(InfoThread):
    def __init__(self, q, e, x):
        super().__init__(q)
        self.ewmh = e
        self.x = x

        x.screen().root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def run(self):
        while not self._stopping.is_set() and self.x.next_event():
            self.queue.put(DataStore(Type.DESKTOP, self.current_desktop()))

    def current_desktop(self):
        d = self.ewmh.getCurrentDesktop()
        return '   {}'.format(DESKTOPS[d].format(active=DESKTOP_ACTIVE, inactive=DESKTOP_INACTIVE))
