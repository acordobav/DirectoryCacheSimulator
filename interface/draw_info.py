from interface.global_variables import pygame, space_y, screen
from interface.font import font, font_bold
from interface.colors import black


def draw_info(operation_mode, current_stage, clk):
    x = 15
    y = 600

    # Ciclos de reloj
    clk_text = font_bold.render("CLK: " + str(clk), True, black)
    screen.blit(clk_text, (x, y))

    # Modo de operacion
    y += 30
    operation_mode_text = font_bold.render("Modo de operación: " + operation_mode,
                                           True, black)
    screen.blit(operation_mode_text, (x, y))

    # Etapa actual
    # y += 30
    # stage_text = font_bold.render("Etapa: " + current_stage, True, black)
    # screen.blit(stage_text, (x, y))
