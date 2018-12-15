from pprint      import pprint
from collections import Counter, defaultdict, namedtuple, deque
from heapq       import heappop, heappush
import time

def contents(year, day, part):
    with open(f'./{year}/day{day}/part{part}') as f:
        return f.read().splitlines()

def X(point): return point[0]
def Y(point): return point[1]

def R(point): return point[0]
def C(point): return point[1]

origin = (0, 0)
xy_HEADINGS = xy_UP, xy_LEFT, xy_DOWN, xy_RIGHT = (0, -1), (-1, 0), (0, 1), (1, 0)
rc_HEADINGS = rc_UP, rc_LEFT, rc_DOWN, rc_RIGHT = (-1, 0), (0, -1), (1, 0), (0, 1)

def xy_turn_right(heading): return xy_HEADINGS[HEADINGS.index(heading) - 1]
def xy_turn_around(heading):return xy_HEADINGS[HEADINGS.index(heading) - 2]
def xy_turn_left(heading):  return xy_HEADINGS[HEADINGS.index(heading) - 3]

def rc_turn_right(heading): return rc_HEADINGS[HEADINGS.index(heading) - 1]
def rc_turn_around(heading):return rc_HEADINGS[HEADINGS.index(heading) - 2]
def rc_turn_left(heading):  return rc_HEADINGS[HEADINGS.index(heading) - 3]


def neighbors4(point): 
    "The four neighboring squares."
    x, y = point
    return (          (x, y-1),
            (x-1, y),           (x+1, y), 
                      (x, y+1))

def mapt(fn, *args): 
    "Do a map, and make the results into a tuple."
    return tuple(map(fn, *args))

def always(value): return (lambda *args: value)

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

def bfs(start, moves_func, goals):
    "Breadth-first search"
    goal_func = (goals if callable(goals) else lambda s: s in goals)
    return Astar(start, moves_func, lambda s: (0 if goal_func(s) else 1))

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed

