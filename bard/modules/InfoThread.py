from threading import Thread, Event
from .Model import DataStore, Type

class InfoThread(Thread):
    def __init__(self, q):
        super().__init__()
        self.queue = q
        self._stopping = Event()

    def join(self, timeout=None):
        self.queue.put(DataStore(Type.STOP))
        self._stopping.set()
        # super(InfoThread, self).join(timeout)
