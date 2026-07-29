"""Render animasi bola di PORT: contraption statis + bola menyusuri jalur tervalidasi.
Fase gulir (sprite 0x5e6) lalu fase fisika (bola kecil) -> GIF."""
import os, sys, json, struct
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from PIL import Image
from cc import cga, assets

GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
CAP = r"C:\Projects\Creative_Contraptions\work\emu_caps"
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))

draws = json.load(open(os.path.join(os.path.dirname(__file__), "cc", "draws", "draws_goal%d.json" % GOAL)))
dorder = json.load(open(os.path.join(CAP, "draworder_goal%d.json" % GOAL)))
physics = json.load(open(os.path.join(CAP, "ball_mode2_goal%d.json" % GOAL)))
roll = [(x, y) for (sptr, x, y, w, h) in dorder if sptr == 0x05e6]

# sprite bola gulir 0x5e6 (16x8) dari file bin
ballbin = open(os.path.join(CAP, "ball_sprite_5e6.bin"), "rb").read()
ballspr = pygame.Surface((16, 8))
for row in range(8):
    for cb in range(4):
        byte = ballbin[row * 4 + cb]
        for p in range(4):
            ballspr.set_at((cb * 4 + p, row), cga.PALETTE[(byte >> (6 - 2 * p)) & 3])
ballspr.set_colorkey(cga.PALETTE[cga.BG_INDEX])


def bg():
    fb = cga.make_framebuffer()
    for d in draws:
        if d["idx"] < 0:
            continue
        spr = (graph if d["arch"] == "GRAPH" else mechs).sprite_by_idx(d["idx"])
        if spr:
            fb.blit(spr, (d["x"], d["y"]))
    return fb


frames = []
# fase gulir: bola 0x5e6 di tiap posisi
for (x, y) in roll:
    fb = bg()
    fb.blit(ballspr, (x, y))
    frames.append(fb.copy())
# fase fisika: bola kecil (3x3 putih) di tiap posisi
for (x, y) in physics:
    fb = bg()
    pygame.draw.circle(fb, cga.PALETTE[3], (x, y), 2)
    frames.append(fb.copy())

imgs = [Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(f, (640, 400)), "RGB")) for f in frames]
out = r"C:\Projects\Creative_Contraptions\work\port_ball_goal%d.gif" % GOAL
imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=60, loop=0)
print("frames=%d -> %s" % (len(imgs), out))
pygame.quit()
