from enum import Enum, auto

class Position(Enum):
    RIGHT = auto()
    CENTER = auto()
    LEFT = auto()

class Type(Enum):
    STOP = auto()

class DataStore():
    def __init__(self, id, data='', pos=None, priority=0):
        self.id = id
        self.data = str(data)
        self.pos = pos
        self.priority = priority
