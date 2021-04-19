from interface.global_variables import *
from interface.draw_node import draw_node
from interface.draw_directory import draw_directory
from interface.draw_memory import draw_memory
from interface.computer_manager import *

# Title and icon
pygame.display.set_caption("Directory based cache coherence")

running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ex.exec()
                print("pressed")

    screen.fill((255, 255, 255))
    update_node_info()
    update_directory_info()
    update_memory_info()
    for i in range(0, 1):
        draw_node(15, 15,
                  cpu_instr[i],
                  cache_mem_dir[i],
                  cache_data[i],
                  cache_state[i])
    draw_directory(directory_mem_dir[0],
                   directory_data[0],
                   directory_state[0],
                   directory_processor[0])
    draw_memory(memory_data)
    pygame.display.update()

