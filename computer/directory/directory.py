from computer.directory.directory_state import DirectoryState
from computer.directory.cache_L2 import L2
from computer.memory.memory_operation import MemoryOperation
from computer.node.cache.coherence_state import CoherenceState


class Directory:

    def __init__(self, num_blocks, num_processors,
                 update_buses, mem_bus):
        # Cantidad de procesadores
        self.num_processors = num_processors

        self.update_buses = update_buses
        self.mem_bus = mem_bus

        # Lista de estado para cada bloque
        self.blockState = [DirectoryState.uncached] * num_blocks

        # Vector que almacena las refencias de los procesadores
        self.processorRef = [[0] * num_processors] * num_blocks

        # Creacion de la cache L2
        self.cache = L2(num_blocks)

    def check_mem_dir(self, mem_dir):
        # Verifica si la direccion se encuentra en cache
        if mem_dir not in self.cache.blockDirMem:
            return False

        # Obtiene el index del elemento
        index = self.cache.blockDirMem.index(mem_dir)

        # Verifica si el estado del bloque es invalido
        state = self.blockState[index]
        if state == DirectoryState.uncached:
            return False

        return True

    def read(self, node_id, mem_dir):
        # Obtiene el index del elemento
        index = self.cache.blockDirMem.index(mem_dir)

        # Verifica si el estado del bloque es exclusivo
        state = self.blockState[index]
        if state == DirectoryState.exclusive:
            owner = self.processorRef[index].index(1)
            if owner != node_id:
                # Se actualiza el estado del bloque en L1 y L2
                self.update_buses[owner].put([mem_dir, CoherenceState.shared])
                self.blockState[index] = DirectoryState.shared
                # Se realiza un write back a memoria
                self.mem_write_back(index)

        # Se agrega la nueva referencia
        self.processorRef[index][node_id] = 1
        return self.cache.read(mem_dir)

    def write(self, node_id, mem_dir, data, index, newState):
        # Verifica si bloque es exclusivo y no es el mismo procesador el que escribe
        if self.blockState[index] == DirectoryState.exclusive and \
                self.processorRef[index].index(1) != node_id:
            # Se realiza un write back a memoria
            self.mem_write_back(index)

        # Notifica a las cache que deben invalidar el bloque
        for i in range(0, self.num_processors):
            if self.processorRef[index][i] == 1 and i != node_id:
                # Notificacion
                self.update_buses[i].put([mem_dir, CoherenceState.invalid])
                # Eliminacion de la referencia en el directorio
                self.processorRef[index][i] = 0

        # Se escribe el valor en cache
        self.cache.write(mem_dir, data, index)
        # Se actualiza la referencia y el estado en el directorio
        self.blockState[index] = newState
        self.processorRef[index][node_id] = 1

    def mem_write_back(self, index):
        # Se realiza un write back a memoria
        wb_data = self.cache.blockData[index]
        wb_mem_dir = self.cache.blockDirMem[index]
        self.mem_bus.put([MemoryOperation.write, wb_mem_dir, wb_data])