import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from PIL import Image, ImageDraw
from cc import cga, assets
from main import Game

pygame.init()
g = Game(assets.find_data_dir())
EMU = r"C:\Projects\Creative_Contraptions\work\emu_caps"
NAMES = {1: "Up and At 'Em", 2: "Hair Care", 3: "Easy Eating",
         4: "Dog Days", 5: "Cool It", 6: "Lights Out!"}
gap, lbl, W = 8, 18, 320
sheet = Image.new("RGB", (2 * W + gap, 6 * (200 + lbl) + gap), (15, 15, 15))
dr = ImageDraw.Draw(sheet)
for gid in range(1, 7):
    fb = cga.make_framebuffer()
    g._blit_scene(fb, gid, True)
    port = Image.frombytes("RGB", (320, 200), pygame.image.tostring(fb, "RGB"))
    emu = Image.open(os.path.join(EMU, "emu_goal%d.png" % gid)).convert("RGB")
    y = (gid - 1) * (200 + lbl) + lbl
    dr.text((4, y - 14), "Goal %d: %s   [KIRI game asli | KANAN port]" % (gid, NAMES[gid]),
            fill=(255, 255, 0))
    sheet.paste(emu, (0, y))
    sheet.paste(port, (W + gap, y))
sheet.save(r"C:\Projects\Creative_Contraptions\work\compare_all6.png")
print("compare_all6.png", sheet.size)
pygame.quit()