@timeit
def day15():

    class GameState:
        def __init__(self, raw):
            from string import ascii_lowercase
            unit_nums = {
                'E': list(ascii_lowercase),
                'G': list(ascii_lowercase)
            }
            players = unit_nums.keys()

            self.units = []
            self.field = {}

            x, y = 0, 0
            for line in raw:
                for point in line:
                    if point in players:
                        self.units.append(Unit(self, (x, y), point, unit_nums[point].pop(0)))
                        self.field[(x, y)] =  "."
                    else:
                        self.field[(x, y)] = point
                    x += 1
                y += 1
                x = 0
            self.valid_field_points = self.field.keys()
            self.non_walls = [p for p in self.field.keys() if self.field[p] == "."]

        def active_units(self):
            return [u for u in self.units if u.alive]

        def active_enemies(self, current):
            return [u for u in self.active_units() if u.team != current.team]

        def valid_neighbors(self, point):
            return set([n for n in neighbors4(point) if n in self.non_walls])

        def empty_neighbors(self, target):
            return set([n for n in self.valid_neighbors(target.point) if self.field[n] == "."])

        def attackable_enemies(self, current):
            current_surroundings = self.valid_neighbors(current.point)
            return set([u for u in self.active_enemies(current) if u.point in current_surroundings])

        def active_count(self):
            return Counter(u.team for u in self.active_units())

        def unoccupied_field_points(self):
            unit_positions = set([u.point for u in self.active_units()])
            return set([p for p in self.non_walls if p not in unit_positions])

        def shortest_path(self, current, target):
            unoccupied_field_points = self.unoccupied_field_points()
            valid = lambda pt: set([n for n in self.valid_neighbors(pt) if n in unoccupied_field_points])

            destinations = self.empty_neighbors(target)
            candidates = defaultdict(list)
            for point in destinations:
                path = bfs(current.point, valid, (point,))
                if path:
                    path.pop(0)
                    candidates[len(path)].append(path)
            if not candidates.keys():
                return None

            min_path = min(candidates.keys())
            min_paths = candidates[min_path]
            s_min_paths = sorted(min_paths, key=lambda e: book_order(e[0]))
            return s_min_paths[0]

    def book_order(pt):       
        return (Y(pt), X(pt))

    class Unit:
        def __init__(self, game_state, point, team, unit_num):
            self.game_state = game_state
            self.point = point
            self.team = team
            self.attack_power = 3
            self.health = 200
            self.alive = True
            self.unit_num = unit_num
            
        def __str__(self):
            return f"{self.team}{self.unit_num}"

        def __repr__(self):
            return f"<Unit {str(self)} p={self.point} h={self.health} a={self.alive}"
            
        def attacked(self, attack_power):
            self.health -= attack_power
            if self.health <= 0:
                self.alive = False
        
        def turn(self):
            if len(self.game_state.active_enemies(self)) == 0:
                return False
            if self.attack_if_possible():
                return True
            moved = self.move_towards_enemy()
            if moved:
                self.attack_if_possible()
            return True
                
        def attack_if_possible(self):
            enemies = self.game_state.attackable_enemies(self)
            if not enemies:
                return False

            candidates = defaultdict(list)
            for enemy in enemies:
                candidates[enemy.health].append(enemy)

            lowest = min(candidates.keys())
            targets = sorted(candidates[lowest], key=lambda c: book_order(c.point))
            target = targets[0]
            if GLOBAL_DEBUG: print(str(self), ": hit ", str(target))
            target.attacked(self.attack_power)
            return True
            
        def move_towards_enemy(self):
            enemies = self.game_state.active_enemies(self)
            if not enemies:
                return False
            
            candidates = defaultdict(list)
            for enemy in enemies:
                path = self.game_state.shortest_path(self, enemy)
                if path:
                    candidates[len(path)].append((enemy, path))

            if not candidates.keys():
                return False
            
            min_path = min(candidates.keys())
            min_paths = candidates[min_path]
            targets = sorted(min_paths, key=lambda t: book_order(t[0].point))
            target = targets[0]
            if GLOBAL_DEBUG: print(str(self), ": move ", self.point, " to ", target[1][0], " towards ", str(target[0]))
            self.point = target[1][0]
            return True
            
    def print_field(t, gs):
        print(f'Round {t}')
        p_units = {u.point: u for u in gs.active_units()}
        mx = max(X(e) for e in gs.valid_field_points)
        my = max(Y(e) for e in gs.valid_field_points)
        for y in range(my + 1):
            for x in range(mx + 1):
                if (x, y) in p_units:
                    item = p_units[(x,y)]
                    tag = f"{item.team}{item.unit_num}"
                    print(f"{tag}", end=" ")
                else:
                    print(gs.field[(x,y)], end="  ")
            print()

        print_units(gs, 'E')
        print_units(gs, 'G')
        print()
        print()

    def print_units(gs, team):
        squad = [u for u in gs.units if u.team == team]
        for idx, unit in enumerate(sorted(squad, key=lambda u: u.health, reverse=True), start=1):
            print(F"{idx}:{unit.team}{unit.unit_num}({unit.health})", end="  ")
        
    def end_game(t, gs):
        es = [u for u in gs.active_units() if u.team == "E"]
        gs = [u for u in gs.active_units() if u.team == "G"]
        
        eht = sum(e.health for e in es)
        ght = sum(g.health for g in gs)
        
        print(f" Rounds: {t}")
        print(f"  Elves: {len(es)} units, total {eht}, score: {eht*t}")
        print(f"Goblins: {len(gs)} units, total {ght}, score: {ght*t}")

    def do_round(t, gs):
        a_units = gs.active_units()
        sa_units = sorted(a_units, key=lambda u: book_order(u.point))
        
        for unit in sa_units:
            if not unit.alive: 
                continue
            if unit.turn() is False:
                return True
        return False
            
    def main(file):
        gs = GameState(contents(2018, 15, file))
        t = 0
        while True:
            if GLOBAL_DEBUG:
                print_field(t, gs)
                input("<paused>")
            else:
                print('!', end="")
                if t % 100 == 0:
                    print()
                    print_field(t, gs)

            if do_round(t, gs):
                print_field(t, gs)
                end_game(t, gs)
                return
            t += 1

    GLOBAL_DEBUG = False
    
    #for f in ("0a", "0b", "0c", "0d", "0e", "0f"):
    for f in ("1",):
        print(f"---- {f} begin ----")
        main(f)
        print(f"---- {f} end ----")
        

day15()

"""
attempts
203224: too high
188789: too low
"""

"""
0a 47 rounds, G 590, 27730 - good
0b 37 rounds, E 982, 38334 - good
0c 46 rounds, E 859, 39514 - good
0d 35 founds, G 793, 27755 - good
0e 54 rounds, G 536, 28944 - good
0f 20 rounds, G 937, 18740 - good
"""