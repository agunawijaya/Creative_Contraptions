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


def render(draws):
    fb = cga.make_framebuffer()
    for d in draws:
        if d["idx"] < 0:
            continue
        spr = (graph if d["arch"] == "GRAPH" else mechs).sprite_by_idx(d["idx"])
        if spr:
            fb.blit(spr, (d["x"], d["y"]))
    return fb


for gid, vi in [(1, 0), (1, 1)]:
    draws = json.load(open(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal%d_v%d.json" % (gid, vi)))
    fb = render(draws)
    port = Image.frombytes("RGB", (320, 200), pygame.image.tostring(fb, "RGB"))
    vram_fp = r"C:\Projects\Creative_Contraptions\work\vframes_goal%d_v%d\v000.png" % (gid, vi)
    vram = Image.open(vram_fp).convert("RGB") if os.path.exists(vram_fp) else None
    # montase: port kiri, vram kanan
    m = Image.new("RGB", (320 * 2 * 2, 200 * 2))
    m.paste(port.resize((640, 400), Image.NEAREST), (0, 0))
    if vram:
        m.paste(vram.resize((640, 400), Image.NEAREST), (640, 0))
        diff = sum(1 for p, q in zip(port.getdata(), vram.getdata()) if p != q)
        print("goal%d v%d: beda piksel port vs VRAM = %d / 64000" % (gid, vi, diff))
    m.save(r"C:\Projects\Creative_Contraptions\work\cmpvram_g%d_v%d.png" % (gid, vi))
    print("-> cmpvram_g%d_v%d.png (port kiri, VRAM kanan)" % (gid, vi))
pygame.quit()
