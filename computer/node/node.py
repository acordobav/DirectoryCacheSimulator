from computer.node.cpu.cpu import CPU
from computer.node.cache.l1Cache import L1
from computer.node.control.control import Control


class Node:
    def __init__(self, inQueue, outQueue, enable):
        self.cpu = CPU()
        self.cache = L1()
        self.control = Control(self.cpu,
                               self.cache,
                               inQueue,
                               outQueue)
        self.enable = enable

    def exec(self):
        if self.enable:
            self.control.execute()
