import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
g.state = main.TITLE
n = len(g.title_ball)
print("title_ball frames:", n)
imgs = []
for t in range(0, n * 2 + 4, 2):
    g.title_tick = t
    fb = cga.make_framebuffer(); g.draw(fb)
    imgs.append(Image.frombytes("RGB", (640, 400),
                pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")))
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\title_rg.gif",
             save_all=True, append_images=imgs[1:], duration=75, loop=0)
print("-> title_rg.gif frames=%d" % len(imgs))
# frame kunci per fase (indeks frame bola)
keys = {"drum1_boom": 20, "drum2_boom": 34, "lever_launch": 54, "eleph_react": 78,
        "cups": 100, "springbox": 116, "spring_launch": 124}
for lbl, f in keys.items():
    if f < n:
        g.title_tick = f * 2
        fb = cga.make_framebuffer(); g.draw(fb)
        Image.frombytes("RGB", (640, 400),
            pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")
            ).save(r"C:\Projects\Creative_Contraptions\work\rg_%s.png" % lbl)
        print("rg_%s.png (frame %d)" % (lbl, f))
pygame.quit()
