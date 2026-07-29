import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())

# 1) ASCII bola hasil ekstraksi
CH = {(0, 0, 170): "|", (0, 170, 170): ".", (170, 0, 170): "O", (170, 170, 170): "#"}
b = g.title_ballspr
print("title ball %dx%d:" % (b.get_width(), b.get_height()))
for y in range(b.get_height()):
    print("".join(CH.get(tuple(b.get_at((x, y)))[:3], "?") for x in range(b.get_width())))

# 2) GIF zoom area cangkir (x206..292, y74..160) sepanjang jalur kanan
g.state = main.TITLE
imgs = []
box = (206, 74, 88, 90)
for f in range(92, 145):
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    sub = fb.subsurface(pygame.Rect(*box)).copy()
    big = pygame.transform.scale(sub, (box[2] * 4, box[3] * 4))
    imgs.append(Image.frombytes("RGB", (box[2] * 4, box[3] * 4),
                pygame.image.tostring(big, "RGB")))
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\cups_zoom.gif",
             save_all=True, append_images=imgs[1:], duration=120, loop=0)
print("-> cups_zoom.gif (%d frame)" % len(imgs))
pygame.quit()
