import unittest
from queue import Queue
from computer.directory.directory_control import DirectoryControl
from computer.memory.memory_operation import MemoryOperation


def get_directory_control():
    mem_bus = Queue()
    num_processors = 4
    p_buses = []
    for i in range(0, num_processors):
        p_buses.append([Queue(), Queue()])

    return DirectoryControl(p_buses, mem_bus)


class TestDirectoryControlMethods(unittest.TestCase):

    def test_read_memory(self):
        directory = get_directory_control()
        mem_bus = directory.mem_bus
        waiting_state = directory.waiting_state

        node_id = 2
        mem_dir = 4
        directory.read_memory(mem_dir, node_id)
        self.assertFalse(mem_bus.empty())
        r = mem_bus.get()
        self.assertTrue(r[0], MemoryOperation.read)
        self.assertTrue(r[1], mem_dir)
        self.assertTrue(waiting_state[node_id])

    def test_write_memory(self):
        directory = get_directory_control()
        mem_bus = directory.mem_bus
        waiting_state = directory.waiting_state

        data = 62235
        mem_dir = 7
        directory.write_memory(mem_dir, data)
        self.assertFalse(mem_bus.empty())
        r = mem_bus.get()
        self.assertTrue(r[0], MemoryOperation.read)
        self.assertTrue(r[1], mem_dir)
        self.assertTrue(mem_bus.empty())

        for i in range(0, len(waiting_state)):
            self.assertFalse(waiting_state[i])
