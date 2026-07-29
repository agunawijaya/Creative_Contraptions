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
print("title_ball frames:", len(g.title_ball))
imgs = []
# 2 tick per frame bola -> putar 1 siklus penuh + sedikit
for t in range(0, len(g.title_ball) * 2 + 4, 2):
    g.title_tick = t
    fb = cga.make_framebuffer(); g.draw(fb)
    imgs.append(Image.frombytes("RGB", (640, 400),
                pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")))
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\title_ball.gif",
             save_all=True, append_images=imgs[1:], duration=80, loop=0)
print("-> title_ball.gif frames=%d" % len(imgs))
# frame kunci tiap fase
for lbl, f in [("chick_fall", 15), ("seesaw_hit", 30), ("arc_to_eleph", 50),
               ("eleph_react", 74), ("spring_fall", 92), ("big_arc", 115)]:
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    Image.frombytes("RGB", (640, 400),
        pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")
        ).save(r"C:\Projects\Creative_Contraptions\work\tb_%s.png" % lbl)
pygame.quit()
