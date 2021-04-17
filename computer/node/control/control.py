from computer.node.cpu.instr import InstrType
from computer.node.cache.cache_L1 import CacheAlert, CoherenceState
from computer.node.control.replace_action import ReplaceAction


class Control:
    alert = []

    def __init__(self, cpu, cache, inQueue, outQueue, update, notify):
        self.cpu = cpu
        self.cache = cache
        self.inQueue = inQueue
        self.outQueue = outQueue
        self.update = update
        self.notify = notify
        self.waiting = False

    def execute(self):
        if not self.waiting:
            # Si el procesador no esta esperando el resultado
            # de una solicitud a L2 se ejecuta una instruccion
            self.execInstr()

        else:
            # Se verifica si la respuesta ya fue generada
            if not self.inQueue.empty():
                # Se procesa la respuesta
                self.execRequestResponse()

    def execRequestResponse(self):
        # Se procesa la respuesta
        result = self.inQueue.get()

        if self.alert[0] == CacheAlert.rdMiss:
            # Se escribe el valor en cache
            memDir = self.alert[1]
            self.replaceCacheBlock(memDir, result, CoherenceState.shared)

    def execInstr(self):
        # Se obtiene una instruccion de la cola
        instr = self.cpu.popInstr()

        if instr[0] == InstrType.read:
            self.readInstr(instr[1])

        elif instr[0] == InstrType.write:
            self.writeInstr(instr[1], instr[2])

        else:
            self.calcInstr()

        # Se genera una nueva instruccion
        # self.cpu.addInstr()

    def calcInstr(self):
        # self.outQueue.put(None)
        # self.outQueue.put(None)
        pass

    def writeInstr(self, memDir, data):
        result = self.cache.write(
            memDir,
            data,
            CoherenceState.modified)

        # Si la escritura fue un hit no se realiza ninguna accion
        if result[0] == CacheAlert.wrHit:
            self.alert = [CacheAlert.wrHit, memDir, data]
            self.outQueue.put(self.alert)
            # self.outQueue.put(None)
            return

        # Se notifica al directorio que ocurrio un wrMiss
        self.alert = [CacheAlert.wrMiss, memDir, data]
        self.outQueue.put(self.alert)
        # self.inQueue.get()

        # Se escribe el valor en cache
        self.replaceCacheBlock(memDir, data, CoherenceState.modified)

    def readInstr(self, memDir):
        result = self.cache.read(memDir)

        # Si la lectura fue un hit no se realiza ninguna accion
        if result[0] == CacheAlert.rdHit:
            # self.outQueue.put(None)
            # self.outQueue.put(None)
            return

        # Se espera para obtener el valor de la cache L2
        self.alert = [CacheAlert.rdMiss, memDir]
        self.outQueue.put(self.alert)

        self.waiting = True

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
        self.notify.put([replaceAction, oldMemDir])

        # Se reemplaza el bloque
        self.cache.replace(memDir, data, newState, index)

        return True
