from computer.node.cpu.cpu import CPU
from computer.node.cache.cache_L1 import L1
from computer.node.control.control import Control


class Node:
    def __init__(self, inQueue, outQueue, cond):
        self.cpu = CPU()
        self.cache = L1()
        self.control = Control(self.cpu,
                               self.cache,
                               inQueue,
                               outQueue)
        self.cond = cond

    def exec(self):
        self.cond.wait()
        self.control.execute()
