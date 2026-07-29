import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
pygame.init()
graph = assets.Archive(os.path.join(assets.find_data_dir(), "GRAPH"))
CH = {(0, 0, 170): "|", (0, 170, 170): ".", (170, 0, 170): "O", (170, 170, 170): "#"}
for idx in (469, 470):
    s = graph.sprite_by_idx(idx)
    print("=== %d (%dx%d) ===" % (idx, s.get_width(), s.get_height()))
    for y in range(s.get_height()):
        print("".join(CH.get(tuple(s.get_at((x, y)))[:3], "?") for x in range(s.get_width())))
pygame.quit()
