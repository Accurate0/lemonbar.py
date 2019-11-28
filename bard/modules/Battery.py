import time

import pyudev

from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

NAME = 'com.yeet.bard.Battery'
CLASSNAME = 'BatteryThread'

BATTERY_PATH = '/sys/class/power_supply/BAT0'
BAT_FULL = BATTERY_PATH + '/charge_full_design'
BAT_NOW = BATTERY_PATH + '/charge_now'
BAT_STATUS = BATTERY_PATH + '/status'

class BatteryThread(Module):
    """
    <node>
        <interface name='com.yeet.bard.Battery'>
            <method name='refresh'/>
            <method name='load'/>
            <method name='unload'/>
        </interface>
    </node>
    """
    def __init__(self, q, conf):
        super().__init__(q, NAME)
        self.font_col = conf.lemonbar.font_color
        self.put_new()

    @property
    def position(self):
        return Position.RIGHT

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
            s = ' %{{F{color}}}{status}, {percent}%%{{F}}'.format(color=self.font_col,
                                                                    status=status,
                                                                    percent=percent)
        else:
            s = ''
        # print(s)
        self._queue.put(DataStore(self.name, s, self.position))

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
