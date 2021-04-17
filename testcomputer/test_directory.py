import unittest
from queue import Queue
from computer.directory.directory import Directory, CacheAlert, CoherenceState
from computer.directory.directory_state import DirectoryState


def get_directory():
    num_blocks = 3
    num_processors = 3
    directory = Directory(num_blocks, num_processors)

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


def get_update_buses():
    buses = []
    for i in range(0, 4):
        buses.append(Queue())
    return buses


class TestDirectoryMethods(unittest.TestCase):

    def test_read(self):
        directory = get_directory()
        update_buses = get_update_buses()

        # Prueba de rdMiss en direccion que no se tiene
        node_id = 0
        r = directory.read(node_id, 40, update_buses)
        self.assertEqual(r[0], CacheAlert.rdMiss)
        self.assertEqual(r[1], node_id)

        # Prueba de rdMiss en direccion con estado invalido
        node_id = 1
        r = directory.read(node_id, 10, update_buses)
        self.assertEqual(r[0], CacheAlert.rdMiss)
        self.assertEqual(r[1], node_id)

        # Prueba de escritura en un bloque exclusive, por parte del owner
        node_id = 0
        r = directory.read(node_id, 30, update_buses)
        self.assertEqual(r[0], CacheAlert.rdHit)
        self.assertEqual(r[1], 31)
        self.assertEqual(directory.processorRef[2], [1, 0, 0])

        # Prueba de lectura en un bloque exclusive, por parte de un
        # procesador que no es el owner
        node_id = 2
        r = directory.read(node_id, 30, update_buses)
        self.assertEqual(r[0], CacheAlert.rdHit)
        self.assertEqual(r[1], 31)
        self.assertEqual(directory.processorRef[2], [1, 0, 1])

        # Se verifica que se haya generado la alerta de actualizacion
        update_bus = update_buses[0]
        self.assertFalse(update_bus.empty())
        update = update_bus.get()
        self.assertEqual(update[0], 30)
        self.assertEqual(update[1], CoherenceState.shared)

    def test_write(self):
        directory = get_directory()
        update_buses = get_update_buses()

        # Escritura en un bloque invalido
        r = directory.write(1, 10, 22, update_buses)
        self.assertEqual(r[0], CacheAlert.wrHit)
        self.assertEqual(directory.processorRef[0], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            self.assertTrue(update_buses[i].empty())

        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  22  | DM  | 010 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Escritura en un bloque modificado por parte del mismo procesador
        r = directory.write(1, 10, 50, update_buses)
        self.assertEqual(r[0], CacheAlert.wrHit)
        self.assertEqual(directory.processorRef[0], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            self.assertTrue(update_buses[i].empty())

        """
        | N | Dir | Data | Sta | P   |
        | 0 |  10 |  50  | DM  | 010 |
        | 1 |  20 |  21  | DS  | 011 |
        | 2 |  30 |  31  | DM  | 100 |
        """
        # Escritura en unbloque modificado por otro procesador
        r = directory.write(1, 30, 70, update_buses)
        self.assertEqual(r[0], CacheAlert.wrHit)
        self.assertEqual(directory.processorRef[2], [0, 1, 0])
        self.assertEqual(directory.blockState[0], DirectoryState.exclusive)
        for i in range(0, len(update_buses)):
            if i == 0:
                message = update_buses[0].get()
                self.assertTrue(message[0], 30)
                self.assertTrue(message[0], CoherenceState.shared)
            else:
                self.assertTrue(update_buses[i].empty())