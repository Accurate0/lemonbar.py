from datetime import datetime
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

NAME = 'com.yeet.bard.Time'
CLASSNAME = 'TimeThread'

class TimeThread(Module):
    """
    <node>
        <interface name='com.yeet.bard.Time'>
            <method name='refresh'/>
        </interface>
    </node>
    """
    def __init__(self, q, conf):
        super().__init__(q, NAME)
        self.font_col = conf.lemonbar.font_color

    @property
    def position(self):
        return Position.RIGHT

    def refresh(self):
        self.put_new()

    def put_new(self):
        super().put_new()
        t = datetime.now().strftime('%e %B, %I:%M %p')
        t = ' %{{F{color}}}{time}%{{F}}'.format(time=t, color=self.font_col)
        self._queue.put(DataStore(self.name, t, self.position))

    def run(self):
        while not self._stopping.is_set():
            self._stopping.wait(5)
            self.put_new()
