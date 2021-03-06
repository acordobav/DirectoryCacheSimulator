from computer.node.cache.coherence_state import CoherenceState
from computer.node.cache.cache_alert import CacheAlert


class L1:

    def __init__(self, blockNum):
        # Cantidad de bloques
        self.blocks = blockNum

        # Lista de estado para cada bloque
        self.blockState = [CoherenceState.invalid] * blockNum

        # Direccion de memoria para cada bloque
        self.blockDirMem = [0 for _ in range(blockNum)]

        # Informacion almacenada en cada bloque
        self.blockData = [0 for _ in range(blockNum)]

    def set_state(self, dir_mem, state):
        if dir_mem not in self.blockDirMem:
            return

        index = self.blockDirMem.index(dir_mem)
        if not self.blockState[index] == CoherenceState.invalid:
            self.blockState[index] = state

    def read(self, dirMem):
        # Verifica si la direccion se encuentra en cache
        if dirMem not in self.blockDirMem:
            return [CacheAlert.rdMiss]

        # Obtiene el index del elemento
        index = self.blockDirMem.index(dirMem)

        # Verifica el estado del bloque
        if self.blockState[index] == CoherenceState.invalid:
            return [CacheAlert.rdMiss]

        # Retorna el valor almacenado en cache
        return [CacheAlert.rdHit, self.blockData[index]]

    def write(self, dirMem, data, state):
        # Verifica si la direccion se encuentra en cache
        if dirMem not in self.blockDirMem:
            return [CacheAlert.wrMiss]

        # Obtiene el index del elemento
        index = self.blockDirMem.index(dirMem)

        # Se verifica si el bloque es invalido
        if self.blockState[index] == CoherenceState.invalid:
            return [CacheAlert.wrMiss]

        # Se actualiza el valor de data y estado en el index
        self.blockData[index] = data
        self.blockState[index] = state

        return [CacheAlert.wrHit]

    def replace(self, memDir, data, state, index):
        self.blockState[index] = state
        self.blockDirMem[index] = memDir
        self.blockData[index] = data
