"""Verifikasi: render tiap goal (tabel sprite) vs ground truth screenshot user.
Ukur kecocokan pixel di area sprite zany + render 'assembled' utk dilihat."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from PIL import Image
from cc import cga, assets
from main import Game

pygame.init()
g = Game(assets.find_data_dir())
BG = cga.PALETTE[cga.BG_INDEX]
here = os.path.dirname(__file__)


def to_pil(surf):
    im = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            im.putpixel((x, y), surf.get_at((x, y))[:3])
    return im


print("Verifikasi kecocokan sprite zany vs ground truth (screenshot user):")
tot_m = tot_n = 0
for gid in range(1, 7):
    fb = cga.make_framebuffer()
    g._blit_scene(fb, gid, draw_mech=True)   # assembled utk dilihat
    to_pil(fb).resize((640, 400), Image.NEAREST).save(os.path.join(here, "asm_goal%d.png" % gid))
    # untuk skor: render zany saja, bandingkan pixel non-bg ke ground truth
    fbz = cga.make_framebuffer()
    g._blit_scene(fbz, gid, draw_mech=False)
    gt = Image.open(os.path.join(here, "gtu_goal%d.png" % gid)).convert("RGB")
    m = n = 0
    for y in range(200):
        for x in range(320):
            c = fbz.get_at((x, y))[:3]
            if c == BG:
                continue
            n += 1
            if gt.getpixel((x, y)) == c:
                m += 1
    tot_m += m; tot_n += n
    print("  goal %d: sprite zany cocok %d/%d (%.0f%%)" % (gid, m, n, 100 * m / n))
print("TOTAL zany: %.1f%% pixel cocok dgn game asli" % (100 * tot_m / tot_n))
pygame.quit()
