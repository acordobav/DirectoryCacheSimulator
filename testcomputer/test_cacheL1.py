import unittest

from computer.node.cache.cache_L1 import CoherenceState, L1
from computer.node.cache.cache_alert import CacheAlert


class TestL1Methods(unittest.TestCase):
    """
    Metodo para construir una cache L1 para pruebas
    | Num | Dir | Data | State
    | 0   | 10  | 4864 | S
    | 1   | 22  | 360  | M
    | 2   | 50  | 64   | I
    """
    def getL1(self):
        cache = L1(3)
        cache.blockState = [CoherenceState.shared,
                            CoherenceState.modified,
                            CoherenceState.invalid]
        cache.blockDirMem = [10, 22, 50]
        cache.blockNum = [0, 1, 2]
        cache.blockData = [4864, 360, 64]

        return cache

    def test_read(self):
        cache = self.getL1()

        # Caso bloque no se encuentra en cache
        r1 = cache.read(15)
        self.assertEqual(r1[0], CacheAlert.rdMiss)

        # Caso bloque es invalido
        r2 = cache.read(50)
        self.assertEqual(r2[0], CacheAlert.rdMiss)

        # Caso lectura exitosa
        r3 = cache.read(10)
        self.assertEqual(r3[0], CacheAlert.rdHit)
        self.assertEqual(r3[1], 4864)

    def test_write(self):
        cache = self.getL1()

        # Escribir en un bloque shared
        r1 = cache.write(10, 50, CoherenceState.shared)
        self.assertEqual(r1[0], CacheAlert.wrHit)

        # Escribir en un bloque que no se tiene
        r2 = cache.write(30, 120, CoherenceState.shared)
        self.assertEqual(r2[0], CacheAlert.wrMiss)

        # Escribir en un bloque modified
        r3 = cache.write(22, 500, CoherenceState.modified)
        self.assertEqual(r3[0], CacheAlert.wrHit)

    def test_replace(self):
        """
        | 1 | 22 | 360 | M
        """
        cache = self.getL1()

        index = 1
        data = 70
        memDir = 70
        state = CoherenceState.shared
        cache.replace(data, memDir, state, index)
        self.assertEqual(cache.blockData[index], data)
        self.assertEqual(cache.blockDirMem[index], memDir)
        self.assertEqual(cache.blockState[index], state)

        """
        | 1 | 70 | 70 | S
        """
