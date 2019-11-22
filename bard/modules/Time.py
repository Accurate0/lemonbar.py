from .Model import DataStore, Type
from .InfoThread import InfoThread
from datetime import datetime
from .Constants import FONT_COLOR

class TimeThread(InfoThread):
    def __init__(self, q):
        super().__init__(q)

    def run(self):
        while not self._stopping.is_set():
            t = datetime.now().strftime('%e %B, %I:%M %p')
            t = '%{{F{color}}}{time}  %{{F}}'.format(time=t, color=FONT_COLOR)
            self.queue.put(DataStore(Type.TIME, t))
            self._stopping.wait(5)
