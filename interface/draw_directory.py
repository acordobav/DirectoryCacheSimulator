from interface.global_variables import pygame, screen, space_y
from interface.font import font_bold
from interface.colors import cpu_alert_background, white
from interface.conversions import dec_to_bin, dec_to_hex
from interface.draw_node import draw_node_element_rect, draw_cache_column


def draw_mem_operations(x, y, operations):
    width = 170
    background_rect = pygame.Rect(x, y, width, 132)
    pygame.draw.rect(screen, cpu_alert_background, background_rect, 0, 10)
    for i in range(0, len(operations)):
        font = font_bold.render(operations[i], True, white)
        text_width = font.get_width()
        screen.blit(font, (x + abs(width - text_width) / 2, (y+10) + space_y * (i)))


def draw_directory(mem_dir, data, state, processors, mem_operations):
    x = 15
    y = 350
    draw_node_element_rect(x, y, 255, 175, "Caché L2 & Directorio")

    draw_mem_operations(x+285, y+25, mem_operations)

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
