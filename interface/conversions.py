from computer.node.cpu.instr import InstrType


def dec_to_bin(num):
    binary = bin(num)[2:]

    if len(binary) < 3:
        for i in range(0, 3-len(binary)):
            binary = "0" + binary

    return binary


def dec_to_hex(num):
    hexadecimal = hex(num)[2:]
    for i in range(0, 5 - len(hexadecimal)):
        hexadecimal = "0" + hexadecimal
    return hexadecimal.upper()


def instr_to_string(instr, node_id):
    string_instr = "P" + str(node_id) + ": "
    instr_type = instr[0]
    if instr_type == InstrType.read:
        string_instr += "READ "
        string_instr += dec_to_bin(instr[1])
    elif instr_type == InstrType.write:
        string_instr += "WRITE "
        string_instr += dec_to_bin(instr[1]) + "; "
        string_instr += dec_to_hex(instr[2])
    else:
        string_instr += "CALC"

    return string_instr
