import pygame
from interface.colors import *

# Initialize the pygame library
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Title and icon
pygame.display.set_caption("Directory based cache coherence")

running = True

# Font
font = pygame.font.Font("../assets/SegoeUI.ttf", 14)
font_bold = pygame.font.Font("../assets/SegoeUIBold.ttf", 14)

space_y = 28


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
    draw_node_element_rect(x, y, max_width, 120, "Cache L1")

    x += 10
    y += 5

    draw_cache_column(x+2, y, ["N", "0", "1"])
    draw_cache_column(x+25, y, ["Dir", "101", "001"])
    draw_cache_column(x+60, y, ["Dato", "10000", "AFJEJ"])
    draw_cache_column(x+110, y, ["Estado", "S", "M"])


def draw_cache_column(x, y, text):
    for i in range(0, len(text)):
        num_title = font.render(text[i], True, cpu_text_color)
        screen.blit(num_title, (x, y + space_y * (i + 1)))


def draw_node(x, y):
    background_rect = pygame.Rect(x-10, y-10, 190, 283)
    pygame.draw.rect(screen, node_background, background_rect)

    cpu_instr1 = ["P0: CALC", "P0: READ 0100", "P0: WRITE 1010; 10000"]
    draw_cpu(x, y, 0, cpu_instr1)

    mem_dir = [1, 2]
    data = [60124, 4828]
    state = ["I", "S"]

    draw_cache(x, y+140, mem_dir, data, state)


def show_score(x, y):
    text = font.render("Texto de prueba", True, (255, 255, 255))
    screen.blit(text, (x, y))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    draw_node(50, 50)
    draw_node(400, 50)
    pygame.display.update()

