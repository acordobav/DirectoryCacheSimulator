from interface.global_variables import pygame, screen
from interface.colors import white
from interface.conversions import dec_to_bin, dec_to_hex
from interface.draw_node import draw_node_element_rect, draw_cache_column


def draw_directory(mem_dir, data, state, processors):
    x = 15
    y = 350
    draw_node_element_rect(x, y, 255, 175, "Caché L2 & Directorio")

    x += 10
    y += 5
    draw_cache_column(x+2, y, ["N", "0", "1", "2", "3"])
    draw_cache_column(x+25, y, ["Dir",
                                dec_to_bin(mem_dir[0]),
                                dec_to_bin(mem_dir[1]),
                                dec_to_bin(mem_dir[2]),
                                dec_to_bin(mem_dir[3])])
    draw_cache_column(x+60, y, ["Dato",
                                dec_to_hex(data[0]),
                                dec_to_hex(data[1]),
                                dec_to_hex(data[2]),
                                dec_to_hex(data[3])])
    pygame.draw.line(screen, white, (x + 110, y + 35), (x + 110, y + 160))

    draw_cache_column(x+120, y, ["Estado"] + state)
    draw_cache_column(x+170, y, ["Procesador"] + processors)
