from computer.memory.memory_operation import MemoryOperation


class DirectoryControl:
    waiting = False

    def __init__(self, p_buses, mem_bus):
        # Lista con los buses de los procesadores
        self.p_buses = p_buses

        # Bus para acceder a memoria
        self.mem_bus = mem_bus

        # Estado de espera para cada procesador
        self.waiting_state = [False] * len(p_buses)

    def read_memory(self, mem_dir, node_id):
        # Se solicita la informacion a memoria principa;
        self.mem_bus.put([MemoryOperation.read, mem_dir])

        self.waiting_state[node_id] = True

    def write_memory(self, mem_dir, data):
        # Se solicita una operacion de escritura a memoria principal
        self.mem_bus.put([MemoryOperation.write, mem_dir, data])
