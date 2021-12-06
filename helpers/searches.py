from .functional import always

__all__ = [
	'Astar',
	'AstarSteps',
	'bfs',
]


def Astar(start, moves_func, h_func, cost_func=always(1)):
	"Find a shortest sequence of states from start to a goal state (where h_func(s) == 0)."
	frontier  = [(h_func(start), start)] # A priority queue, ordered by path length, f = g + h
	previous  = {start: None}  # start state has no previous state; other states will
	path_cost = {start: 0}     # The cost of the best path to a state.
	Path      = lambda s: ([] if (s is None) else Path(previous[s]) + [s])
	while frontier:
		(f, s) = heappop(frontier)
		if h_func(s) == 0:
			return Path(s)
		for s2 in moves_func(s):
			g = path_cost[s] + cost_func(s, s2)
			if s2 not in path_cost or g < path_cost[s2]:
				heappush(frontier, (g + h_func(s2), s2))
				path_cost[s2] = g
				previous[s2] = s

				
def AstarSteps(*args, **kwargs):
	return len(Astar(*args, **kwargs)) - 1


def bfs(start, moves_func, goals):
	"Breadth-first search"
	goal_func = (goals if callable(goals) else lambda s: s in goals)
	return Astar(start, moves_func, lambda s: (0 if goal_func(s) else 1))
