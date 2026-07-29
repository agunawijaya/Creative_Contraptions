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
print("title_frames:", len(g.title_frames))
# GIF sampel seluruh siklus (tiap 6 frame) utk lihat semua fase
imgs = []
for fi in range(0, len(g.title_frames), 6):
    g.title_tick = fi * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    imgs.append(Image.frombytes("RGB", (640, 400),
                pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")))
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\title_full.gif",
             save_all=True, append_images=imgs[1:], duration=70, loop=0)
print("title_full.gif frames=%d" % len(imgs))
# frame kunci utk cek fase (chicken awal, tengah, akhir/elephant)
for fi in (40, 200, 360, 520, 640):
    g.title_tick = fi * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    Image.frombytes("RGB", (640, 400),
        pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")
        ).save(r"C:\Projects\Creative_Contraptions\work\titf_%d.png" % fi)
    print("titf_%d.png" % fi)
pygame.quit()
