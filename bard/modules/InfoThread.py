from threading import Thread, Event
from .Model import DataStore, Type

class InfoThread(Thread):
    def __init__(self, q, name):
        super().__init__()
        self.name = name
        self.queue = q
        self._stopping = Event()
        self._loaded = True

    def put_new(self):
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
