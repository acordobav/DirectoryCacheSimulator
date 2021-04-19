import unittest
from queue import Queue
from computer.directory.directory_control import DirectoryControl, CacheAlert
from computer.directory.directory_state import DirectoryState
from computer.memory.memory_operation import MemoryOperation
from computer.node.control.replace_action import ReplaceAction


def get_directory_control():
    mem_bus = [Queue(), Queue()]
    replace_bus = []
    num_processors = 4
    p_buses = []
    update_buses = []
    for i in range(0, num_processors):
        p_buses.append([Queue(), Queue()])
        p_buses.append(Queue())
        update_buses.append(Queue())
        replace_bus.append(Queue())

    directory_control = DirectoryControl(p_buses, mem_bus,
                                         update_buses, num_processors,
                                         replace_bus)
    directory = directory_control.directory

    """
    | N | Dir | Data | Sta | P    |
    | 0 |  10 |  11  | DI  | 0000 |
    | 1 |  20 |  21  | DS  | 0110 |
    | 2 |  30 |  31  | DM  | 1000 |
    | 3 |  40 |  41  | DS  | 1011 |
    """
    directory.cache.blockDirMem = [10, 20, 30, 40]
    directory.cache.blockData = [11, 21, 31, 41]
    directory.blockState = [DirectoryState.uncached,
                            DirectoryState.shared,
                            DirectoryState.exclusive,
                            DirectoryState.shared]
    directory.processorRef = [[0, 0, 0, 0],
                              [0, 1, 1, 0],
                              [1, 0, 0, 0],
                              [1, 0, 1, 1]]

    return directory_control


class TestDirectoryControlMethods(unittest.TestCase):

    def test_read_memory(self):
        directory = get_directory_control()
        mem_bus = directory.mem_bus[0]

        mem_dir = 4
        directory.read_memory(mem_dir)
        self.assertFalse(mem_bus.empty())
        r = mem_bus.get()
        self.assertTrue(r[0], MemoryOperation.read)
        self.assertTrue(r[1], mem_dir)

    def test_write_memory(self):
        directory = get_directory_control()
        mem_bus = directory.mem_bus[0]

        data = 62235
        mem_dir = 7
        directory.write_memory(mem_dir, data)
        self.assertFalse(mem_bus.empty())
        r = mem_bus.get()
        self.assertTrue(r[0], MemoryOperation.read)
        self.assertTrue(r[1], mem_dir)
        self.assertTrue(mem_bus.empty())

    def test_get_limits_set(self):
        directory = get_directory_control()

        index_set = 0
        x, y = directory.get_limits_set(index_set)
        self.assertEqual(x, 0)
        self.assertEqual(y, 2)

        index_set = 1
        x, y = directory.get_limits_set(index_set)
        self.assertEqual(x, 2)
        self.assertEqual(y, 4)

    def test_get_index_min_references(self):
        directory = get_directory_control()
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1010 |
        """
        x1 = 0
        y1 = 2
        x2 = 2
        y2 = 4

        i = directory.get_index_min_references(x1, y1)
        self.assertEqual(i, 0)

        i = directory.get_index_min_references(x2, y2)
        self.assertEqual(i, 2)

    def test_handle_read(self):
        directory_control = get_directory_control()
        mem_bus = directory_control.mem_bus[0]
        pending_requests = directory_control.pending_requests
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        mem_dir = 10
        node_id = 2
        requested = False
        directory_control.handle_read(mem_dir, node_id, requested)
        self.assertFalse(mem_bus.empty())
        m = mem_bus.get()
        self.assertEqual(m[0], MemoryOperation.read)
        self.assertEqual(m[1], mem_dir)

        self.assertIsNotNone(pending_requests[node_id])
        a = pending_requests[node_id]
        self.assertEqual(a[0], CacheAlert.rdMiss)
        self.assertEqual(a[1], mem_dir)

        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        mem_dir = 30
        node_id = 2
        requested = False
        directory_control.handle_read(mem_dir, node_id, requested)
        self.assertFalse(mem_bus.empty()) # Bloque exclusivo, hace write back

        self.assertIsNone(pending_requests[node_id])
        self.assertEqual(directory_control.directory.processorRef[2],
                         [1, 0, 1, 0])

    def test_hande_write(self):
        directory_control = get_directory_control()
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        # Escritura en un bloque que no esta cargado
        mem_dir = 8
        data = 81
        node_id = 3
        directory_control.handle_write(mem_dir, data, node_id)
        self.assertEqual(directory_control.directory.processorRef[0],
                         [0, 0, 0, 1])
        self.assertEqual(directory_control.directory.blockState[0],
                         DirectoryState.exclusive)

        # Escritura en un bloque que esta cargado
        mem_dir = 9
        data = 81
        node_id = 1
        directory_control.handle_write(mem_dir, data, node_id)
        self.assertEqual(directory_control.directory.processorRef[2],
                         [0, 1, 0, 0])
        self.assertEqual(directory_control.directory.blockState[2],
                         DirectoryState.exclusive)
        self.assertFalse(directory_control.update_buses[0].empty())

    def test_handle_memory_response(self):
        directory_control = get_directory_control()
        mem_bus = directory_control.mem_bus[1]
        pending_requests = directory_control.pending_requests
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        mem_dir = 50
        data = 51
        mem_bus.put([mem_dir, data])
        pending_requests[0] = [CacheAlert.rdMiss, mem_dir]
        directory_control.handle_memory_response()
        self.assertEqual(directory_control.directory.processorRef[0],
                         [1, 0, 0, 0])

    def test_remove_reference(self):
        directory_control = get_directory_control()
        mem_bus = directory_control.mem_bus[0]
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        # Remover referencia del procesador 0 en el bloque 2
        directory_control.remove_reference(30, 0)
        self.assertEqual(directory_control.directory.processorRef[2],
                        [0, 0, 0, 0])
        self.assertEqual(directory_control.directory.blockState[2],
                         DirectoryState.uncached)
        self.assertFalse(mem_bus.empty())
        m = mem_bus.get()

        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DI  | 0000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        # Remover referencia del procesador 1 en el bloque 1
        directory_control.remove_reference(20, 1)
        self.assertEqual(directory_control.directory.processorRef[1],
                        [0, 0, 1, 0])
        self.assertEqual(directory_control.directory.blockState[1],
                         DirectoryState.shared)
        self.assertTrue(mem_bus.empty())

    def test_handle_replace_alerts(self):
        directory_control = get_directory_control()
        replace_bus = directory_control.replace_bus
        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0110 |
        | 2 |  30 |  31  | DM  | 1000 |
        | 3 |  40 |  41  | DS  | 1011 |
        """
        replace_bus[1].put([ReplaceAction.share_replaced, 20])
        replace_bus[2].put([ReplaceAction.share_replaced, 20])
        replace_bus[2].put([ReplaceAction.share_replaced, 40])
        replace_bus[0].put([ReplaceAction.share_replaced, 30])
        directory_control.handle_replace_alerts()

        """
        | N | Dir | Data | Sta | P    |
        | 0 |  10 |  11  | DI  | 0000 |
        | 1 |  20 |  21  | DS  | 0000 |
        | 2 |  30 |  31  | DM  | 0000 |
        | 3 |  40 |  41  | DS  | 1001 |
        """
        self.assertEqual(directory_control.directory.processorRef[1],
                         [0, 0, 0, 0])
        self.assertEqual(directory_control.directory.processorRef[2],
                         [0, 0, 0, 0])
        self.assertEqual(directory_control.directory.processorRef[3],
                         [1, 0, 0, 1])
