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


def crop(f, box, name):
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    sub = fb.subsurface(pygame.Rect(*box)).copy()
    big = pygame.transform.scale(sub, (box[2] * 6, box[3] * 6))
    Image.frombytes("RGB", (box[2] * 6, box[3] * 6),
                    pygame.image.tostring(big, "RGB")).save(
        r"C:\Projects\Creative_Contraptions\work\%s.png" % name)
    print("%s frame %d" % (name, f))


# ball inside lever box (frame ~44, hold lever) — crop around lever box (124,128)
crop(44, (110, 118, 60, 45), "fix_lever_inside")
# ball inside spring box (frame ~140, hold spring) — crop around spring box (168,128)
crop(140, (155, 118, 60, 45), "fix_spring_inside")
# cup tilt (frame ~108, cup_R tilted) — crop around springs (216,82)
crop(108, (210, 76, 80, 85), "fix_cup_tilt")
pygame.quit()
