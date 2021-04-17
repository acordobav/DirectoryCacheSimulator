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

    def write(self, node_id, mem_dir, data, update_buses):
        # Verifica si la direccion se encuentra en cache
        if mem_dir not in self.cache.blockDirMem:
            return [CacheAlert.wrMiss]

        # Obtiene el index del elemento
        index = self.cache.blockDirMem.index(mem_dir)

        # Notifica a las cache que deben invalidar el bloque
        for i in range(0, self.num_processors):
            if self.processorRef[index][i] == 1 and i != node_id:
                # Notificacion
                update_buses[i].put([mem_dir, CoherenceState.invalid])
                # Eliminacion de la referencia en el directorio
                self.processorRef[index][i] = 0

        # Se escribe el valor en cache
        self.cache.write(mem_dir, data, index)
        # Se actualiza la referencia y el estado en el directorio
        self.blockState[index] = DirectoryState.exclusive
        self.processorRef[index][node_id] = 1

        return [CacheAlert.wrHit]
