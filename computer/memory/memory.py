from computer.memory.memory_operation import MemoryOperation


class Memory:
    def __init__(self, mem_bus):
        """
        Constructor
        :param mem_bus: lista con el bus de entrada en la primera posicion,
                        y el bus de salida en la segunda posicion
        """
        self.mem_bus = mem_bus
        self.data = [0 for _ in range(8)]

    def execute(self):
        while not self.mem_bus[0].empty():
            request = self.mem_bus[0].get()
            mem_dir = request[1]

            if request[0] == MemoryOperation.read:
                self.read(mem_dir)
            else:
                data = request[2]
                self.write(mem_dir, data)

    def write(self, mem_dir, data):
        """
        Metodo para escribir en memoria
        :param mem_dir: direccion de memoria
        :param data: informacion a escribir
        """
        self.data[mem_dir] = data

    def read(self, mem_dir):
        """
        Metodo para leer de memoria
        :param mem_dir: direccion de memoria
        :return: dato leido
        """
        self.mem_bus[1].put([mem_dir, self.data[mem_dir]])
