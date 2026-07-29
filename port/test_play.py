"""Uji headless mode PLAY: mulai goal 1, isi slot dgn jawaban benar, tangkap frame."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga
from main import Game, MECH_TYPES, PLAY
from cc import assets

pygame.init()
g = Game(assets.find_data_dir())
g.start_play(1)
fb = cga.make_framebuffer()


def shot(name):
    g.draw(fb)
    big = pygame.transform.scale(fb, (cga.WIDTH * 3, cga.HEIGHT * 3))
    pygame.image.save(big, os.path.join(os.path.dirname(__file__), name))
    print(name, "score=%d" % g.score, "msg=", g.message)


shot("play_0_empty.png")

# Isi setiap slot dgn jawaban benar (cari indeks part yg cocok)
type_to_part = {t: i for i, (t, _) in enumerate(MECH_TYPES)}
# uji juga jawaban SALAH dulu di slot 0
g.cur_slot = 0
g.cur_part = (type_to_part[g.slots[0]["correct"]] + 1) % len(MECH_TYPES)
g._place()
shot("play_1_wrong.png")

# lalu benar untuk semua slot
for i, s in enumerate(g.slots):
    if s["filled"] is not None:
        continue
    g.cur_slot = i
    g.cur_part = type_to_part[s["correct"]]
    g._place()
shot("play_2_done.png")
pygame.quit()
