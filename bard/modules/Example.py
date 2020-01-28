import time
import logging

# Optional Utilities
from bard import Utilities
# Required imports
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

# Filename without the .py ext
# is used as the name of the module
# Config header of the same
# name will be passed as a dict
# Filename must also match name of the class that extends Module

# Logging is optional but recommended for errors
# Use debug level for excessive logging
logger = logging.getLogger(__name__)

class Example(Module):
    # DBus XML, no methods are required but refresh
    # is fairly standard
    dbus = '<node> \
                <interface name=\'{name}\'> \
                    <method name=\'refresh\'/> \
                </interface> \
            </node>'

    def __init__(self, q, conf, name):
        """
        Setup the class, initialise anything needed,
        read required config
        """
        super().__init__(q, conf, name)

    def callback(self, iterable):
        """
        Called by the MainThread for click options,
        iterable is a list of strings.
        The input command must be a CSV format, with the first
        value representing the module name to contact,
        and the rest is passed as a string split on ','
        """
        pass

    @property
    def position(self):
        """
        Right, Centre or Left, refers to lemonbar positioning
        """
        return Position.RIGHT

    @property
    def priority(self):
        """
        Higher priority means closer to the left
        """
        return 0

    def refresh(self):
        """
        This method must put something into the queue
        """
        super().refresh()
        self._queue.put(DataStore(self.name))

    def run(self):
        """
        The loop to run in the background, might be time based,
        or otherwise blocking
        """
        while True:
            self.refresh()
            logger.info('Might log something to the file in /tmp/bard.log')
            time.sleep(10)
