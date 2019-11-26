from .Model import DataStore, Type
from .InfoThread import InfoThread
from datetime import datetime

class TimeThread(InfoThread):
    def __init__(self, q, font_col):
        super().__init__(q)
        self.font_col = font_col

    def run(self):
        while not self._stopping.is_set():
            t = datetime.now().strftime('%e %B, %I:%M %p')
            t = '%{{F{color}}}{time}  %{{F}}'.format(time=t, color=self.font_col)
            self.queue.put(DataStore(Type.TIME, t))
            self._stopping.wait(5)
