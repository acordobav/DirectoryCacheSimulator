import time
from queue import Queue
from computer.node.node import Node
from computer.directory.directory_control import DirectoryControl
from computer.memory.memory import Memory


class Executer:
    def __init__(self):
        self.num_processors = 1
        # Creacion de los nodos
        self.nodes = []
        p_buses = []
        update_buses = []
        notify_buses = []
        for i in range(0, self.num_processors):
            inQueue = Queue()
            outQueue = Queue()
            p_buses.append([outQueue, inQueue])

            update = Queue()
            update_buses.append(update)

            notify = Queue()
            notify_buses.append(notify)

            self.nodes.append(Node(inQueue, outQueue, update, notify))

        # Creacion del directorio
        mem_bus = [Queue(), Queue()]
        self.directory = DirectoryControl(p_buses,
                                          mem_bus,
                                          update_buses,
                                          self.num_processors,
                                          notify_buses)

        # Creacion de la memoria principal
        self.memory = Memory(mem_bus)

    def exec(self):
        # Ejecucion de cada uno de los nodos
        for i in range(0, self.num_processors):
            self.nodes[i].exec()

        # time.sleep(2)

        self.directory.execute()

        # time.sleep(2)

        self.memory.execute()

