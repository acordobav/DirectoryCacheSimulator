from enum import Enum


class DirectoryState(Enum):
    modified = "DM"
    shared = "DS"
    invalid = "DI"


class L2():

    def __init__(self, blockNum, numProcessors):
        # Cantidad de bloques
        self.blockNum = blockNum

        # Lista de estado para cada bloque
        self.blockState = [DirectoryState.invalid] * blockNum

        # Direccion de memoria para cada bloque
        self.blockDirMem = [0] * blockNum

        # Informacion almacenada en cada bloque
        self.blockData = [0] * blockNum

        # Vector que almacena las refencias de los procesadores
        self.processorRef = [0] * numProcessors
