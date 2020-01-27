from abc import ABC, abstractclassmethod, abstractproperty, abstractmethod

from threading import Thread, Event
from .Model import DataStore, Type
from .Config import Config as c

class ModuleManager():
    def __init__(self, queue):
        super().__init__()
        self._modules = {}
        self._queue = queue

    def add(self, t, module):
        self._modules[t] = module
        self._modules[t].start()
        self._modules[t].refresh()

    def remove(self, t):
        # also stop the thread
        self._modules[t].join(1)
        # place empty data to update the bar
        self._queue.put(DataStore(t))
        del self._modules[t]

    @property
    def modules(self):
        return self._modules

# Inheriting classes need to define the DBus interface
class Module(Thread, ABC):
    def __init__(self, queue, conf, name):
        # edit docstring to add prefix+name
        super().__init__(name=name)
        self._queue = queue
        self.name = name
        self._loaded = True
        self.daemon = True
        self._stopping = Event()
        type(self).dbus = type(self).dbus.format(name=name)

    @abstractmethod
    def callback(self, iterable):
        pass

    @abstractproperty
    def priority(self):
        pass

    @abstractproperty
    def position(self):
        pass

    @abstractmethod
    def refresh(self):
        pass

    def join(self, timeout=None):
        self._stopping.set()
        super().join(timeout)
