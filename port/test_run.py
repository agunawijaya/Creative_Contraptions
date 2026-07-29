"""Uji headless: isi goal 1, RUN, tangkap bola di beberapa titik sepanjang jalur."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga, assets
from main import Game, MECH_TYPES

pygame.init()
g = Game(assets.find_data_dir())
g.start_play(1)
# isi semua slot dgn benar
t2p = {t: i for i, (t, _) in enumerate(MECH_TYPES)}
for i, s in enumerate(g.slots):
    g.cur_slot = i; g.cur_part = t2p[s["correct"]]; g._place()
# mulai run
g._play_key(pygame.K_SPACE)
print("panjang jalur bola:", len(g.ball_path))

fb = cga.make_framebuffer()
N = len(g.ball_path)
shots = [int(N * f) for f in (0.15, 0.45, 0.8)] if N else []
frame = 0
saved = 0
while g.ball_i >= 0 and frame < N + 2:
    if saved < len(shots) and frame == shots[saved]:
        g.draw(fb)
        big = pygame.transform.scale(fb, (960, 600))
        pygame.image.save(big, os.path.join(os.path.dirname(__file__), "run_%d.png" % saved))
        print("run_%d.png @frame %d ball=%s" % (saved, frame, g.ball_path[g.ball_i]))
        saved += 1
    g.tick()
    frame += 1
pygame.quit()
