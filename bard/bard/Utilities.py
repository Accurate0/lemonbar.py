from bard.Constants import SPACE

def wrap_in_f_colour(string, color):
    return '%{{F{color}}}{string}%{{F}}'.format(string=string, color=color)

def wrap_in_b_colour(string, color):
    return '%{{B{color}}}{string}%{{F}}'.format(string=string, color=color)

def add_padding(string, left, right):
    return f'{SPACE * left}{string}{SPACE * right}'
