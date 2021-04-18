from computer.memory.memory_operation import MemoryOperation
from computer.directory.directory import Directory


class DirectoryControl:
    waiting = False

    def __init__(self, p_buses, mem_bus, update_buses):
        # Lista con los buses de los procesadores
        self.p_buses = p_buses

        # Bus para acceder a memoria
        self.mem_bus = mem_bus

        self.update_buses = update_buses

        self.associativity = 2
        self.num_blocks = 4
        self.num_sets = self.num_blocks / self.associativity

        # Estado de espera para cada procesador
        self.waiting_state = [False] * len(p_buses)

        self.directory = Directory(self.num_blocks, len(p_buses))
        self.cache = self.directory.cache

    def read_memory(self, mem_dir, node_id):
        # Se solicita la informacion a memoria principa;
        self.mem_bus.put([MemoryOperation.read, mem_dir])

        self.waiting_state[node_id] = True

    def write_memory(self, mem_dir, data):
        # Se solicita una operacion de escritura a memoria principal
        self.mem_bus.put([MemoryOperation.write, mem_dir, data])

    def get_limits_set(self, index_set):
        """
        Funcion para obtener los limites que componen el set solicitado
        :param index_set: numero del set solicitado
        :return: [index inicial, index final + 1]
        """
        return [index_set * self.num_sets,
                index_set * self.num_sets + self.associativity]

    def get_index_min_references(self, x, y):
        """
        Funcion que retorna el index del bloque con menor cantidad de
        referencias en un set
        :param x: index del primer elemento del set
        :param y: index del ultimo elemento del set + 1
        :return: index del bloque con menor cantidad de referencias
        """
        # Se establece un valor que va a ser mayor a la cantidad
        # de referencias posible
        min_references = len(self.p_buses) + 1
        index = x

        # Se recorre el set buscando el bloque con menos referencias
        for i in range(x, y):
            # Se obtiene la cantidad total de referencias del bloque
            block_references = sum(self.directory.processorRef[i])
            if block_references < min_references:
                min_references = block_references
                index = i

        return index

    def replaceBlock(self, mem_dir, data, newState, node_id):
        # Se obtiene el index del set en el que debe estar el bloque
        index_set = int(mem_dir % self.num_sets)

        # Se obtienen los limites del set
        x, y = self.get_limits_set(index_set)

        # Se obtiene el index del bloque a reemplazar
        index = self.get_index_min_references(x, y)

        # Se escribe la nueva informacion en el bloque
        self.directory.write(node_id, mem_dir, data, index, newState, self.update_buses)
