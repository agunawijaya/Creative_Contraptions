"""Template-match zany tiap goal ke record GRAPH benar (vs ground truth capture).
Output tabel {goal: {zany_index: record_idx}} + confidence."""
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
goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
GT = r"C:\Projects\Creative_Contraptions\work\gt"
BG = cga.PALETTE[cga.BG_INDEX]


def load_gt(g):
    im = Image.open(os.path.join(GT, "gt_goal%d.png" % g)).convert("RGB")
    return im


def score(spr, gt, ox, oy):
    w, h = spr.get_size()
    match = nonbg = 0
    for j in range(0, h, 1):
        for i in range(0, w, 1):
            c = spr.get_at((i, j))[:3]
            if c == BG:
                continue
            nonbg += 1
            X, Y = ox + i, oy + j
            if 0 <= X < 320 and 0 <= Y < 200 and gt.getpixel((X, Y)) == c:
                match += 1
    return (match / nonbg) if nonbg > 15 else 0


table = {}
GOALNAMES = {1: "Up&AtEm", 2: "HairCare", 3: "EasyEating", 4: "DogDays", 5: "CoolIt", 6: "LightsOut"}
for g in range(1, 7):
    if g not in goals:
        continue
    gt = load_gt(g)
    var = goals[g][0]
    table[g] = {}
    print("=== goal %d (%s) ===" % (g, GOALNAMES.get(g)))
    for zi, (y, x, typ) in enumerate(var["zany"]):
        best = None
        for ci in graph.by_major.get(typ, []):
            spr = graph.sprite(graph.records[ci])
            for oy in range(y - 5, y + 7):
                for ox in range(x - 5, x + 7):
                    s = score(spr, gt, ox, oy)
                    if best is None or s > best[0]:
                        best = (s, ci, ox - x, oy - y)
        if best:
            r = graph.records[best[1]]
            table[g][zi] = best[1]
            print("  zany#%d type=%d @(%d,%d) -> rec idx=%d id=%d.%d conf=%.0f%% off=(%+d,%+d)"
                  % (zi, typ, x, y, best[1], r["major"], r["minor"], 100 * best[0],
                     best[2], best[3]))
json.dump(table, open(os.path.join(os.path.dirname(__file__), "sprite_table.json"), "w"))
pygame.quit()
print("\nTabel -> sprite_table.json")
