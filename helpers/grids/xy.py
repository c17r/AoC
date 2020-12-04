from .shared import *
__all__ = [
	'X', 'Y', 
	'HEADINGS', 'UP', 'LEFT', 'DOWN', 'RIGHT',
	'turn_right', 'turn_around', 'turn_left'
	'chess_move', 
	'data_to_grid', 
	'grid_yield', 
	'grid_print',
]

X = lambda pt: pt[0]
Y = lambda pt: pt[1]

HEADINGS = UP, LEFT, DOWN, RIGHT = (0, -1), (-1, 0), (0, 1), (1, 0)

turn_right = lambda heading: HEADINGS[HEADINGS.index(heading) - 1]
turn_around = lambda heading: HEADINGS[HEADINGS.index(heading) - 2]
turn_left = lambda heading: HEADINGS[HEADINGS.index(heading) - 3]

def chess_move(*, rights=0, downs=0, lefts=0, ups=0):
	return chess_move_inner((rights, RIGHT), (downs, DOWN), (lefts, LEFT), (ups, UP))

def data_to_grid(raw):
	grid, hf, hs = data_to_grid_inner(raw, lambda f, s: (s, f))
	return grid, hs, hf

def grid_yield(grid):
	for f, s, eol in grid_yield_inner(grid):
		yield s, f, eol

def grid_print(grid, test=always(False)):
	grid_print_inner(grid, grid_yield, test)
