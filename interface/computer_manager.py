from computer.executer import Executer
from computer.node.cache.coherence_state import CoherenceState
from computer.directory.directory_state import DirectoryState
from interface.conversions import instr_to_string, alert_to_string

# Nodo
cpu_instr = [[], [], [], []]
cache_mem_dir = [[], [], [], []]
cache_data = [[], [], [], []]
cache_state = [[], [], [], []]
cpu_alerts = ["", "", "", ""]

# Directorio
directory_mem_dir = [[]]
directory_data = [[]]
directory_state = [[]]
directory_processor = [[]]

# Memoria
memory_data = [[]]

# Modo de operacion
operation_mode = ["Manual"]
current_stage = ["Nodo"]
clk = [1]


def update_node_info():
    for i in range(0, 1):
        # Conversion de las instrucciones
        instr_list = []
        for instr in ex.nodes[i].cpu.instr:
            instr_list.append(instr_to_string(instr, i))
        instr_list.append(instr_to_string(ex.nodes[i].control.instr, i))
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

        alert = ex.nodes[i].control.alert
        cpu_alerts[i] = alert_to_string(alert)


def update_directory_info():
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
        ref = str(block[0])  # + str(block[1])  # + str(block[2]) + str(block[3])
        processor_ref.append(ref)
    directory_processor[0] = processor_ref


def update_memory_info():
    memory_data[0] = ex.memory.data


def update_info(mode):
    # Etapa
    stage = ex.stage
    if stage == 2:
        current_stage[0] = "Nodos"
    elif stage == 3:
        current_stage[0] = "Directorio"
    else:
        current_stage[0] = "Memoria"

    # CLK
    clk[0] = ex.clk

    # Modo de operacion
    if mode:
        operation_mode[0] = "Automatico"
    else:
        operation_mode[0] = "Manual"


ex = Executer()
update_node_info()
update_directory_info()
update_memory_info()
