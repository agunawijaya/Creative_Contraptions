import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
# MENU -> Mix Up (menu#3) -> LEVEL (Apprentice) -> GOAL -> goal1
g.key(pygame.K_RETURN)                        # TITLE->MENU
for _ in range(3): g.key(pygame.K_DOWN)      # sel=3 Mix Up
g.key(pygame.K_RETURN)                        # ->LEVEL
g.key(pygame.K_RETURN)                        # Apprentice -> GOAL
g.key(pygame.K_RETURN)                        # goal1 -> start_play(both)
print("state=%d fill_mode=%s slots=%d palette=%d timer=%s level=%d" %
      (g.state, g.fill_mode, len(g.slots), len(g.palette), g.timer, g.level))
narch = {}
for s in g.slots: narch[s["arch"]] = narch.get(s["arch"], 0) + 1
print("slot per arch:", narch)
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\mixup_start.png")
# isi semua benar (cari palette entry yg id-nya cocok)
def pal_of(idm):
    for i, p in enumerate(g.palette):
        if idm in p[1]: return i
    return None
for i, s in enumerate(g.slots):
    c = pal_of(s["correct"])
    if c is not None:
        g.cur_slot = i; g.cur_part = c; g.key(pygame.K_RETURN)
won = all(s["filled"] == s["correct"] for s in g.slots)
print("terisi benar:", won, "skor sebelum SPACE:", g.score)
g.key(pygame.K_SPACE)
print("SPACE -> state=%d (win?) skor=%d (termasuk bonus waktu)" % (g.state, g.score))
# timer countdown cek
g.timer = 3.0; g.state = main.PLAY; g.running = False
for _ in range(120): g.tick()
print("timer setelah ~4 detik tick:", round(g.timer, 1), "msg:", g.message)
pygame.quit()
