import unittest

from computer.node.cpu.cpu import CPU, InstrType


class TestCPUMethods(unittest.TestCase):

    def test_generateMemDir(self):
        cpu = CPU()

        for i in range(0, 50):
            dirMem = cpu.generateMemDir()
            self.assertTrue(dirMem < 9)

    def test_generateInstr(self):
        cpu = CPU()

        for i in range(0, 50):
            instr = cpu.generateInstr()

            if len(instr) == 1:
                self.assertEqual(instr[0], InstrType.calc)

            elif len(instr) == 2:
                self.assertEqual(instr[0], InstrType.read)
                self.assertTrue(instr[1] < 9)

            else:
                self.assertEqual(instr[0], InstrType.write)
                self.assertTrue(instr[1] < 9)
                self.assertTrue(instr[1] < 2**16)
