import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN)             # TITLE->MENU
g.draw(fb)
Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")).save(r"C:\Projects\Creative_Contraptions\work\menu_port.png")
print("menu rendered. icons loaded:", [i is not None for i in g.menu_icons])
# cek: Fill in Mechanisms (sel 1) -> LEVEL
g.sel = 1; g._choose()
print("Fill Mech -> state=%d (LEVEL=%d)" % (g.state, main.LEVEL))
g.sel = 1; g._choose()   # Master Builder -> GOAL
print("  level=%d -> state=%d (GOAL=%d)" % (g.level, g.state, main.GOAL))
g.key(pygame.K_RETURN)   # goal1 -> start_play
print("  -> state=%d fill_mode=%s" % (g.state, g.fill_mode))
# cek Fill Zany juga lewat level
g.state = main.MENU; g.sel = 2; g._choose()
print("Fill Zany -> state=%d (LEVEL)" % g.state)
pygame.quit()
