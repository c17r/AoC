from ..functional import always
from ..iters import add


def move(start, dir, amt=1):
	dist = dir[0] * amt, dir[1] * amt
	return add(start, dist)

	
def chess_move_inner(rights, downs, lefts, ups):
	rv = (0, 0)

	for _ in range(rights[0]): rv = add(rv, rights[1])
	for _ in range(downs[0]): rv = add(rv, downs[1])
	for _ in range(lefts[0]): rv = add(rv, lefts[1])
	for _ in range(ups[0]): rv = add(rv, ups[1])

	return rv


def data_to_grid_inner(raw, fs_to_c):
	grid, hf, hs = {}, None, None
	
	for fi, f in enumerate(raw):
		for si, s in enumerate(f):
			grid[fs_to_c(fi, si)] = s
			hs = si if hs is None or si > hs else hs
		hf = fi if hf is None or fi > hf else hf
	return grid, hf, hs


def grid_yield_inner(grid):
	lf = hf = ls = hs = None
	for f, s in grid.keys():
		lf = f if lf is None else min(lf, f)
		hf = f if hf is None else max(hf, f)
		ls = s if ls is None else min(ls, s)
		hs = s if hs is None else max(hs, s)
	for tf in range(lf, hf + 1):
		for ts in range(ls, hs + 1):
			yield tf, ts, False
		yield None, None, True


def grid_print_inner(grid, grid_yield, test=always(False)):
	for f, s, eol in grid_yield(grid):
		if eol:
			print('')
			continue
		p = grid.get((f, s), '')
		t = test(p)
		print(t if t is not False else p, end='')
