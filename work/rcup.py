import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
graph = assets.Archive(os.path.join(assets.find_data_dir(), "GRAPH"))
s = graph.sprite_by_idx(467)   # 68x72 @ (216,82)
CH = {(0, 0, 170): "|", (0, 170, 170): ".", (170, 0, 170): "O", (170, 170, 170): "#"}
# cangkir KANAN = kolom lokal 44-67 (screen x260-283), baris atas
print("467 cangkir kanan (kolom lokal 44-67, baris 2-22):")
for y in range(2, 22):
    print("y%2d(scr%d) " % (y, 82 + y) + "".join(CH.get(tuple(s.get_at((x, y)))[:3], "?")
                                                for x in range(44, 68)))
# render ct_R zoom besar
g = main.Game(assets.find_data_dir())
g.state = main.TITLE
for f in (108, 110, 113):
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    sub = fb.subsurface(pygame.Rect(255, 78, 40, 40)).copy()
    big = pygame.transform.scale(sub, (40 * 9, 40 * 9))
    Image.frombytes("RGB", (40 * 9, 40 * 9),
                    pygame.image.tostring(big, "RGB")).save(
        r"C:\Projects\Creative_Contraptions\work\rcupz_%d.png" % f)
    print("rcupz_%d.png" % f)
pygame.quit()
