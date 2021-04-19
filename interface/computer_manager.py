from computer.executer import Executer
from computer.node.cache.coherence_state import CoherenceState
from computer.directory.directory_state import DirectoryState
from interface.conversions import instr_to_string

# Nodo
cpu_instr = [[], [], [], []]
cache_mem_dir = [[], [], [], []]
cache_data = [[], [], [], []]
cache_state = [[], [], [], []]

# Directorio
directory_mem_dir = [[]]
directory_data = [[]]
directory_state = [[]]
directory_processor = [[]]

# Memoria
memory_data = []

def update_node_info():
    for i in range(0, 1):
        # Conversion de las instrucciones
        instr_list = []
        for instr in ex.nodes[i].cpu.instr:
            instr_list.append(instr_to_string(instr, i))
        instr_list.append(instr_to_string(ex.nodes[i].control.instr,i))
        cpu_instr[i] = instr_list

        cache_mem_dir[i] = ex.nodes[i].cache.blockDirMem
        cache_data[i] = ex.nodes[i].cache.blockData

        # Conversion de los estados de la cache
        cach_states = []
        for state in ex.nodes[i].cache.blockState:
            if state == CoherenceState.shared:
                cach_states.append("S")
            elif state == CoherenceState.modified:
                cach_states.append("M")
            else:
                cach_states.append("I")
        cache_state[i] = cach_states


def update_directory_info():
    # global directory_mem_dir
    # global directory_data
    # global directory_state
    # global directory_processor

    directory_mem_dir[0] = ex.directory.directory.cache.blockDirMem
    directory_data[0] = ex.directory.cache.blockData

    state_list = []
    for state in ex.directory.directory.blockState:
        if state == DirectoryState.exclusive:
            state_list.append("DM")
        elif state == DirectoryState.shared:
            state_list.append("DS")
        else:
            state_list.append("DI")
    # print(state_list)
    directory_state[0] = state_list

    processor_ref = []
    refs = ex.directory.directory.processorRef
    for block in refs:
        ref = str(block[0]) # + str(block[1])  # + str(block[2]) + str(block[3])
        processor_ref.append(ref)
    directory_processor[0] = processor_ref


def update_memory_info():
    global memory_data
    memory_data = ex.memory.data


ex = Executer()
ex.exec()
update_node_info()
update_directory_info()
update_memory_info()
