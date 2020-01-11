import time

from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

NAME = 'Example'
CLASSNAME = 'ExampleThread'

class ExampleThread(Module):
    """
    <node>
        <interface name='com.yeet.bard.Example'>
            <method name='refresh'/>
        </interface>
    </node>
    """
    def __init__(self, q, conf):
        super().__init__(q)

    @property
    def position(self):
        return Position.RIGHT

    def refresh(self):
        self.put_new()

    def put_new(self):
        super().put_new()
        self._queue.put(DataStore(self.name))

    def run(self):
        while True:
            self.put_new()
            time.sleep(10)
