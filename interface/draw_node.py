from interface.global_variables import pygame, space_y, screen
from interface.font import font, font_bold
from interface.colors import cpu_text_color, cpu_rect_background, \
                             cpu_rect_border, cpu_rect_aux, node_background, \
                             cpu_alert_background
from interface.conversions import dec_to_bin, dec_to_hex


def draw_alert_rect(x, y, alert):
    width = 170
    background_rect = pygame.Rect(x, y, width, 33)
    pygame.draw.rect(screen, cpu_alert_background, background_rect, 0, 10)

    title = font_bold.render(alert, True, cpu_text_color)

    title_width = title.get_width()
    screen.blit(title, (x + abs(width - title_width) / 2, y + 5))


def draw_node_element_rect(x, y, width, height, title_text):
    background_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, cpu_rect_background, background_rect)
    pygame.draw.rect(screen, cpu_rect_background, background_rect)
    pygame.draw.rect(screen, cpu_rect_border, background_rect, 4)

    title_rect = pygame.Rect(x, y, width, 30)
    pygame.draw.rect(screen, cpu_rect_border, title_rect)

    title = font_bold.render(title_text, True, cpu_text_color)

    title_width = title.get_width()
    screen.blit(title, (x + abs(width-title_width)/2, y + 5))


def draw_cpu(x, y, num, cpu_instr):
    max_width = 170
    draw_node_element_rect(x, y, max_width, 125, "Procesador " + str(num))

    x += 10
    y += 5

    for i in range(0, len(cpu_instr)):
        if i == len(cpu_instr)-1:
            instr_rect = pygame.Rect(x-3, y+space_y*(i+1), max_width-13, 24)
            pygame.draw.rect(screen, cpu_rect_aux, instr_rect, 0, 10)
            instr = font_bold.render(cpu_instr[i], True, cpu_text_color)
            screen.blit(instr, (x, y + space_y * (i + 1)))
        else:
            instr = font.render(cpu_instr[i], True, cpu_text_color)
            screen.blit(instr, (x, y+space_y*(i+1)))


def draw_cache(x, y, mem_dir, data, state):
    max_width = 170
    draw_node_element_rect(x, y, max_width, 120, "Caché L1")

    x += 10
    y += 5

    draw_cache_column(x+2, y, ["N", "0", "1"])
    draw_cache_column(x+25, y, ["Dir", dec_to_bin(mem_dir[0]), dec_to_bin(mem_dir[1])])
    draw_cache_column(x+60, y, ["Dato", dec_to_hex(data[0]), dec_to_hex(data[1])])
    draw_cache_column(x+110, y, ["Estado"] + state)


def draw_cache_column(x, y, text):
    for i in range(0, len(text)):
        num_title = font.render(text[i], True, cpu_text_color)
        screen.blit(num_title, (x, y + space_y * (i + 1)))


def draw_node(x, y, instr, mem_dir, data, state, alert, node_id):
    background_rect = pygame.Rect(x-5, y-5, 181, 272)
    pygame.draw.rect(screen, node_background, background_rect)

    draw_cpu(x, y, node_id, instr)

    draw_cache(x, y+140, mem_dir, data, state)

    draw_alert_rect(x, y+280, alert)
