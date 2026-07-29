import os, sys, json, struct
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
G = int(sys.argv[1]) if len(sys.argv) > 1 else 1
draws = json.load(open(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal%d.json" % G))
fb = cga.make_framebuffer()
for d in draws:
    if d["idx"] < 0: continue
    spr = (graph if d["arch"] == "GRAPH" else mechs).sprite_by_idx(d["idx"])
    if spr: fb.blit(spr, (d["x"], d["y"]))

# roll-left (0x5e6) dari draworder
dorder = json.load(open(r"C:\Projects\Creative_Contraptions\work\emu_caps\draworder_goal%d.json" % G))
roll = [(x+8, y+4) for (sptr, x, y, w, h, *rest) in dorder if sptr == 0x05e6]   # center sprite 16x8
# physics ball — posisi LAYAR sebenarnya (VRAM), bukan koord logis
ball = [(p[0], p[1]) for p in json.load(open(r"C:\Projects\Creative_Contraptions\work\emu_caps\ballscreen_goal%d.json" % G))]

import colorsys
# roll-left: putih redup
for i in range(1, len(roll)):
    pygame.draw.line(fb, (200,200,200), roll[i-1], roll[i], 1)
# physics: rainbow by time
for i in range(1, len(ball)):
    hue = i/len(ball)
    col = tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue*0.85,1,1))
    pygame.draw.line(fb, col, ball[i-1], ball[i], 1)
for (x,y) in ball:
    if 0<=x<320 and 0<=y<200: fb.set_at((x,y),(255,255,0))
pygame.image.save(pygame.transform.scale(fb,(960,600)), r"C:\Projects\Creative_Contraptions\work\ballpath_screen_g%d.png" % G)
print("goal %d: roll pts %d, physics pts %d -> ballpath_screen_g%d.png" % (G, len(roll), len(ball), G))
pygame.quit()
