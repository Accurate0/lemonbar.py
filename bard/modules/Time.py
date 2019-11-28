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
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, conf):
        super().__init__(q, NAME)
        self.font_col = conf.lemonbar.font_color

    @property
    def position(self):
        return Position.RIGHT

    def put_new(self):
        super().put_new()
        if self._loaded:
            t = datetime.now().strftime('%e %B, %I:%M %p')
            t = ' %{{F{color}}}{time}  %{{F}}'.format(time=t, color=self.font_col)
        else:
            t = ''
        self._queue.put(DataStore(self.name, t, self.position))

    def run(self):
        while not self._stopping.is_set():
            self.put_new()
            self._stopping.wait(5)
