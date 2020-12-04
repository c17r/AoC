def contents(year, day, part):
	with open(f'./y{year}/day{day}/part{part}') as f:
		return f.read().splitlines()
