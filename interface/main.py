from interface.global_variables import *
from interface.draw_node import draw_node
from interface.draw_directory import draw_directory
from interface.draw_memory import draw_memory
from interface.draw_info import draw_info
from interface.computer_manager import *
from threading import Thread
import time


# Title and icon
pygame.display.set_caption("Directory based cache coherence")

# Modo de operacion automatico
automatic_mode = False


def automatic_execute():
    global automatic_mode
    while True:
        if automatic_mode:
            ex.exec()
            update_node_info()
            update_directory_info()
            update_memory_info()
            update_info(automatic_mode)
        time.sleep(3)


t1 = Thread(target=automatic_execute, daemon=True)
t1.start()


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not automatic_mode:
                ex.exec()
                update_node_info()
                update_directory_info()
                update_memory_info()
                update_info(automatic_mode)
            if event.key == pygame.K_SPACE:
                automatic_mode = not automatic_mode
                update_info(automatic_mode)

    screen.fill((255, 255, 255))
    for i in range(0, p):
        draw_node(15 + (i * 200), 15,
                  cpu_instr[i],
                  cache_mem_dir[i],
                  cache_data[i],
                  cache_state[i],
                  cpu_alerts[i], i)

    draw_directory(directory_mem_dir[0],
                   directory_data[0],
                   directory_state[0],
                   directory_processor[0],
                   directory_mem_operations[0])
    draw_memory(memory_data[0])
    draw_info(operation_mode[0], current_stage[0], clk[0])
    pygame.display.update()

