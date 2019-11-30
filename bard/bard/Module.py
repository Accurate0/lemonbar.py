from abc import ABC, abstractclassmethod, abstractproperty

from threading import Thread, Event
from .Model import DataStore, Type

class ModuleManager():
    def __init__(self, queue):
        super().__init__()
        self._modules = {}
        self._queue = queue

    def add(self, t, module):
        self._modules[t] = module
        self._modules[t].start()
        self._modules[t].put_new()

    def remove(self, t):
        # also stop the thread
        self._modules[t].join()
        # place empty data to update the bar
        self._queue.put(DataStore(t))
        del self._modules[t]

    @property
    def modules(self):
        return self._modules

# Inheriting classes need to define the DBus interface
class Module(Thread, ABC):
    def __init__(self, queue, name):
        super().__init__()
        self._queue = queue
        self.name = name
        self._loaded = True
        self.daemon = True
        self._stopping = Event()

    @abstractclassmethod
    def put_new(cls):
        pass

    @abstractproperty
    def position(cls):
        pass

    @abstractclassmethod
    def refresh(cls):
        pass

    def join(self, timeout=None):
        self._stopping.set()
        super().join(timeout)
