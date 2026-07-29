"""Cocokkan tiap part goal 1 ke record GRAPH yang BENAR via template-matching
terhadap ground truth (frame asli). Ungkap aturan pemilihan sprite."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga, assets
from tools_ground_truth import recover_native

pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))

gt = recover_native(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png")
BG = cga.PALETTE[cga.BG_INDEX]


def score(rec, ox, oy):
    """Jumlah pixel non-bg sprite yg COCOK dgn ground truth pada offset (ox,oy)."""
    spr = graph.sprite(rec)
    w, h = spr.get_size()
    match = nonbg = 0
    for j in range(h):
        for i in range(w):
            c = spr.get_at((i, j))[:3]
            if c == BG:
                continue
            nonbg += 1
            X, Y = ox + i, oy + j
            if 0 <= X < 320 and 0 <= Y < 200 and gt.getpixel((X, Y)) == c:
                match += 1
    return match, nonbg


var = goals[1][0]
print("=== Cocokkan zany goal 1 ke record GRAPH terbaik (vs ground truth) ===")
for (y, x, typ) in var["zany"]:
    cands = graph.by_major.get(typ, [])
    best = None
    for ci in cands:
        rec = graph.records[ci]
        # cari offset terbaik di jendela kecil sekitar (x,y)
        for oy in range(y - 6, y + 8):
            for ox in range(x - 6, x + 8):
                m, nb = score(rec, ox, oy)
                if nb > 20 and (best is None or m / nb > best[0]):
                    best = (m / nb, rec, ox, oy, m, nb)
    if best:
        r = best[1]
        print("type=%2d @(%d,%d): record idx=%d id=%d.%d %dx%d  match=%.0f%% offset=(%+d,%+d)"
              % (typ, x, y, r["idx"], r["major"], r["minor"], r["w"], r["h"],
                 100 * best[0], best[2] - x, best[3] - y))
    else:
        print("type=%2d @(%d,%d): TAK ADA kandidat cocok" % (typ, x, y))
pygame.quit()
