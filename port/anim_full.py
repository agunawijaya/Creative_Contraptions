"""Render animasi PENUH goal di port: contraption + part beranimasi + bola, per-frame.
Pakai data frame-tagged dari emulator (anim_goal*, ballframes, draworder 0x5e6)."""
import os, sys, json
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
anim = json.load(open(os.path.join(CAP, "anim_goal%d.json" % GOAL)))
ballframes = json.load(open(os.path.join(CAP, "ballscreen_goal%d.json" % GOAL)))   # posisi LAYAR nyata
dorder = json.load(open(os.path.join(CAP, "draworder_goal%d.json" % GOAL)))
maxf = max([a["frame"] for a in anim] + [b[2] for b in ballframes])

ballbin = open(os.path.join(CAP, "ball_sprite_5e6.bin"), "rb").read()
ballspr = pygame.Surface((16, 8))
for row in range(8):
    for cb in range(4):
        for p in range(4):
            ballspr.set_at((cb * 4 + p, row), cga.PALETTE[(ballbin[row * 4 + cb] >> (6 - 2 * p)) & 3])
ballspr.set_colorkey(cga.PALETTE[cga.BG_INDEX])

# indeks per frame
anim_by_f = {}
for a in anim:
    anim_by_f.setdefault(a["frame"], []).append(a)
roll_by_f = {}
for (sptr, x, y, w, h, fr) in dorder:
    if sptr == 0x05e6:
        roll_by_f.setdefault(fr, []).append((x, y))
ball_by_f = {}
for (x, y, fr) in ballframes:
    ball_by_f.setdefault(fr, []).append((x, y))


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
for f in range(1, maxf + 1):
    fb = bg()
    for a in anim_by_f.get(f, []):
        if a["idx"] < 0:
            continue
        spr = (graph if a["arch"] == "GRAPH" else mechs).sprite_by_idx(a["idx"])
        if spr:
            fb.blit(spr, (a["x"], a["y"]))
    for (x, y) in roll_by_f.get(f, []):
        fb.blit(ballspr, (x, y))
    for (x, y) in ball_by_f.get(f, []):
        pygame.draw.circle(fb, cga.PALETTE[3], (x, y), 2)
    frames.append(fb.copy())

imgs = [Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(f, (640, 400)), "RGB")) for f in frames]
out = r"C:\Projects\Creative_Contraptions\work\port_full_goal%d.gif" % GOAL
imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=120, loop=0)
print("maxframe=%d frames=%d -> %s" % (maxf, len(imgs), out))
pygame.quit()
