
origin = (0, 0)


def neighbors4(point): 
	"The four neighboring squares."
	x, y = point
	return (          (x, y-1),
			(x-1, y),           (x+1, y), 
					  (x, y+1))


def neighbors8(point): 
	"The eight neighboring squares."
	x, y = point 
	return ((x-1, y-1), (x, y-1), (x+1, y-1),
			(x-1, y),             (x+1, y),
			(x-1, y+1), (x, y+1), (x+1, y+1))


def neighborsLR(point):
	x, y = point
	return (x-1, y), (x+1, y)


def neighborsAB(point):
	x, y = point
	return (x, y-1), (x, y+1)


def cityblock_distance(P, Q=origin): 
	"Manhatten distance between two points."
	return sum(abs(p - q) for p, q in zip(P, Q))


def distance(P, Q=origin): 
	"Straight-line (hypotenuse) distance between two points."
	return sum((p - q) ** 2 for p, q in zip(P, Q)) ** 0.5


def king_distance(P, Q=origin):
	"Number of chess King moves between two points."
	return max(abs(p - q) for p, q in zip(P, Q))
