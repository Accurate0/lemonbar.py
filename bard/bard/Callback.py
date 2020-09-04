from threading import Thread
from bard.Model import DataStore, Type

class CallbackThread(Thread):
    def __init__(self, q, mm, c, p):
        super().__init__(name='Callback', daemon=True)
        self._queue = q
        self._mm = mm
        self._c = c
        self._p = p

    def run(self):
        for line in self._p.stdout:
            line = line.decode().split(',')
            d = [ l.rstrip() for l in line[1:] ]
            data = DataStore(line[0], data=d)
            data.type = Type.CALLBACK
            self._queue.put(data)
