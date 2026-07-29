import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main

G = int(sys.argv[1]) if len(sys.argv) > 1 else 1
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN)       # TITLE->MENU
g.key(pygame.K_RETURN)       # MENU(Review)->GOAL
# pilih goal G
for _ in range(G - 1):
    g.key(pygame.K_DOWN)
g.key(pygame.K_RETURN)       # ->CONTRAPTION
g.key(pygame.K_SPACE)        # ->PLAYANIM
imgs = []
guard = 0
while g.anim_i < len(g.anim_frames) - 1 and guard < 2000:
    g.draw(fb)
    imgs.append(Image.frombytes("RGB", (640, 400),
                pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")))
    g.tick(); guard += 1
g.draw(fb)
imgs.append(Image.frombytes("RGB", (640, 400),
            pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB")))
out = r"C:\Projects\Creative_Contraptions\work\port_review_goal%d.gif" % G
imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=80, loop=0)
print("goal %d: %d frame -> %s" % (G, len(imgs), out))
pygame.quit()
