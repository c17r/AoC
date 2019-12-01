# Utility
import re
import sys
import copy
import arrow
from dataclasses import dataclass, field
from pprint      import pprint
from collections import abc
from collections import Counter, defaultdict, namedtuple, deque
from functools   import lru_cache
from itertools   import permutations, combinations, chain, cycle, product, islice
from heapq       import heappop, heappush
from time        import sleep
from numba       import jit

def contents(year, day, part):
    with open(f'./{year}/day{day}/part{part}') as f:
        return f.read().splitlines()

def take(n, iterable, default=None):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n, default))

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)

first = lambda iterable: nth(iterable, 0)
map_ints = lambda ints: list(map(int, list(ints)))
get_ints = lambda line: map_ints(re.findall(r'\d+', line))
cat = ''.join

def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks:
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def overlapping(iterable, n):
    """Generate all (overlapping) n-element subsequences of iterable.
    overlapping('ABCDEFG', 3) --> ABC BCD CDE DEF EFG"""
    if isinstance(iterable, abc.Sequence):
        yield from (iterable[i:i+n] for i in range(len(iterable) + 1 - n))
    else:
        result = deque(maxlen=n)
        for x in iterable:
            result.append(x)
            if len(result) == n:
                yield tuple(result)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    return overlapping(iterable, 2)

def sequence(iterable, type=tuple):
    "Coerce iterable to sequence: leave alone if already a sequence, else make it `type`."
    return iterable if isinstance(iterable, abc.Sequence) else type(iterable)

def join(iterable, sep=''):
    "Join the items in iterable, converting each to a string first."
    return sep.join(map(str, iterable))

def powerset(iterable):
    "Yield all subsets of items."
    items = list(iterable)
    for r in range(len(items)+1):
        for c in combinations(items, r):
            yield c

def neighbors4(point):
    "The four neighboring squares."
    x, y = point
    return (          (x, y-1),
            (x-1, y),           (x+1, y),
                      (x, y+1))

def add(A, B):
    "Element-wise addition of two n-dimensional vectors."
    return mapt(sum, zip(A, B))

def mapt(fn, *args):
    "Do a map, and make the results into a tuple."
    return tuple(map(fn, *args))

"""
Day 15
"""

