import unittest
from queue import Queue
from computer.directory.directory import Directory, MemoryOperation, CoherenceState
from computer.directory.directory_state import DirectoryState


def get_directory():
    num_blocks = 3
    num_processors = 3

    buses = []
    for i in range(0, 4):
        buses.append(Queue())
    mem_bus = Queue()

    directory = Directory(num_blocks, num_processors, buses, mem_bus)

    """
    | N | Dir | Data | Sta | P   |
    | 0 |  10 |  11  | DI  | 000 |
    | 1 |  20 |  21  | DS  | 011 |
    | 2 |  30 |  31  | DM  | 100 |
    """

    directory.cache.blockDirMem = [10, 20, 30]
    directory.cache.blockData = [11, 21, 31]
    directory.blockState = [DirectoryState.uncached,
                            DirectoryState.shared,
                            DirectoryState.exclusive]
    directory.processorRef = [[0, 0, 0],
                              [0, 1, 1],
                              [1, 0, 0]]

    return directory


class TestDirectoryMethods(unittest.TestCase):

    def test_check_mem_dir(self):
        directory = get_directory()
        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  11  | DI  | 000 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Prueba de direccion que no se tiene
        r = directory.check_mem_dir(40)
        self.assertFalse(r)

        # Prueba de direccion con estado invalido
        r = directory.check_mem_dir(10)
        self.assertFalse(r)

        # Prueba con direccion que si es valida
        r = directory.check_mem_dir(20)
        self.assertTrue(r)

    def test_read(self):
        directory = get_directory()
        update_buses = directory.update_buses
        mem_bus = directory.mem_bus

        # Prueba de lectura en un bloque exclusive, por parte del owner
        node_id = 0
        r = directory.read(node_id, 30)
        self.assertEqual(r, 31)
        self.assertEqual(directory.processorRef[2], [1, 0, 0])
        self.assertTrue(mem_bus.empty())

        # Prueba de lectura en un bloque exclusive, por parte de un
        # procesador que no es el owner
        node_id = 2
        r = directory.read(node_id, 30)
        self.assertEqual(r, 31)
        self.assertEqual(directory.processorRef[2], [1, 0, 1])
        self.assertFalse(mem_bus.empty())
        m = mem_bus.get()
        self.assertEqual(m[0], MemoryOperation.write)
        self.assertEqual(m[1], 30, 31)

        # Se verifica que se haya generado la alerta de actualizacion
        update_bus = update_buses[0]
        self.assertFalse(update_bus.empty())
        update = update_bus.get()
        self.assertEqual(update[0], 30)
        self.assertEqual(update[1], CoherenceState.shared)

    def test_write(self):
        directory = get_directory()
        update_buses = directory.update_buses
        mem_bus = directory.mem_bus

        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  11  | DI  | 000 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Escritura en un bloque invalido
        directory.write(1, 10, 22, 0, DirectoryState.exclusive)
        self.assertEqual(directory.processorRef[0], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            self.assertTrue(update_buses[i].empty())
        self.assertTrue(mem_bus.empty())
        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  22  | DM  | 010 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Escritura en un bloque modificado por parte del mismo procesador
        directory.write(1, 10, 50, 0, DirectoryState.exclusive)
        self.assertEqual(directory.processorRef[0], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            self.assertTrue(update_buses[i].empty())
        self.assertTrue(mem_bus.empty())
        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  50  | DM  | 010 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Escritura en un bloque modificado por otro procesador
        directory.write(1, 30, 70, 2, DirectoryState.exclusive)
        self.assertEqual(directory.processorRef[2], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            if i == 0:
                message = update_buses[0].get()
                self.assertTrue(message[0], 30)
                self.assertTrue(message[0], CoherenceState.shared)
            else:
                self.assertTrue(update_buses[i].empty())
        self.assertFalse(mem_bus.empty())
        m = mem_bus.get()
        self.assertEqual(m[0], MemoryOperation.write)
        self.assertEqual(m[1], 30)
        self.assertEqual(m[2], 31)
