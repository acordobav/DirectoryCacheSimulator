class L2:

    def __init__(self, num_blocks):
        # Direccion de memoria para cada bloque
        self.blockDirMem = [0] * num_blocks

        # Informacion almacenada en cada bloque
        self.blockData = [0] * num_blocks

    def write(self, mem_dir, data, index):
        self.blockDirMem[index] = mem_dir
        self.blockData[index] = data

    def read(self, mem_dir):
        # Obtiene el index del elemento
        index = self.blockDirMem.index(mem_dir)

        return self.blockData[index]
