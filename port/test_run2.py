"""Uji gerak bola halus: jalankan run, lacak posisi kontinu tiap tick, gambar jejak."""
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
t2p = {t: i for i, (t, _) in enumerate(MECH_TYPES)}
for i, s in enumerate(g.slots):
    g.cur_slot = i; g.cur_part = t2p[s["correct"]]; g._place()
g._play_key(pygame.K_SPACE)

# latar contraption (render sekali ke fb)
fb = cga.make_framebuffer()
g.ball_pos_backup = None
# kumpulkan jejak kontinu
trail = []
ticks = 0
while g.ball_i >= 0 and ticks < 5000:
    if g.ball_pos:
        trail.append((int(g.ball_pos[0]), int(g.ball_pos[1])))
    g.tick()
    ticks += 1
print("total tick (durasi run): %d, titik jejak: %d" % (ticks, len(trail)))

# gambar latar + jejak
g.ball_pos = None
g.draw(fb)
for (x, y) in trail:
    fb.set_at((x, y), cga.PALETTE[2])
big = pygame.transform.scale(fb, (960, 600))
pygame.image.save(big, os.path.join(os.path.dirname(__file__), "run_trail.png"))
pygame.quit()
print("-> run_trail.png")
