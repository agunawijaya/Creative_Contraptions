"""Auto-crop region game (native 320x200) dari capture fullscreen via bbox non-biru."""
import os
from PIL import Image

CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
IN = r"C:\Projects\Creative_Contraptions\work\caps_goals"
OUT = r"C:\Projects\Creative_Contraptions\work\gt"
os.makedirs(OUT, exist_ok=True)
BLUE = (0, 0, 170)


def snap(rgb):
    return min(CGA, key=lambda c: sum((a - b) ** 2 for a, b in zip(rgb, c)))


def autocrop(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # cari bbox pixel yg jelas game (cyan/gray/magenta), abaikan biru & hitam & putih(menu)
    minx = miny = 10 ** 9
    maxx = maxy = -1
    step = 2
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = im.getpixel((x, y))
            is_cyan = abs(r - 0) < 60 and abs(g - 170) < 60 and abs(b - 170) < 60
            if is_cyan:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx < 0:
        return None
    # game 320x200: perluas bbox ke ukuran penuh dari sudut kiri-atas cyan
    # (status bar atas & area bawah mungkin bukan cyan; pakai lebar cyan sbg acuan)
    return im.crop((minx, miny, maxx + 1, maxy + 1)), (minx, miny, maxx - minx + 1, maxy - miny + 1)


for g in range(1, 7):
    res = autocrop(os.path.join(IN, "goal%d.png" % g))
    if res is None:
        print("goal%d: tak ketemu region cyan" % g); continue
    crop, box = res
    print("goal%d: bbox cyan = %s (w=%d h=%d)" % (g, box[:2], box[2], box[3]))
    # resize ke 320x200 & snap palet
    nat = crop.resize((320, 200), Image.NEAREST)
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            out.putpixel((x, y), snap(nat.getpixel((x, y))))
    out.save(os.path.join(OUT, "gt_goal%d.png" % g))
    out.resize((640, 400), Image.NEAREST).save(os.path.join(OUT, "gt_goal%d_big.png" % g))
