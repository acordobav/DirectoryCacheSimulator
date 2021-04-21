from numpy import random
from computer.node.cpu.instr import InstrType


class CPU:

    def __init__(self):
        self.instr = []
        for i in range(0, 2):
            self.addInstr()

    def generateMemDir(self):
        return random.binomial(n=7, p=0.5, size=1)[0]

    def generateInstr(self):
        val = random.binomial(n=2, p=0.6, size=1)[0]
        if val == 0:  # instruccion read
            return [InstrType.read, self.generateMemDir()]

        elif val == 1:  # instruccion calc
            return [InstrType.calc]

        else:  # instruccion write
            data = random.binomial(n=2**16, p=0.5, size=1)[0]
            return [InstrType.write, self.generateMemDir(), data]

    def addInstr(self):
        newInstr = self.generateInstr()
        self.instr.insert(0, newInstr)

    def popInstr(self):
        return self.instr.pop()
