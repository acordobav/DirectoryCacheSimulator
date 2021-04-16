from computer.node.cpu.instr import InstrType
from computer.node.cache.l1Cache import CacheAlert, CoherenceState
from computer.node.control.replaceAction import ReplaceAction


class Control:
    instr = [""]

    def __init__(self, cpu, cache, inQueue, outQueue):
        self.cpu = cpu
        self.cache = cache
        self.inQueue = inQueue;
        self.outQueue = outQueue;

    def execute(self):
        # Se obtiene una instruccion de la cola
        self.instr = self.cpu.popInstr()
        instr = self.instr

        if instr[0] == InstrType.read:
            self.readInstr(instr[1])

        elif instr[0] == InstrType.write:
            self.writeInstr(instr[1], instr[2])

        else:
            self.calcInstr()

        # Se genera una nueva instruccion
        self.cpu.addInstr()

    def calcInstr(self):
        self.outQueue.put(None)
        self.outQueue.put(None)

    def writeInstr(self, memDir, data):
        result = self.cache.write(
            memDir,
            data,
            CoherenceState.modified)

        # Si la escritura fue un hit no se realiza ninguna accion
        if result[0] == CacheAlert.wrHit:
            self.outQueue.put([CacheAlert.wrHit, memDir])
            self.outQueue.put(None)
            return

        # Se notifica al directorio que ocurrio un wrMiss
        self.outQueue.put([CacheAlert.wrMiss, memDir])
        self.inQueue.get()

        # Se escribe el valor en cache
        self.replaceCacheBlock(memDir, data, CoherenceState.modified)

    def readInstr(self, memDir):
        result = self.cache.read(memDir)

        # Si la lectura fue un hit no se realiza ninguna accion
        if result[0] == CacheAlert.rdHit:
            self.outQueue.put(None)
            self.outQueue.put(None)
            return

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
