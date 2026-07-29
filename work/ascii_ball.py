import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
D = assets.find_data_dir()
mechs = assets.Archive(os.path.join(D, "MECHS"))
CH = {(0, 0, 170): "|", (0, 170, 170): " ", (170, 0, 170): "O", (170, 170, 170): "."}
spr = mechs.sprite_by_idx(26)
w, h = spr.get_width(), spr.get_height()
print("lever idx26 (%dx%d):" % (w, h))
for y in range(h):
    print("".join(CH.get(tuple(spr.get_at((x, y)))[:3], "?") for x in range(w)))

# render left-cup (cangkir ke-3) tilt closeup dari title
g = main.Game(assets.find_data_dir())
g.state = main.TITLE
# cari frame di mana cangkir KIRI miring (cuptilt di CUP_L) -> sekitar s8 awal (frame ~124)
for f in (126, 130):
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    sub = fb.subsurface(pygame.Rect(210, 95, 55, 60)).copy()
    big = pygame.transform.scale(sub, (55 * 6, 60 * 6))
    Image.frombytes("RGB", (55 * 6, 60 * 6),
                    pygame.image.tostring(big, "RGB")).save(
        r"C:\Projects\Creative_Contraptions\work\cup3_%d.png" % f)
    print("cup3_%d.png" % f)
pygame.quit()
