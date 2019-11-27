import time

import pyudev

from .InfoThread import InfoThread
from .Model import DataStore, Type

BATTERY_PATH = '/sys/class/power_supply/BAT0'
BAT_FULL = BATTERY_PATH + '/charge_full_design'
BAT_NOW = BATTERY_PATH + '/charge_now'
BAT_STATUS = BATTERY_PATH + '/status'

class BatteryThread(InfoThread):
    def __init__(self, q, font_col):
        super().__init__(q, 'Battery')
        self.font_col = font_col
        self.put_new()

    @staticmethod
    def read_with_except(file, default):
        ret = default
        try:
            with open(file) as f:
                ret = f.readline()
        except FileNotFoundError as e:
            print(e)
        return ret

    def put_new(self):
        super().put_new()
        if self._loaded:
            status = self.read_with_except(BAT_STATUS, 'Power Supply')
            full = self.read_with_except(BAT_FULL, '1')
            now = self.read_with_except(BAT_NOW, '1')

            status = status.rstrip()
            full = int(full)
            now = int(now)

            percent = int((now / full) * 100)
            s = ' %{{F{color}}}{status}, {percent}%%{{F}} '.format(color=self.font_col,
                                                                    status=status,
                                                                    percent=percent)
        else:
            s = ''
        # print(s)
        self.queue.put(DataStore(Type.BATTERY, s))

    def run(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('power_supply')

        # my laptop battery doesn't send events on percentage change
        # thats annoying, something to deal with later though
        for device in iter(monitor.poll, None):
            time.sleep(3)
            self.put_new()
            # print(device)
