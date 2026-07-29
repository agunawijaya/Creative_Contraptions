import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
OUT = r"C:\Projects\Creative_Contraptions\work"


def snap():
    fb = cga.make_framebuffer(); g.draw(fb)
    return Image.frombytes("RGB", (640, 400),
                           pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))


def force(gid, vi):
    for _ in range(400):
        g.start_play(gid, fill="mech")
        if g.cur_variant == vi:
            return
    raise SystemExit("gagal paksa v%d" % vi)


for gid, vi in [(1, 0), (1, 1), (3, 1), (6, 1)]:
    force(gid, vi)
    snap().save(os.path.join(OUT, "diag_g%d_v%d.png" % (gid, vi)))
    print("diag_g%d_v%d.png" % (gid, vi))
pygame.quit()
