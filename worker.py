import re
import sys
import copy
import arrow
from pprint      import pprint
from collections import abc
from collections import Counter, defaultdict, namedtuple, deque
from functools   import lru_cache, reduce
from itertools   import permutations, combinations, chain, cycle, product, islice, zip_longest
from heapq       import heappop, heappush
from time        import sleep

import multiprocessing
from multiprocessing import Process, Queue

map_ints = lambda ints: list(map(int, list(ints)))

def contents(year, day, part):
    with open(f'./{year}/day{day}/part{part}') as f:
        return f.read().splitlines()

def mapt(fn, *args): 
    "Do a map, and make the results into a tuple."
    return tuple(map(fn, *args))

class Machine:
    def __init__(self, ops, data, get_pipe, put_pipe):
        Instruction = namedtuple('Instruction', ['func', 'ip'])
        self.get_pipe = get_pipe
        self.put_pipe = put_pipe
        self.ops = ops[:]
        self.ip = 0
        self.params = {}
        self.data = data
        self.instructions = {  1: Instruction(self.add, 4), 2: Instruction(self.mul, 4),
                               3: Instruction(self.get, 2), 4: Instruction(self.put, 2),
                               5: Instruction(self.jnz, 3), 6: Instruction(self.jez, 3),
                               7: Instruction(self.clt, 4), 8: Instruction(self.ceq, 4),
                              99: Instruction(self.hlt, 0) }
        
    def run(self):
        while True:
            old_ip = self.ip
            instruction = self.get_instruction()
            if (instruction.func()):
                return
            self.ip += instruction.ip if self.ip == old_ip else 0
            
    def get_instruction(self):
        op = f"{self.ops[self.ip]}"
        self.params =  {idx: int(p) for idx, p in enumerate(op[:-2][::-1], 1)}
        return self.instructions.get(int(op[-2:]), None)
        
    def read(self, idx):
        rv = self.ops[self.ip + idx]
        return self.ops[rv] if self.params.get(idx, 0) == 0 else rv
    
    def write(self, idx, v):
        self.ops[self.ops[self.ip + idx]] = v
    
    def hlt(self):
        #print("halt: ", self.ops[0])
        return True
    
    def put(self): 
        #print(self.read(1))
        #print(multiprocessing.current_process().name, 'put', self.read(1))
        self.put_pipe.put(self.read(1))
    
    def add(self): self.write(3, self.read(1) + self.read(2))
    def mul(self): self.write(3, self.read(1) * self.read(2))
    def get(self): 
        #self.write(1, int(self.data.pop(0)))
        rv = self.get_pipe.get()
        #print(multiprocessing.current_process().name, 'get', rv)
        self.write(1, int(rv))
        
    def jnz(self): self.ip = self.read(2) if self.read(1) != 0 else self.ip
    def jez(self): self.ip = self.read(2) if self.read(1) == 0 else self.ip
    def clt(self): self.write(3, 1 if self.read(1) < self.read(2) else 0)
    def ceq(self): self.write(3, 1 if self.read(1) == self.read(2) else 0)
        
def amplifier(ops, phase, inp):
    output = []
    def func(a):
        output.append(a)
    machine = Machine(ops, [phase, inp], func)
    machine.run()
    return output[0]

def multi_amp(ops, phase, get_pipe, put_pipe):
    def run():
        machine = Machine(ops, None, get_pipe, put_pipe)
        machine.run()

    get_pipe.put(phase)
    return Process(target=lambda x: run())

def run():
    raw = contents(2019, 7, 1)[0].split(',')
    ops = map_ints(raw)
    #ops = map_ints("3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0".split(','))
    #ops = map_ints("3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0".split(','))
    #ops = map_ints("3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5".split(','))


    def multi_start(tape):
        winner = None
        for p in permutations(range(5)):
            ab = Queue()
            bc = Queue()
            cd = Queue()
            de = Queue()
            ea = Queue()
            
            workers = []

            

            workers.append(multi_amp(tape, p[0], ea, ab))
            workers.append(multi_amp(tape, p[1], ab, bc))
            workers.append(multi_amp(tape, p[2], bc, cd))
            workers.append(multi_amp(tape, p[3], cd, de))
            workers.append(multi_amp(tape, p[4], de, ea))
            for w in workers:
                w.start()

            ea.put(0)
            for w in workers:
                w.join()

            rv = ea.get()
            if winner is None or rv > winner:
                print(rv)
                winner = rv

        return winner

    print('final', multi_start(ops))

if __name__ == '__main__':
    run()