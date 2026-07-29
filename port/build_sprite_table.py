"""Bangun tabel sprite BENAR dari screenshot user (Fill in Mechanisms XX.png).
Matcher (terbukti 100% di goal1) mencari record GRAPH terbaik per zany + per mech-slot."""
import os
import sys
import json
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from PIL import Image
from cc import cga, assets

pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
SHOT = r"C:\Projects\Creative_Contraptions\sceenshots\Fill in Mechanisms %02d.png"
BG = cga.PALETTE[cga.BG_INDEX]
PAL = cga.PALETTE


def snap(rgb):
    return min(PAL, key=lambda c: sum((a - b) ** 2 for a, b in zip(rgb, c)))


def recover(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    sx, sy = w / 320.0, h / 200.0
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            out.putpixel((x, y), snap(im.getpixel((min(int(x * sx + sx / 2), w - 1),
                                                    min(int(y * sy + sy / 2), h - 1)))))
    return out


def best_record(arch, typ, x, y, gt, win=6):
    best = None
    for ci in arch.by_major.get(typ, []):
        spr = arch.sprite(arch.records[ci])
        w, h = spr.get_size()
        for oy in range(y - win, y + win + 1):
            for ox in range(x - win, x + win + 1):
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
                if nonbg > 12:
                    s = match / nonbg
                    if best is None or s > best[0]:
                        best = (s, ci, ox - x, oy - y)
    return best


table = {"zany": {}, "mech": {}}
for g in range(1, 7):
    gt = recover(SHOT % g)
    gt.save(os.path.join(os.path.dirname(__file__), "gtu_goal%d.png" % g))
    var = goals[g][0]
    table["zany"][str(g)] = {}
    table["mech"][str(g)] = {}
    print("=== goal %d ===" % g)
    for zi, (y, x, typ) in enumerate(var["zany"]):
        b = best_record(graph, typ, x, y, gt)
        if b:
            table["zany"][str(g)][str(zi)] = [b[1], b[2], b[3]]
            r = graph.records[b[1]]
            print("  zany#%d t=%d @(%d,%d) -> rec %d (id%d.%d) conf=%.0f%% off=(%+d,%+d)"
                  % (zi, typ, x, y, b[1], r["major"], r["minor"], 100 * b[0], b[2], b[3]))
    for mi, (y, x, typ) in enumerate(var["mech"]):
        b = best_record(mechs, typ, x, y, gt)
        if b:
            table["mech"][str(g)][str(mi)] = [b[1], b[2], b[3]]
            r = mechs.records[b[1]]
            print("  mech#%d t=%d @(%d,%d) -> rec %d (id%d.%d) conf=%.0f%%"
                  % (mi, typ, x, y, b[1], r["major"], r["minor"], 100 * b[0]))

json.dump(table, open(os.path.join(os.path.dirname(__file__), "cc", "sprite_table.json"), "w"))
pygame.quit()
print("\n-> cc/sprite_table.json")
