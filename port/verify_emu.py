"""Verifikasi: render port (daftar draw deterministik) vs ground truth emulator."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from PIL import Image
from cc import cga, assets
from main import Game

pygame.init()
g = Game(assets.find_data_dir())
EMU = r"C:\Projects\Creative_Contraptions\work\emu_caps"
here = os.path.dirname(__file__)
tot_m = tot = 0
for gid in range(1, 7):
    fb = cga.make_framebuffer()
    g._blit_scene(fb, gid, draw_mech=True)
    Image.frombytes("RGB", (320, 200), pygame.image.tostring(fb, "RGB")).resize((640,400), Image.NEAREST).save(os.path.join(here, "port_goal%d.png" % gid))
    emu = Image.open(os.path.join(EMU, "emu_goal%d.png" % gid)).convert("RGB")
    m = 0
    for y in range(200):
        for x in range(320):
            if fb.get_at((x, y))[:3] == emu.getpixel((x, y)):
                m += 1
    tot_m += m; tot += 64000
    print("goal %d: cocok %d/64000 (%.1f%%)" % (gid, m, 100 * m / 64000))
print("TOTAL: %.1f%% cocok dgn game asli (emulator)" % (100 * tot_m / tot))
pygame.quit()
