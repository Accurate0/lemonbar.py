import time
import logging

from bard import Utilities
from bard.Module import Module, ModuleManager
from bard.Model import DataStore, Type, Position

import gi
gi.require_version('Playerctl', '2.0')
from gi.repository import Playerctl, GLib

logger = logging.getLogger(__name__)

class Player(Module):
    dbus = '<node> \
                <interface name=\'{name}\'> \
                    <method name=\'refresh\'/> \
                </interface> \
            </node>'

    def __init__(self, q, conf, name):
        super().__init__(q, conf, name)
        self.font_col = conf['font_color']
        self.player = None
        self.manager = Playerctl.PlayerManager()
        self.string = Utilities.f_colour('No Media Playing', self.font_col)

        def init_player(name):
            self.player = Playerctl.Player.new_from_name(name)
            self.player.connect('playback-status::stopped', self.on_stopped, self.manager)
            self.player.connect('playback-status::playing', self.on_change, self.manager)
            self.player.connect('metadata', self.on_change, self.manager)
            self.manager.manage_player(self.player)

        self.manager.connect('name-appeared', lambda manager, name: init_player(name))

        for name in self.manager.props.player_names:
            init_player(name)

    def on_stopped(self, player, status, manager):
        print(player, status, manager)
        self.string = Utilities.f_colour('No Media Playing', self.font_col)
        self.refresh()

    def on_change(self, player, metadata, manager):
        metadata = player.props.metadata
        if 'xesam:artist' in metadata.keys() and 'xesam:title' in metadata.keys():
            artist = metadata['xesam:artist'][0]
            title = metadata['xesam:title']

            if len(artist) == 0 and len(title) == 0:
                self.string = Utilities.f_colour('No Media Playing', self.font_col)
            else:
                title = (title[:15] + '..') if len(title) > 15 else title
                artist = (artist[:15] + '..') if len(artist) > 15 else artist

                self.string = Utilities.f_colour(f'{title} - {artist}', self.font_col)
        else:
            self.string = Utilities.f_colour('No Media Playing', self.font_col)

        self.refresh()

    def callback(self, iterable):
        pass

    @property
    def position(self):
        return Position.RIGHT

    @property
    def priority(self):
        return 0

    def refresh(self):
        super().refresh()
        self._queue.put(DataStore(self.name, self.string, self.position, self.priority))

    def run(self):
        main = GLib.MainLoop()
        main.run()
