import os, sys
from PIL import Image
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")

# 1) ukuran Bola_01.png + blob magenta di dalamnya
im = Image.open(r"C:\Projects\Creative_Contraptions\sceenshots\Bola_01.png").convert("RGB")
print("Bola_01.png size:", im.size)
px = im.load()
W, H = im.size
# warna magenta CGA (170,0,170) mungkin ter-antialias; cek 'kemerahan-ungu'
def is_mag(c):
    r, g, b = c
    return r > 100 and g < 100 and b > 100
xs = [x for y in range(H) for x in range(W) if is_mag(px[x, y])]
ys = [y for y in range(H) for x in range(W) if is_mag(px[x, y])]
if xs:
    print("magenta bbox: x %d..%d (w=%d), y %d..%d (h=%d)" %
          (min(xs), max(xs), max(xs) - min(xs) + 1, min(ys), max(ys), max(ys) - min(ys) + 1))

# 2) bola di sprite lever (MECHS idx26) — ukuran native. Cari blob magenta paling atas-kanan
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
mechs = assets.Archive(os.path.join(D, "MECHS"))
for idx in (26, 27):
    spr = mechs.sprite_by_idx(idx)
    w, h = spr.get_width(), spr.get_height()
    mag = [(x, y) for y in range(h) for x in range(w) if tuple(spr.get_at((x, y)))[:3] == (170, 0, 170)]
    # bola = blob magenta bulat (bukan segitiga fulcrum di bawah-tengah). Ambil blob kiri/kanan atas.
    print("lever idx%d: %d px magenta; bbox x %s..%s y %s..%s" %
          (idx, len(mag), min(p[0] for p in mag), max(p[0] for p in mag),
           min(p[1] for p in mag), max(p[1] for p in mag)))
pygame.quit()
