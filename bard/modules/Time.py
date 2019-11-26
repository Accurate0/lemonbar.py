from .Model import DataStore, Type
from .InfoThread import InfoThread
from datetime import datetime

class TimeThread(InfoThread):
    def __init__(self, q, font_col):
        super().__init__(q, 'Time')
        self.font_col = font_col

    def put_new(self):
        super().put_new()
        t = datetime.now().strftime('%e %B, %I:%M %p')
        t = '%{{F{color}}}{time}  %{{F}}'.format(time=t, color=self.font_col)
        t = t if self._loaded else ''
        self.queue.put(DataStore(Type.TIME, t))

    def run(self):
        while not self._stopping.is_set():
            self.put_new()
            self._stopping.wait(5)
