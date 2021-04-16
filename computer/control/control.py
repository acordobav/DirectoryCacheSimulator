from queue import Queue
from computer.cpu.cpu import CPU
from computer.cpu.instr import InstrType
from computer.cache.l1Cache import L1, CacheAlert, CoherenceState
from computer.control.replace import ReplaceAction

class Control:

    def __init__(self, cpu, cache, inQueue, outQueue):
        self.cpu = cpu
        self.cache = cache
        self.inQueue = inQueue;
        self.outQueue = outQueue;

    def execute(self):
        instr = self.cpu.popInstr()

        if instr[0] == InstrType.read:
            result = self.readInstr(instr[1])

    def readInstr(self, memDir):
        result = self.cache.read(memDir)

        # Si la lectura fue un hit se retorna el valor
        if result[0] == CacheAlert.rdHit:
            return result[1]

        # Se espera para obtener el valor de la cache L2
        self.outQueue.put([CacheAlert.rdMiss, memDir])
        data = self.inQueue.get()

        # Se escribe el valor en cache
        self.replaceCacheBlock(memDir, data, CoherenceState.shared)

    def replaceCacheBlock(self, memDir, data, newState):
        # Se intenta reemplazar un bloque invalido
        if self.replaceAux(memDir,
                           data,
                           CoherenceState.invalid,
                           ReplaceAction.invalid_replace,
                           newState):
            return

        # Se intenta reemplazar un bloque compartido
        if self.replaceAux(memDir,
                           data,
                           CoherenceState.shared,
                           ReplaceAction.share_replaced,
                           newState):
            return

        # Se intenta reemplazar un bloque modificado
        if self.replaceAux(memDir,
                           data,
                           CoherenceState.modified,
                           ReplaceAction.modified_replaced,
                           newState):
            return

    def replaceAux(self, memDir, data, state, replaceAction, newState):
        if state not in self.cache.blockState:
            return False

        # Se obtiene el index del elemento compartido
        index = self.cache.blockState.index(state)

        # Se notifica al directorio que el bloque se libera
        oldMemDir = self.cache.blockDirMem[index]
        self.outQueue.put([replaceAction, oldMemDir])

        # Se reemplaza el bloque
        self.cache.replace(memDir, data, newState, index)

        return True
