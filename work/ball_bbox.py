import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
pygame.init()
mechs = assets.Archive(os.path.join(assets.find_data_dir(), "MECHS"))
MAG = (170, 0, 170)
for idx in (26, 27):
    s = mechs.sprite_by_idx(idx)
    w, h = s.get_width(), s.get_height()
    # bola = blob magenta di bagian ATAS (rows 8-19), BUKAN fulcrum (rows>=16 sisi kiri)
    pts = [(x, y) for y in range(8, 19) for x in range(w)
           if tuple(s.get_at((x, y)))[:3] == MAG]
    # buang fulcrum: fulcrum di kiri (x<19) rows>=16. Ambil cluster x>=18
    ball = [(x, y) for (x, y) in pts if x >= 18]
    if ball:
        xmn, xmx = min(p[0] for p in ball), max(p[0] for p in ball)
        ymn, ymx = min(p[1] for p in ball), max(p[1] for p in ball)
        print("idx%d BALL bbox: x %d..%d (w=%d) y %d..%d (h=%d)" %
              (idx, xmn, xmx, xmx - xmn + 1, ymn, ymx, ymx - ymn + 1))
# ASCII penuh idx26 kolom 17-31 rows 8-20 utk lihat bola
s = mechs.sprite_by_idx(26)
CH = {(0, 0, 170): "|", (0, 170, 170): ".", (170, 0, 170): "O", (170, 170, 170): "#"}
print("idx26 kolom17-31, baris8-20:")
for y in range(8, 20):
    print("y%2d " % y + "".join(CH.get(tuple(s.get_at((x, y)))[:3], "?") for x in range(17, 32)))
pygame.quit()
