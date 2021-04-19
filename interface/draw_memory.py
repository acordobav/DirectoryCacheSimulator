from interface.conversions import dec_to_hex
from interface.draw_node import draw_node_element_rect, draw_cache_column
from interface.conversions import dec_to_bin


def draw_memory(mem_data):
    x = 300
    y = 300

    draw_node_element_rect(x, y, 125, 285, "Memoria")

    x += 10
    y += 5
    draw_cache_column(x + 2, y, ["N", "0", "1", "2", "3",
                                 "4", "5", "6", "7"])
    draw_cache_column(x + 25, y, ["Dir",
                                  dec_to_bin(0),
                                  dec_to_bin(1),
                                  dec_to_bin(2),
                                  dec_to_bin(3),
                                  dec_to_bin(4),
                                  dec_to_bin(5),
                                  dec_to_bin(6),
                                  dec_to_bin(7)])
    draw_cache_column(x + 60, y, ["Dato",
                                  dec_to_hex(mem_data[0]),
                                  dec_to_hex(mem_data[1]),
                                  dec_to_hex(mem_data[2]),
                                  dec_to_hex(mem_data[3]),
                                  dec_to_hex(mem_data[4]),
                                  dec_to_hex(mem_data[5]),
                                  dec_to_hex(mem_data[6]),
                                  dec_to_hex(mem_data[7])])
