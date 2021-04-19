from computer.memory.memory_operation import MemoryOperation
from computer.directory.directory import Directory
from computer.directory.directory_state import DirectoryState
from computer.node.cache.cache_alert import CacheAlert


class DirectoryControl:
    waiting = False

    def __init__(self, p_buses, mem_bus, update_buses, num_processors, replace_bus):
        """
        Constructor
        :param p_buses: lista con los buses para comunicarse con los procesadores,
                        cada elemento de la lista es una sublista, donde la primera
                        posicion es el bus donde el procesador escribe, y la segunda
                        es el bus donde el procesador lee
        :param mem_bus:
        :param update_buses:
        """
        # Lista con los buses de los procesadores
        self.p_buses = p_buses

        # Bus para acceder a memoria
        self.mem_bus = mem_bus

        self.replace_bus = replace_bus
        self.update_buses = update_buses
        self.num_processors = num_processors
        self.associativity = 2
        self.num_blocks = 4
        self.num_sets = self.num_blocks / self.associativity

        self.directory = Directory(self.num_blocks, num_processors,
                                   update_buses, mem_bus[0])
        self.cache = self.directory.cache

        # Lista para manejar las solicitudes que esperan un resultado
        # de una solicitud a memoria principal
        self.pending_requests = [None] * num_processors

    def read_memory(self, mem_dir):
        # Se solicita la informacion a memoria principa;
        self.mem_bus[0].put([MemoryOperation.read, mem_dir])

    def write_memory(self, mem_dir, data):
        # Se solicita una operacion de escritura a memoria principal
        self.mem_bus[0].put([MemoryOperation.write, mem_dir, data])

    def get_limits_set(self, index_set):
        """
        Funcion para obtener los limites que componen el set solicitado
        :param index_set: numero del set solicitado
        :return: [index inicial, index final + 1]
        """
        return [int(index_set * self.num_sets),
                int(index_set * self.num_sets + self.associativity)]

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
        """
        Funcion para reemplazar un bloque de cache, se reemplaza
        el que tenga menos referencias
        :param mem_dir: direccion de memoria del bloque que se inserta
        :param data: informacion del bloque que se inserta
        :param newState: nuevo estado del bloque que se inserta
        :param node_id: nodo que levanto la alerta
        """
        # Se obtiene el index del set en el que debe estar el bloque
        index_set = int(mem_dir % self.num_sets)

        # Se obtienen los limites del set
        x, y = self.get_limits_set(index_set)

        # Se obtiene el index del bloque a reemplazar
        index = self.get_index_min_references(x, y)

        # Se escribe la nueva informacion en el bloque
        self.directory.write(node_id, mem_dir, data, index, newState)

    def handle_read(self, mem_dir, node_id, requested):
        """
        Funcion para manejar una alerta de lectura
        :param mem_dir: direccion de memoria que se lee
        :param node_id: nodo que realiza la solicitud
        :param requested: indica si la solicitud fue solicitada anteriormente
        """
        is_data_available = self.directory.check_mem_dir(mem_dir)

        # Se verifica que el dato se encuentre en memoria
        if not is_data_available and not requested:
            self.read_memory(mem_dir)
            self.pending_requests[node_id] = [CacheAlert.rdMiss, mem_dir]
            return

        if not is_data_available:
            return

        # Se marca la solicitud como atendida
        self.pending_requests[node_id] = None
        # Se lee el dato
        data = self.directory.read(node_id, mem_dir)
        # Se envia el dato al procesador
        bus = self.p_buses[node_id][1]
        bus.put(data)

    def handle_write(self, mem_dir, data, node_id):
        """
        Funcion para manejar una alerta de escritura
        :param mem_dir: direccion de memoria en donde se escribe
        :param data: informacion que se debe escribir
        :param node_id: nodo que realiza la solicitud
        """
        is_data_in_cache = self.directory.check_mem_dir(mem_dir)

        # Si dato no se encuentra en cache, se reemplaza un bloque
        if not is_data_in_cache:
            self.replaceBlock(mem_dir, data, DirectoryState.exclusive, node_id)

        # Si ya se encuentra en cache, se actualiza su valor
        index = self.directory.cache.blockDirMem.index(mem_dir)
        self.directory.write(node_id, mem_dir, data,
                             index, DirectoryState.exclusive)

    def handle_memory_response(self):
        """
        Funcion para atender las respuestas generadas por una
        solicitud enviada a memoria principal
        """
        # Se verifica si el bus esta vacio
        while not self.mem_bus[1].empty():
            # Se obtienen los datos enviados en la respuesta
            response = self.mem_bus[1].get()
            mem_dir = response[0]
            data = response[1]

            # Se obtiene el id del nodo que realizo la solicitud
            index = self.pending_requests.index([CacheAlert.rdMiss, mem_dir])

            # Se almacenan en la cache
            self.replaceBlock(mem_dir, data, DirectoryState.shared, index)

    def remove_reference(self, mem_dir, node_id):
        """
        Funcion para eliminar una referencia a un bloque del directorio
        :param mem_dir: direccion de memoria del bloque
        :param node_id: nodo que realiza la alerta
        :return:
        """
        if mem_dir not in self.directory.cache.blockDirMem:
            return

        # Se obtiene el index de la lista de referencias del bloque
        index = self.directory.cache.blockDirMem.index(mem_dir)

        # Se elimina la referencia
        self.directory.processorRef[index][node_id] = 0

        # Se verifica si las referencias totales son cero
        if sum(self.directory.processorRef[index]) == 0:
            # Se verifica si es necesario realizar un write back
            if self.directory.blockState[index] == DirectoryState.exclusive:
                self.write_memory(self.directory.cache.blockDirMem[index],
                                  self.directory.cache.blockData[index])

            # Se cambia el estado del bloque
            self.directory.blockState[index] = DirectoryState.uncached

    def handle_replace_alerts(self):
        """
        Funcion para atender todas las solicitud de reemplazo
        en las cache L1
        """
        for i in range(0, self.num_processors):
            bus = self.replace_bus[i]
            while not bus.empty():
                replace_action = bus.get()
                self.remove_reference(replace_action[1], i)

    def execute(self):
        # Se atienden alertas de reemplazo de datos en L1
        self.handle_replace_alerts()

        # Se atienden las respuestas enviadas por memoria principal
        self.handle_memory_response()

        # Se atienden alertas de datos
        for i in range(0, self.num_processors):
            request = self.pending_requests[i]
            if request is not None:
                # Se atiende la solicitud de lectura
                if request[0] == CacheAlert.rdMiss:
                    mem_dir = request[1]
                    self.handle_read(mem_dir, i, True)

            else:
                if not self.p_buses[i][0].empty():
                    request = self.p_buses[i][0].get()
                    request_type = request[0]
                    mem_dir = request[1]
                    if request_type == CacheAlert.rdMiss:
                        self.handle_read(mem_dir, i, False)

                    if request_type == CacheAlert.wrHit or CacheAlert.wrMiss:
                        data = request[2]
                        self.handle_write(mem_dir, data, i)

