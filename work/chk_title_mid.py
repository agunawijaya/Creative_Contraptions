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
for tick in (24, 48, 80, 120):
    g.title_tick = tick
    fb = cga.make_framebuffer(); g.draw(fb)
    Image.frombytes("RGB", (640, 400),
                    pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")
                    ).save(r"C:\Projects\Creative_Contraptions\work\title_f%d.png" % tick)
    print("title_f%d.png (frame idx %d)" % (tick, (tick // 2) % len(g.title_frames)))
pygame.quit()
