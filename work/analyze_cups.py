import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
spr = graph.sprite_by_idx(467)   # tiga per + cangkir
w, h = spr.get_width(), spr.get_height()
BASE = (216, 82)   # posisi draw di title
# cangkir rim = biru (0,0,170) + gray di atas. Cari kolom yg punya biru di baris atas tiap per.
# kelompokkan piksel biru berdasarkan x, cari 3 cluster (kiri/tengah/kanan)
blue = [(x, y) for y in range(h) for x in range(w) if tuple(spr.get_at((x, y)))[:3] == (0, 0, 170)]
# cluster sederhana by x-gap
xs = sorted(set(x for x, y in blue))
clusters = []
cur = [xs[0]]
for x in xs[1:]:
    if x - cur[-1] <= 3:
        cur.append(x)
    else:
        clusters.append(cur); cur = [x]
clusters.append(cur)
print("jumlah cluster-x biru:", len(clusters))
for c in clusters:
    xmin, xmax = min(c), max(c)
    ys = [y for x, y in blue if xmin <= x <= xmax]
    ymin, ymax = min(ys), max(ys)
    # cangkir = bagian ATAS cluster (rim). ambil bbox penuh cluster utk erase.
    print("  cup cluster: local x %d..%d y %d..%d -> SCREEN x %d..%d y %d..%d (w=%d h=%d)" %
          (xmin, xmax, ymin, ymax, BASE[0]+xmin, BASE[0]+xmax, BASE[1]+ymin, BASE[1]+ymax,
           xmax-xmin+1, ymax-ymin+1))
pygame.quit()
