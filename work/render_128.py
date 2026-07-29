import os, sys, json
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
d = json.load(open(r"C:\Projects\Creative_Contraptions\work\emu_caps\draws_goal128.json"))
print("goal128 draws:")
for e in d:
    a = graph if e["arch"] == "GRAPH" else (mechs if e["arch"] == "MECHS" else None)
    mj = a.records[e["idx"]]["major"] if a and e["idx"] >= 0 else None
    print("  ", e["arch"], "idx", e["idx"], "(%d,%d)" % (e["x"], e["y"]), "%dx%d" % (e["w"], e["h"]), "major", mj)
fb = cga.make_framebuffer(); fb.fill(cga.PALETTE[cga.BG_INDEX])
for e in d:
    if e["idx"] < 0: continue
    spr = (graph if e["arch"] == "GRAPH" else mechs).sprite_by_idx(e["idx"])
    if spr: fb.blit(spr, (e["x"], e["y"]))
Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")).save(r"C:\Projects\Creative_Contraptions\work\render_128.png")
print("-> render_128.png")
pygame.quit()
