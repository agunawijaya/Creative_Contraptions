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
# frame di tengah tilt tiap cangkir
for lbl, f in [("R", 110), ("M", 119), ("L", 128)]:
    g.title_tick = f * 2
    fb = cga.make_framebuffer(); g.draw(fb)
    sub = fb.subsurface(pygame.Rect(206, 74, 88, 60)).copy()
    big = pygame.transform.scale(sub, (88 * 6, 60 * 6))
    Image.frombytes("RGB", (88 * 6, 60 * 6),
                    pygame.image.tostring(big, "RGB")).save(
        r"C:\Projects\Creative_Contraptions\work\ct_%s_%d.png" % (lbl, f))
    print("ct_%s_%d.png" % (lbl, f))

# ASCII sprite 467 bagian atas (cups+handle) & 468 (tilted cup)
graph = assets.Archive(os.path.join(assets.find_data_dir(), "GRAPH"))
CH = {(0, 0, 170): "|", (0, 170, 170): ".", (170, 0, 170): "O", (170, 170, 170): "#"}
for idx, rows in [(467, range(0, 40)), (468, range(0, 21))]:
    s = graph.sprite_by_idx(idx)
    print("=== sprite %d (%dx%d) ===" % (idx, s.get_width(), s.get_height()))
    for y in rows:
        print("".join(CH.get(tuple(s.get_at((x, y)))[:3], "?") for x in range(s.get_width())))
pygame.quit()
