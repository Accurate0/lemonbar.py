from abc import ABC, abstractclassmethod, abstractproperty

from threading import Thread, Event
from .Model import DataStore, Type
from .DBus import DBus

class ModuleManager():
    def __init__(self, queue):
        super().__init__()
        self._modules = {}
        self._queue = queue

    def add(self, t, module):
        self._modules[t] = module
        self._modules[t].start()

    def remove(self, t):
        # also stop the thread
        self._modules[t].join()
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

    def load(self):
        self._loaded = True

    def unload(self):
        self._loaded = False

    def is_loaded(self):
        return self._loaded

    def refresh(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass

    def join(self, timeout=None):
        self._stopping.set()
        super().join(timeout)

class InfoThread(Thread, ABC):
    def __init__(self, q, name):
        super().__init__()
        self.name = name
        self.queue = q
        self._stopping = Event()
        self._loaded = True

    @abstractclassmethod
    def put_new(cls):
        pass

    def is_loaded(self):
        return self._loaded

    def load(self):
        self._loaded = True

    def unload(self):
        self._loaded = False

    def join(self, timeout=None):
        self.queue.put(DataStore(Type.STOP))
        self._stopping.set()
        # super(InfoThread, self).join(timeout)
