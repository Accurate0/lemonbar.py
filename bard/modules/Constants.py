DESKTOP_INACTIVE = '#8f9ba8'
DESKTOP_ACTIVE = '#d25050'
FONT_COLOR = '#8f9ba8'
BACKGROUND = '#282a2e'
FONT_AWESOME = 'Font Awesome 5 Free:style=Solid:size=10'
MAIN_FONT = 'Roboto:style=Medium:size=11'
GEOMETRY = '1920x32'
DIVIDER = "%{{F{color}}}|%{{F}}".format(color=FONT_COLOR)
LEMONBAR_CMD = [
                    'lemonbar',
                    '-B', BACKGROUND,
                    '-o', '-3',
                    '-f', FONT_AWESOME,
                    '-o', '-1',
                    '-f', MAIN_FONT,
                    '-g', GEOMETRY,
                    '-n', 'pybar'
                ]

DESKTOPS = [
                '%{{F{active}}}firefox%{{F}}    %{{F{inactive}}}discord%{{F}}    %{{F{inactive}}}dota2%{{F}}',
                '%{{F{inactive}}}firefox%{{F}}    %{{F{active}}}discord%{{F}}    %{{F{inactive}}}dota2%{{F}}',
                '%{{F{inactive}}}firefox%{{F}}    %{{F{inactive}}}discord%{{F}}    %{{F{active}}}dota2%{{F}}'
           ]
