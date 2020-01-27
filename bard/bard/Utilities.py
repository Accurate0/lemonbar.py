from bard.Constants import SPACE

def f_colour(string, color):
    return '%{{F{color}}}{string}%{{F}}'.format(string=string, color=color)

def b_colour(string, color):
    return '%{{B{color}}}{string}%{{F}}'.format(string=string, color=color)

def add_padding(string, left, right):
    return f'{SPACE * left}{string}{SPACE * right}'

def command(string, cmd):
    return '%{{A:{cmd}:}}{string}%{{A}}'.format(string=string, cmd=cmd)
