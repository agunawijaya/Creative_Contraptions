import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
# TITLE->MENU
g.key(pygame.K_RETURN)
# pilih "Fill in Mechanisms" (menu#1)
g.key(pygame.K_DOWN); g.key(pygame.K_RETURN)   # ->GOAL
g.key(pygame.K_RETURN)                          # pilih goal1 -> start_play (Fill)
print("state=", g.state, "mode=", g.mode, "PLAY=", main.PLAY)
print("jumlah slot=", len(g.slots))
for i, s in enumerate(g.slots):
    print("  slot", chr(0x41+i), "pos=(%d,%d)" % (s["x"], s["y"]), "correct_type=", s["correct"], "filled=", s["filled"])
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\fill_start.png")
print("-> fill_start.png")
pygame.quit()
