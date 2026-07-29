import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
# MENU -> Fill in Zany Objects (menu#2) -> GOAL -> goal1
g.key(pygame.K_RETURN)               # TITLE->MENU
g.key(pygame.K_DOWN); g.key(pygame.K_DOWN)   # sel=2 (Fill Zany)
g.key(pygame.K_RETURN)               # ->GOAL
g.key(pygame.K_RETURN)               # goal1 -> start_play(zany)
print("state=%d fill_mode=%s slots=%d palette=%d" %
      (g.state, g.fill_mode, len(g.slots), len(g.palette)))
print("slot correct types:", [s["correct"] for s in g.slots])
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\zany_start.png")
# isi semua benar
def pal_of(idm):
    for i, entry in enumerate(g.palette):
        if idm in entry[1]: return i
    return None
for i, s in enumerate(g.slots):
    c = pal_of(s["correct"])
    if c is not None:
        g.cur_slot = i; g.cur_part = c; g.key(pygame.K_RETURN)
won = all(s["filled"] == s["correct"] for s in g.slots)
print("terisi benar:", won, "skor:", g.score)
g.key(pygame.K_SPACE)
print("SPACE -> state=%d (PLAYANIM=%d win?)" % (g.state, main.PLAYANIM))
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\zany_win.png")
pygame.quit()
