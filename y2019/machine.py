from collections import namedtuple

Instruction = namedtuple('Instruction', 'func ip')
MachineState = namedtuple('MachineState', 'program, ip, rb, params')

class Machine:
    def __init__(self, ops, inp, outp, haltf):
        self.ops = {idx: i for idx, i in enumerate(ops)}
        self.ip = 0
        self.rb = 0
        self.params = {}
        self.inp = inp
        self.outp = outp
        self.haltf = haltf
        self.instructions = {  1: Instruction(self.add, 4), 2: Instruction(self.mul, 4),
                               3: Instruction(self.get, 2), 4: Instruction(self.put, 2),
                               5: Instruction(self.jnz, 3), 6: Instruction(self.jez, 3),
                               7: Instruction(self.clt, 4), 8: Instruction(self.ceq, 4),
                               9: Instruction(self.rbo, 2),
                              99: Instruction(self.hlt, 0) }
        self.modes = {
            0: self.mode0,
            1: self.mode1,
            2: self.mode2,
        }

    def run(self):
        while True:
            if self.step() is False:
                return

    def step(self):
        old_ip = self.ip
        instruction = self.get_instruction()
        if (instruction.func()):
            return False
        self.ip += instruction.ip if self.ip == old_ip else 0
        return True

    def get_instruction(self):
        op = f"{self.ops[self.ip]}"
        self.params =  {idx: int(p) for idx, p in enumerate(op[:-2][::-1], 1)}
        return self.instructions.get(int(op[-2:]), None)

    def read(self, idx):
        return self.modes[self.params.get(idx, 0)](self.ops[self.ip + idx])

    def write(self, idx, v):
        addr = self.ops[self.ip + idx]
        if self.params.get(idx, 0) == 2:
            addr = self.rb + addr
        self.ops[addr] = v

    def hlt(self):
        self.haltf()
        return True

    def mode0(self, addr): return self.ops.get(addr, 0)
    def mode1(self, val): return val
    def mode2(self, addr): return self.ops.get(self.rb + addr, 0)

    def rbo(self): self.rb = self.rb + self.read(1)
    def add(self): self.write(3, self.read(1) + self.read(2))
    def mul(self): self.write(3, self.read(1) * self.read(2))
    def get(self): self.write(1, int(self.inp()))
    def put(self): self.outp(self.read(1))
    def jnz(self): self.ip = self.read(2) if self.read(1) != 0 else self.ip
    def jez(self): self.ip = self.read(2) if self.read(1) == 0 else self.ip
    def clt(self): self.write(3, 1 if self.read(1) < self.read(2) else 0)
    def ceq(self): self.write(3, 1 if self.read(1) == self.read(2) else 0)

class FMachine(Machine):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self.history = []

    def _freeze(self):
        self.history.append(MachineState(self.ops, self.ip, self.rb. self.params))

    def run(self):
        while True:
            self._freeze()
            if self.step() is False:
                return