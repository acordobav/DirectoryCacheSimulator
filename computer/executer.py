import threading
from queue import Queue
from computer.node.node import Node
from computer.directory.directory_control import DirectoryControl
from computer.memory.memory import Memory


def node_execution(condition_obj, node, finished):
    while True:
        # Espera por la senal de reloj
        condition_obj.acquire()
        condition_obj.wait()
        condition_obj.release()

        node.exec()
        finished.put(True)


class Executer:
    def __init__(self, num_processors):
        # Manejo de hilos
        self.cond = threading.Condition()

        self.num_processors = num_processors

        # Creacion de los nodos
        self.nodes = []
        p_buses = []
        update_buses = []
        notify_buses = []
        self.synQueue = Queue()
        for i in range(0, self.num_processors):
            inQueue = Queue()
            outQueue = Queue()
            p_buses.append([outQueue, inQueue])

            update = Queue()
            update_buses.append(update)

            notify = Queue()
            notify_buses.append(notify)

            node = Node(inQueue, outQueue, update, notify)
            t = threading.Thread(target=node_execution, args=(self.cond, node, self.synQueue,), daemon=True)
            t.start()

            self.nodes.append(node)

        # Creacion del directorio
        self.mem_bus = Queue()
        mem_bus = [self.mem_bus, Queue()]
        self.directory = DirectoryControl(p_buses,
                                          mem_bus,
                                          update_buses,
                                          self.num_processors,
                                          notify_buses)

        # Creacion de la memoria principal
        self.memory = Memory(mem_bus)

        # Datos de simulacion
        # self.stage = 1
        self.clk = 0

        # Operaciones de memoria
        self.mem_operations = []

    def exec(self):
        # Ejecucion de de los nodos
        # if self.stage == 1:
        self.clk += 1
        self.execute_nodes()
        # self.stage = 2

        # elif self.stage == 2:
        self.directory.execute()
        self.extract_mem_operations()
        # self.stage = 3

        # else:
        self.memory.execute()
        # self.stage = 1

    def execute_nodes(self):
        self.cond.acquire()
        self.cond.notify_all()
        self.cond.release()

        for i in range(0, self.num_processors):
            self.synQueue.get()

    def extract_mem_operations(self):
        self.mem_operations = []
        while not self.mem_bus.empty():
            self.mem_operations.append(self.mem_bus.get())

        for op in self.mem_operations:
            self.mem_bus.put(op)
