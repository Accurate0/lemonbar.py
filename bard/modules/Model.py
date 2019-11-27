from enum import Enum, auto

class Type(Enum):
    DESKTOP = auto()
    TIME = auto()
    WEATHER = auto()
    DBUS = auto()
    BATTERY = auto()

class DataStore():
    def __init__(self, id, data=None):
        self.id = id
        self.data = str(data)
