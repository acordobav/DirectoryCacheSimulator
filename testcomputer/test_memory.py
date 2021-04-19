import unittest
from queue import Queue
from computer.memory.memory import Memory
from computer.memory.memory_operation import MemoryOperation


def get_memory():
    mem_bus = [Queue(), Queue()]
    memory = Memory(mem_bus)
    memory.data = [10, 20, 30, 40,
                   50, 60, 70, 80]

    return memory


class TestMemoryMethods(unittest.TestCase):

    def test_write(self):
        memory = get_memory()

        mem_dir = 0
        data = 61615
        memory.write(mem_dir, data)
        self.assertEqual(memory.data[mem_dir], data)

        mem_dir = 5
        data = 47965
        memory.write(mem_dir, data)
        self.assertEqual(memory.data[mem_dir], data)

    def test_read(self):
        memory = get_memory()

        mem_bus = memory.mem_bus[1]

        mem_dir = 0
        memory.read(mem_dir)
        self.assertFalse(mem_bus.empty())
        self.assertEqual(mem_bus.get(), 10)

        mem_dir = 5
        memory.read(mem_dir)
        self.assertFalse(mem_bus.empty())
        self.assertEqual(mem_bus.get(), 60)

        mem_dir = 7
        memory.read(mem_dir)
        self.assertFalse(mem_bus.empty())
        self.assertEqual(mem_bus.get(), 80)

    def test_execute(self):
        memory = get_memory()
        mem_bus = memory.mem_bus

        mem_bus[0].put([MemoryOperation.write, 0, 500])
        mem_bus[0].put([MemoryOperation.read, 4])
        mem_bus[0].put([MemoryOperation.write, 3, 700])
        mem_bus[0].put([MemoryOperation.read, 6])
        mem_bus[0].put([MemoryOperation.write, 7, 56200])

        memory.execute()

        self.assertEqual(memory.data, [500, 20, 30, 700,
                                       50, 60, 70, 56200])

        self.assertFalse(mem_bus[1].empty())
        self.assertEqual(mem_bus[1].get(), 50)
        self.assertFalse(mem_bus[1].empty())
        self.assertEqual(mem_bus[1].get(), 70)

