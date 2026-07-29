import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN)               # TITLE->MENU
g.key(pygame.K_RETURN)               # Review (sel 0) -> REVIEW
print("state=%d (REVIEW=%d) rev_i=%d" % (g.state, main.REVIEW, g.rev_i))
sheet = Image.new("RGB", (640, 400 * 3))
shown = [0, 4, 8]   # Inclined Plane, Pendulum, Spring
for k, ri in enumerate(shown):
    g.rev_i = ri; g.rev_frame = 0
    g.draw(fb)
    im = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
    sheet.paste(im, (0, k * 400))
    print("  screen %d: %s" % (ri, main.REVIEW_DATA[ri][0]))
sheet.save(r"C:\Projects\Creative_Contraptions\work\review_enc.png")
# uji browse & animate tick
g.key(pygame.K_RIGHT); print("after RIGHT rev_i=%d" % g.rev_i)
for _ in range(20): g.tick()
print("after ticks rev_frame=%d" % g.rev_frame)
g.key(pygame.K_ESCAPE); print("ESC -> state=%d (MENU=%d)" % (g.state, main.MENU))
pygame.quit()
