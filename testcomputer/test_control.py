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
        cache = L1(3)

        return Control(cpu, cache, inQueue, outQueue, invalidate, notify)

    def test_replaceCacheBlock(self):
        control = self.getControl()
        notify = control.notify

        """
        | Num | Dir | Data | State
        | 0 | 0 | 0 | I
        | 1 | 0 | 0 | I
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(10, 50, CoherenceState.modified);
        r1 = notify.get()
        self.assertEqual(r1[0], ReplaceAction.invalid_replace)
        self.assertEqual(r1[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 0 | 0 | I
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(74, 120, CoherenceState.shared)
        r2 = notify.get()
        self.assertEqual(r2[0], ReplaceAction.invalid_replace)
        self.assertEqual(r2[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 74 | 120 | S
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(80, 45, CoherenceState.shared)
        r3 = notify.get()
        self.assertEqual(r3[0], ReplaceAction.invalid_replace)
        self.assertEqual(r3[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 74 | 120 | S
        | 2 | 80 | 45 | S
        """
        control.replaceCacheBlock(95, 47, CoherenceState.modified)
        r3 = notify.get()
        self.assertEqual(r3[0], ReplaceAction.share_replaced)
        self.assertEqual(r3[1], 74)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 95 | 47 | M
        | 2 | 80 | 45 | S
        """
        control.replaceCacheBlock(57, 47, CoherenceState.modified)
        r3 = notify.get()
        self.assertEqual(r3[0], ReplaceAction.share_replaced)
        self.assertEqual(r3[1], 80)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 95 | 47 | M
        | 2 | 57 | 47 | M
        """
        control.replaceCacheBlock(1, 20, CoherenceState.shared)
        r3 = notify.get()
        self.assertEqual(r3[0], ReplaceAction.modified_replaced)
        self.assertEqual(r3[1], 10)

        """
        | Num | Dir | Data | State
        | 0 | 01 | 20 | S
        | 1 | 95 | 47 | M
        | 2 | 57 | 47 | M
        """

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
        | 2 | 0 | 0 | I
        """
        memDir = 50
        control.readInstr(memDir)

        # Debe generar un rd miss
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.rdMiss)
        self.assertEqual(r[1], memDir)

        control.execute()

        # Debe notificar que cambio un bloque en la cache
        r = notify.get()
        self.assertEqual(r[0], ReplaceAction.invalid_replace)
        self.assertEqual(r[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 50 | 50 | S
        | 1 | 0  | 0  | I
        | 2 | 0  | 0  | I
        """

    def test_writeInstr(self):
        control = self.getControl()
        inQueue = control.inQueue
        outQueue = control.outQueue
        notify = control.notify

        control.cache.blockState = [CoherenceState.invalid,
                                    CoherenceState.shared,
                                    CoherenceState.modified]

        control.cache.blockDirMem = [1, 2, 3]

        control.cache.blockData = [14856,
                                   684,
                                   8640]
        """
        | Num | Dir | Data | State
        | 0 | 1 | 14856 | I
        | 1 | 2 | 684   | S
        | 2 | 3 | 8640  | M
        """
        inQueue.put(None)
        control.writeInstr(1, 50)

        # Notificacion wrMiss
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.wrMiss)
        self.assertEqual(r[1], 1)

        # Notificacion replacement
        r = notify.get()
        self.assertEqual(r[0], ReplaceAction.invalid_replace)
        self.assertEqual(r[1], 1)

        i = control.cache.blockDirMem.index(1)
        self.assertEqual(control.cache.blockState[i], CoherenceState.modified)

        """
        | Num | Dir | Data | State
        | 0 | 1 | 50    | M
        | 1 | 2 | 684   | S
        | 2 | 3 | 8640  | M
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
        | 0 | 1 | 50    | M
        | 1 | 2 | 700   | M
        | 2 | 3 | 8640  | M
        """
        inQueue.put(None)
        control.writeInstr(3, 800)

        # Notificacion wrHit
        r = outQueue.get()
        self.assertEqual(r[0], CacheAlert.wrHit)
        self.assertEqual(r[1], 3)

        i = control.cache.blockDirMem.index(3)
        self.assertEqual(control.cache.blockState[i], CoherenceState.modified)

    # def test_execute(self):
    #     control = self.getControl()
    #     inQueue = control.inQueue
    #
    #     for i in range(0, 5):
    #         inQueue.put(10)
    #
    #     for i in range(0, 4):
    #         control.execute()
