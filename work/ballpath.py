"""Ekstrak jalur bola dari skrip ANIMATE (op0x00 waypoint) + overlay ke contraption.
Uji semantik: op0x03/0x0C = set posisi basis; op0x00 = bola di basis+(dx,dy)."""
import os
import sys
import struct
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from cc import cga, assets
from main import Game

D = assets.find_data_dir()
b = open(os.path.join(D, "ANIMATE"), "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]


def sgn(v):
    return v - 0x100 if v >= 0xc8 else v


def parse_points(script):
    """Kembalikan daftar titik bola (x,y) absolut, mengikuti basis dari op0x03/0x0C."""
    i, nn = 0, len(script)
    bx = by = 0
    pts = []
    while i < nn:
        op = script[i]; i += 1
        if op == 0xFF:
            break
        if op == 0x00:                       # daftar (dx,dy) bola
            while i + 1 < nn and script[i] != 0xFF:
                dx = sgn(script[i]); dy = sgn(script[i + 1]); i += 2
                pts.append((bx + dx, by + dy))
            i += 1
        elif op == 0x08:                     # 1 titik bola
            if i + 1 < nn:
                pts.append((bx + sgn(script[i]), by + sgn(script[i + 1]))); i += 2
        elif op in (0x03, 0x0C):             # set basis (x,y)
            if i + 1 < nn:
                bx = sgn(script[i]); by = sgn(script[i + 1]); i += 2
        elif op == 0x01:                     # daftar sprite frame -> skip s/d ff
            while i < nn and script[i] != 0xFF:
                i += 1
            i += 1
        elif op == 0x02:
            i += 1
        elif op == 0x04:                     # sound variabel
            mode = script[i]; i += 1
            if mode == 1:
                i += 6
            elif mode in (2, 3):
                while i + 1 < nn and not (script[i] == 0xFF and script[i + 1] == 0xFF):
                    i += 1
                i += 2
        elif op in (0x07, 0x09):
            i += 1
        elif op in (0x0A,):
            i += 2
        elif op == 0x11:
            i += 4
        elif op in (0x05, 0x06, 0x0D, 0x0E, 0x0F, 0x10):
            pass
        else:
            break
    return pts


pygame.init()
g = Game(D)
fb = cga.make_framebuffer()
g.chosen_goal = 1
# latar contraption 1
var = g.goals[1][0]
for (y, x, t) in var["zany"]:
    r = g.graph.first_of_major(t)
    if r:
        fb.blit(g.graph.sprite(r), (x, y))
for (y, x, t) in var["mech"]:
    r = g.mechs.first_of_major(t)
    if r:
        fb.blit(g.mechs.sprite(r), (x, y))

# index ANIMATE by id_major
anim_by_major = {}
for (a, mi, h, w, f, ln, off) in recs:
    if ln:
        anim_by_major.setdefault(a, []).append((off, ln))

# untuk tiap part (zany+mech) goal 1: mainkan skrip id_major==tipe relatif ke posisinya
allpts = []
parts = [(y, x, t) for (y, x, t) in var["zany"]] + [(y, x, t) for (y, x, t) in var["mech"]]
for (py, px, typ) in parts:
    for (off, ln) in anim_by_major.get(typ, []):
        for (dx, dy) in parse_points(b[off:off + ln]):
            allpts.append((px + dx, py + dy))
print("titik bola terkumpul (per-part): %d" % len(allpts))
inb = [(x, y) for (x, y) in allpts if 0 <= x < 320 and 0 <= y < 200]
print("dalam layar: %d  contoh: %s" % (len(inb), inb[:12]))
for (x, y) in inb:
    pygame.draw.circle(fb, cga.PALETTE[2], (x, y), 2)
big = pygame.transform.scale(fb, (960, 600))
pygame.image.save(big, r"C:\Projects\Creative_Contraptions\work\ballpath.png")
pygame.quit()
print("-> ballpath.png")
