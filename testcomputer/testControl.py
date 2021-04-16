import unittest
from computer.control.control import *

class TestControlMethods(unittest.TestCase):
    def getControl(self):
        inQueue = Queue()
        outQueue = Queue()
        cpu = CPU()
        cache = L1(3)

        return Control(cpu, cache, inQueue, outQueue)

    def test_replaceCacheBlock(self):
        control = self.getControl()
        outQueue = control.outQueue

        """
        | Num | Dir | Data | State
        | 0 | 0 | 0 | I
        | 1 | 0 | 0 | I
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(10, 50, CoherenceState.modified);
        r1 = outQueue.get()
        self.assertEqual(r1[0], ReplaceAction.invalid_replace)
        self.assertEqual(r1[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 0 | 0 | I
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(74, 120, CoherenceState.shared)
        r2 = outQueue.get()
        self.assertEqual(r2[0], ReplaceAction.invalid_replace)
        self.assertEqual(r2[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 74 | 120 | S
        | 2 | 0 | 0 | I
        """
        control.replaceCacheBlock(80, 45, CoherenceState.shared)
        r3 = outQueue.get()
        self.assertEqual(r3[0], ReplaceAction.invalid_replace)
        self.assertEqual(r3[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 74 | 120 | S
        | 2 | 80 | 45 | S
        """
        control.replaceCacheBlock(95, 47, CoherenceState.modified)
        r3 = outQueue.get()
        self.assertEqual(r3[0], ReplaceAction.share_replaced)
        self.assertEqual(r3[1], 74)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 95 | 47 | M
        | 2 | 80 | 45 | S
        """
        control.replaceCacheBlock(57, 47, CoherenceState.modified)
        r3 = outQueue.get()
        self.assertEqual(r3[0], ReplaceAction.share_replaced)
        self.assertEqual(r3[1], 80)

        """
        | Num | Dir | Data | State
        | 0 | 10 | 50 | M
        | 1 | 95 | 47 | M
        | 2 | 57 | 47 | M
        """
        control.replaceCacheBlock(1, 20, CoherenceState.shared)
        r3 = outQueue.get()
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

        # Debe notificar que cambio un bloque en la cache
        r = outQueue.get()
        self.assertEqual(r[0], ReplaceAction.invalid_replace)
        self.assertEqual(r[1], 0)

        """
        | Num | Dir | Data | State
        | 0 | 50 | 50 | S
        | 1 | 0  | 0  | I
        | 2 | 0  | 0  | I
        """