def day15():
    import networkx as nx
    from typing import List

    def group(iter, key=lambda i:i, pre=lambda i:i, post=lambda i:i):
        rv = defaultdict(list)
        for item in iter:
            new_item = pre(item)
            rv[key(new_item)].append(post(new_item))
        return rv

    class Unit:
        def __init__(self, r, c, team, symbol, gs, AP=3, HP=200):
            self.pt = (r, c)
            self.team = team
            self.symbol = symbol
            self.AP = AP
            self.HP = HP
            self.gs = gs
            self.alive = True

        def __str__(self):
            return f"{self.team}{self.symbol}"

        def __repr__(self):
            return f"{self.team}{self.symbol}({self.HP})"

        @property
        def dead(self):
            return self.alive is False

        def turn(self):
            if self.find_enemies() is False:
                return False
            if self.attack():
                return True
            self.move()
            self.attack()
            return True

        def take_hit(self, amount):
            self.HP -= amount
            self.alive = self.HP > 0

        def find_enemies(self):
            accounts = self.gs.active_counts()
            return len([t for t in accounts.keys() if t != self.team]) > 0

        def attack(self):
            enemies = self.gs.neighboring_enemies(self)
            if len(enemies) == 0:
                return False

            by_life = group(enemies, key=lambda e: e.HP)
            lowest_key = min(by_life.keys())
            lowest = sorted(by_life[lowest_key], key=lambda e: e.pt)
            target = lowest[0]
            target.take_hit(self.AP)
            return True

        def move(self):
            graph = self.build_graph()
            paths = self.build_paths(graph)
            enemy = self.pick_enemy(paths)
            if not enemy:
                return
            path = self.pick_path(enemy)
            self.pt = path[0]

        def build_graph(self):
            G = nx.Graph()
            units = {u.pt for u in self.gs.active_units() if u != self}
            for source in self.gs.valid:
                G.add_node(source)
                for neighbor in [pt for pt in self.gs.valid_neighbors(source) if pt not in units]:
                    G.add_edge(source, neighbor)
            return G

        def build_paths(self, G):
            rv = []
            for e in self.gs.active_enemy_units(self):
                e_rv = Path()
                e_rv.enemy = e
                for e_pt in self.gs.empty_neighbors(e.pt):
                    try:
                        paths = list(nx.all_shortest_paths(G, self.pt, e_pt))
                        paths = [t[1:] for t in paths]
                        print(str(self), 'build_paths', paths)
                        e_rv.lengths.append(len(paths[0]))
                        e_rv.paths.append(paths)
                    except nx.NetworkXNoPath as ex:
                        continue
                rv.append(e_rv)
            return rv

        def pick_enemy(self, P):
            shortest = None
            for p in P:
                if not p.lengths: continue
                tmp = min(p.lengths)
                if shortest is None or tmp < shortest:
                    shortest = tmp
            options = sorted([p for p in P if shortest in p.lengths], key=lambda p: p.enemy.pt)
            if not options:
                return
            return options[0]

        def pick_path(self, P):
            print(str(self), P) # debug
            shortest = min(P.lengths)
            options = []
            [options.extend(p) for p in P.paths if len(p[0]) == shortest]
            print(str(self), 'before', options) # debug
            options = sorted(options, key=lambda p: p[0])
            print(str(self), 'after', options) # debug
            return options[0]

    class Game:
        def __init__(self, data):
            self.legal = set()
            self.field = dict()
            self.units = set()
            self.teams = set()
            self.round = 0

            self.setup(data)
            self.valid = self.field.keys()
            self.mr = max(pt[0] for pt in self.field.keys())
            self.mc = max(pt[1] for pt in self.field.keys())

        def setup(self, data):
            from string import ascii_lowercase
            r, c = 0, 0
            ids = defaultdict(lambda : list(ascii_lowercase))

            for row in data:
                for col in row:
                    if col in ('#', '.'):
                        self.field[(r, c)] = col
                        if col == '.':
                            self.legal.add((r, c))
                    else:
                        self.field[(r, c)] = '.'
                        self.legal.add((r, c))

                        team = col
                        self.teams.add(team)
                        sym = ids[team].pop(0)
                        self.units.add(Unit(r, c, team, sym, self))

                    c += 1
                c = 0
                r += 1

        def run(self):
            while True:
                self.display_board()
                for unit in sorted(self.units, key=lambda u: u.pt):
                    if unit.dead: continue
                    if not unit.turn(): return
                self.round += 1
                if self.round > 25:
                    1/0

        def active_units(self):
            return set(u for u in self.units if u.alive)

        def active_counts(self):
            return Counter([u.team for u in self.active_units()])

        def empty_points(self):
            occupied = set(u.pt for u in self.active_units())
            return self.legal - occupied

        def active_enemy_units(self, current):
            return set(u for u in self.active_units() if u.team != current.team)

        def valid_neighbors(self, pt):
            neighbors = set(neighbors4(pt))
            return neighbors & self.legal

        def empty_neighbors(self, pt):
            vn = self.valid_neighbors(pt)
            unit_locs = set(u.pt for u in self.active_units())
            return vn - unit_locs

        def neighboring_enemies(self, current):
            vn = self.valid_neighbors(current.pt)
            return set(u for u in self.active_enemy_units(current) if u.pt in vn)

        def display_board(self):
            active_pts = {u.pt:u for u in self.active_units()}

            print('\n\n', f"Round #{self.round}")
            for r in range(self.mr + 1):
                for c in range(self.mc + 1):
                    if (r, c) in active_pts:
                        unit = active_pts[(r, c)]
                        print(str(unit), end=' ')
                    else:
                        print(self.field[(r, c)], end='  ')
                print('\t', end='')
                for unit in self.active_units():
                    if unit.pt[0] != r: continue
                    print(repr(unit), end='  ')
                print()
            print()

    @dataclass
    class Path:
        enemy: Unit = None
        lengths: List[int] = field(default_factory=list)
        paths: List[List[List[tuple]]] = field(default_factory=list)

    raw = contents(2018, 15, "0a")
    game = Game(raw)
    game.run()
    game.end_game()


day15()
