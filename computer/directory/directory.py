from computer.directory.directory_state import DirectoryState
from computer.directory.cache_L2 import L2
from computer.node.cache.cache_alert import CacheAlert
from computer.node.cache.coherence_state import CoherenceState


class Directory:

    def __init__(self, num_blocks, num_processors):
        # Cantidad de procesadores
        self.num_processors = num_processors

        # Lista de estado para cada bloque
        self.blockState = [DirectoryState.uncached] * num_blocks

        # Vector que almacena las refencias de los procesadores
        self.processorRef = [[0] * num_processors] * num_blocks

        # Creacion de la cache L2
        self.cache = L2(num_blocks)

    def read(self, node_id, mem_dir, update_buses):
        # Verifica si la direccion se encuentra en cache
        if mem_dir not in self.cache.blockDirMem:
            return [CacheAlert.rdMiss, node_id]

        # Obtiene el index del elemento
        index = self.cache.blockDirMem.index(mem_dir)

        # Verifica el estado del bloque es invalido
        state = self.blockState[index]
        if state == DirectoryState.uncached:
            return [CacheAlert.rdMiss, node_id]

        # Verifica si el estado del bloque es exclusivo
        if state == DirectoryState.exclusive:
            owner = self.processorRef[index].index(1)
            if owner != node_id:
                update_buses[owner].put([mem_dir, CoherenceState.shared])
                self.blockState[index] = DirectoryState.shared

        # Se agrega la nueva referencia
        self.processorRef[index][node_id] = 1
        return [CacheAlert.rdHit, self.cache.read(mem_dir)]
