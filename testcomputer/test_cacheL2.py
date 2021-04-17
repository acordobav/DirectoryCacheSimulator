import unittest
from computer.directory.cache_L2 import L2


class TestCacheL2Methods(unittest.TestCase):

    def getL2(self):
        cache = L2(4)
        cache.blockData = [10, 20, 30, 40]
        cache.blockDirMem = [54, 65, 23, 44]

        return cache

    def test_write(self):
        cache = self.getL2()

        cache.write(70, 11, 0)
        cache.write(27, 53, 2)

        # Verificacion que las direcciones de memoria cambiaron
        self.assertEqual(cache.blockDirMem, [70, 65, 27, 44])

        # Verificacion que la informacion de los bloques cambio
        self.assertEqual(cache.blockData, [11, 20, 53, 40])

    def test_read(self):
        cache = self.getL2()

        r = cache.read(54)
        self.assertEqual(r, 10)

        r = cache.read(44)
        self.assertEqual(r, 40)

        r = cache.read(65)
        self.assertEqual(r, 20)

