from random import randrange
from computer.cpu.instr import InstrType


class CPU:
    instr = []

    def __init__(self):
        for i in range(0, 5):
            self.addInstr()

    def generateMemDir(self):
        return randrange(9)

    def generateInstr(self):
        val = randrange(10)
        if val < 3: # instruccion cacl
            return [InstrType.calc]

        if 3 <= val < 6: # instruccion read
            return [InstrType.read, self.generateMemDir()]

        if 6 <= val: # instruccion write
            return [InstrType.write, self.generateMemDir(), randrange(2**16)]

    def addInstr(self):
        newInstr = self.generateInstr()
        self.instr.append(newInstr)

    def popInstr(self):
        return self.instr.pop()
