import random

from interface.global_variables import pygame, space_y, screen
from interface.colors import white, node_background, green
from interface.font import font_bold
from interface.conversions import dec_to_bin, dec_to_hex
from computer.executer import Executer
from computer.node.cpu.instr import InstrType

instr_modifier = [0, 0, 0, 0]
instr_type = ["calc", "read", "write"]
processor_name = ["P0", "P1", "P2", "P3"]


def write_text(x, y, text):
    text = font_bold.render(text, True, white)
    screen.blit(text, (x, y))


def draw_instr_modifier(mode):
    if mode:
        return

    x = 250
    y = 565

    width = 100
    heigh = 130

    # Background
    p_rect = pygame.Rect(x, y, width, heigh)
    pygame.draw.rect(screen, node_background, p_rect, 0, 10)

    # Button
    b_rect = pygame.Rect(360, 615, 75, 35)
    pygame.draw.rect(screen, green, b_rect, 0, 10)
    write_text(370, 620, "Agregar")

    x += 10
    y += 10

    # Nombre del procesador
    write_text(x, y, "P:")
    write_text(x + 40, y, processor_name[instr_modifier[0]])

    # Nombre de la instruccion
    write_text(x, y + space_y, "Instr:")
    write_text(x + 40, y + space_y, instr_type[instr_modifier[1]])

    if instr_modifier[1] < 1:
        return

    # Direccion de memoria
    write_text(x, y + space_y * 2, "Dir:")
    write_text(x + 40, y + space_y * 2, dec_to_bin(instr_modifier[2]))

    if instr_modifier[1] < 2:
        return

    # Dato
    write_text(x, y + space_y * 3, "Dato:")
    write_text(x + 40, y + space_y * 3, dec_to_hex(instr_modifier[3]))


def click_input(x, y, mode, ex):
    if mode:
        return

    x_min = 257
    x_max = 340

    # Click en el boton
    if 361 <= x <= 437 and 616 <= y <= 648:
        add_instr(ex)

    # Click fuera del area
    if not x_min <= x <= x_max:
        return

    # Click en el procesador
    if 574 <= y <= 596:
        instr_modifier[0] += 1
        if instr_modifier[0] >= 4:
            instr_modifier[0] = 0

    # Click en el tipo de instruccion
    if 600 <= y <= 624:
        instr_modifier[1] += 1
        if instr_modifier[1] >= 3:
            instr_modifier[1] = 0

    # Click en la direccion de memoria
    if 630 <= y <= 653:
        instr_modifier[2] += 1
        if instr_modifier[2] >= 8:
            instr_modifier[2] = 0

    # Click en el dato
    if 661 <= y <= 682:
        instr_modifier[3] += random.randrange(0, 2 ** 16 + 1)


def add_instr(ex):
    data = instr_modifier[3]
    mem_dir = instr_modifier[2]

    instr = [InstrType.calc]
    instr_t = instr_modifier[1]
    if instr_t == 1:
        instr = [InstrType.read, mem_dir]
    if instr_t == 2:
        instr = [InstrType.read, mem_dir, data]

    node_id = instr_modifier[0]

    ex.nodes[node_id].control.cpu.instr[1] = instr
    print(instr)
