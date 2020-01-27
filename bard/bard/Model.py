from enum import Enum, auto

class Position(Enum):
    RIGHT = auto()
    CENTER = auto()
    LEFT = auto()

class Type(Enum):
    CALLBACK = auto()
    DISPLAY = auto()
    STOP = auto()

class DataStore():
    def __init__(self, id, data='', pos=None, priority=0, type=Type.DISPLAY):
        self.id = id
        self.data = str(data)
        self.pos = pos
        self.priority = priority
        self.type = type

    def __str__(self):
        return f'{self.id} : {self.type} : {self.data}'
