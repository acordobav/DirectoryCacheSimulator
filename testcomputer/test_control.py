import unittest
from queue import Queue
from computer.node.cpu.cpu import CPU
from computer.node.cache.cache_L1 import L1, CacheAlert, CoherenceState
from computer.node.control.control import Control, ReplaceAction


class TestControlMethods(unittest.TestCase):
    def getControl(self):
        inQueue = Queue()
        outQueue = Queue()
        invalidate = Queue()
        notify = Queue()
        cpu = CPU()
        cache = L1(2)

        return Control(cpu, cache, inQueue, outQueue, invalidate, notify)

    def test_replaceCacheBlock(self):
        control = self.getControl()
        notify = control.notify

        """
        | Num | Dir | Data | State
        | 0 | 0 | 0 | I
        | 1 | 0 | 0 | I
        """
        control.replaceCacheBlock(2, 50, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1, 0)

        """
        | Num | Dir | Data | State
        | 0 | 2 | 50 | M
        | 1 | 0 | 0 | I
        """
        control.replaceCacheBlock(6, 50, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1, 2)

        """
        | Num | Dir | Data | State
        | 0 | 6 | 50 | M
        | 1 | 0 | 0 | I
        """
        control.replaceCacheBlock(7, 11, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1, 0)

        """
        | Num | Dir | Data | State
        | 0 | 6 | 50 | M
        | 1 | 7 | 11 | M
        """
        control.replaceCacheBlock(9, 15, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1, 7)

        """
        | Num | Dir | Data | State
        | 0 | 6 | 50 | M
        | 1 | 9 | 15 | M
        """
        control.replaceCacheBlock(0, 11, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1, 6)

    def test_readInstr(self):
        control = self.getControl()
        inQueue = control.inQueue
        outQueue = control.outQueue
        notify = control.notify

        inQueue.put(50)

        """
        | Num | Dir | Data | State
        | 0 | 0 | 0 | I
        | 1 | 0 | 0 | I
        """
        memDir = 2
        control.readInstr(memDir)

        # Debe generar un rd miss
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.rdMiss)
        self.assertEqual(r[1], memDir)

        control.execute()

        # Debe notificar que cambio un bloque en la cache
        r = notify.get()
        self.assertEqual(r, 0)

        """
        | Num | Dir | Data | State
        | 0 | 50 | 50 | S
        | 1 | 0  | 0  | I
        """
        inQueue.put(34)
        memDir = 3
        control.readInstr(memDir)

        # Debe generar un rd miss
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.rdMiss)
        self.assertEqual(r[1], memDir)

        control.execute()

        # Debe notificar que cambio un bloque en la cache
        r = notify.get()
        self.assertEqual(r, 0)

        """
        | Num | Dir | Data | State
        | 0 | 2 | 50 | S
        | 1 | 3 | 34 | S
        """

    def test_writeInstr(self):
        control = self.getControl()
        inQueue = control.inQueue
        outQueue = control.outQueue
        notify = control.notify

        control.cache.blockState = [CoherenceState.modified,
                                    CoherenceState.shared]

        control.cache.blockDirMem = [2, 3]

        control.cache.blockData = [14856,
                                   684]
        """
        | Num | Dir | Data | State
        | 0 | 2 | 14856 | M
        | 1 | 3 | 684   | S
        """
        inQueue.put(None)
        control.writeInstr(1, 50)

        # Notificacion wrMiss
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.wrMiss)
        self.assertEqual(r[1], 1)

        # Notificacion replacement
        r = notify.get()
        self.assertEqual(r, 3)

        i = control.cache.blockDirMem.index(1)
        self.assertEqual(control.cache.blockState[i], CoherenceState.modified)

        """
        | Num | Dir | Data | State
        | 0 | 2 | 14856 | M
        | 1 | 1 | 50    | M
        """
        inQueue.put(None)
        control.writeInstr(2, 700)

        # Notificacion wrHit
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.wrHit)
        self.assertEqual(r[1], 2)

        i = control.cache.blockDirMem.index(2)
        self.assertEqual(control.cache.blockState[i], CoherenceState.modified)

        """
        | Num | Dir | Data | State
        | 0 | 2 | 700   | M
        | 1 | 1 | 50    | M
        """
        inQueue.put(None)
        control.writeInstr(4, 800)

        # Notificacion wrHit
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.wrMiss)
        self.assertEqual(r[1], 4)

        i = control.cache.blockDirMem.index(4)
        self.assertEqual(control.cache.blockState[i], CoherenceState.modified)
