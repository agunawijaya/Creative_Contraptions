import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
random.seed(7)
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()

# lewati semua state & tick tanpa error
states = [main.TITLE, main.MENU, main.LEVEL, main.GOAL, main.CONTRAPTION,
          main.REVIEW, main.REVIEW_DETAIL]
for st in states:
    g.state = st
    for _ in range(3):
        g.tick(); g.draw(fb)
    print("state", st, "OK")

# PLAY tiap mode + tekan SPACE (menang & gagal) tanpa error
for fill in ("mech", "zany", "both"):
    g.start_play(1, fill=fill)
    for _ in range(5):
        g.tick(); g.draw(fb)
    # isi salah 1 -> SPACE (jalur gagal/pesan) lalu tick
    g.key(pygame.K_SPACE)
    for _ in range(30):
        g.tick(); g.draw(fb)
    print("PLAY fill=%s SPACE OK (state=%d)" % (fill, g.state))

# menang penuh v0 mech -> PLAYANIM jalan
for _ in range(50):
    g.start_play(1, fill="mech")
    if g.cur_variant == 0:
        break
for i, s in enumerate(g.slots):
    for pi, p in enumerate(g.palette):
        if s["correct"] in p[1]:
            g.cur_slot = i; g.cur_part = pi; g.key(pygame.K_RETURN); break
g.key(pygame.K_SPACE)
for _ in range(80):
    g.tick(); g.draw(fb)
print("WIN v0 -> state=%d (PLAYANIM=%d) frames=%d" % (g.state, main.PLAYANIM, len(g.anim_frames)))
print("SMOKE OK")
pygame.quit()
