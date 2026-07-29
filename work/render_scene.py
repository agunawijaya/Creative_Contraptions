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

def render(path, title):
    draws = json.load(open(path))
    fb = cga.make_framebuffer()
    fb.fill(cga.PALETTE[cga.BG_INDEX])
    for d in draws:
        if d["idx"] < 0:
            continue
        spr = (graph if d["arch"] == "GRAPH" else mechs).sprite_by_idx(d["idx"])
        if spr:
            fb.blit(spr, (d["x"], d["y"]))
    big = pygame.transform.scale(fb, (640, 400))
    out = r"C:\Projects\Creative_Contraptions\work\render_%s.png" % title
    Image.frombytes("RGB", (640, 400), pygame.image.tostring(big, "RGB")).save(out)
    print("->", out)

render(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal1.json", "ref_g1")
render(r"C:\Projects\Creative_Contraptions\work\emu_caps\draws_goal1_v0.json", "cap_g1_v0")
render(r"C:\Projects\Creative_Contraptions\work\emu_caps\draws_goal1_v1.json", "cap_g1_v1")
pygame.quit()
