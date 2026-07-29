"""Kalibrasi crop 320x200 (dari capture fullscreen) dgn mencocokkan goal1 ke screenshot user.
Lalu recover native untuk semua 6 goal."""
import os
from PIL import Image

CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
IN = r"C:\Projects\Creative_Contraptions\work\caps_goals"
OUT = r"C:\Projects\Creative_Contraptions\work\gt"
os.makedirs(OUT, exist_ok=True)


def snap(rgb):
    return min(CGA, key=lambda c: sum((a - b) ** 2 for a, b in zip(rgb, c)))


def crop_native(im, left, top):
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            out.putpixel((x, y), snap(im.getpixel((left + x, top + y))))
    return out


def user_native():
    im = Image.open(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png").convert("RGB")
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            out.putpixel((x, y), snap(im.getpixel((x * 5 + 2, y * 6 + 3))))
    return out


ref = user_native()
g1 = Image.open(os.path.join(IN, "goal1.png")).convert("RGB")
best = None
for top in range(795, 812):
    for left in range(1276, 1286):
        c = crop_native(g1, left, top)
        same = sum(1 for y in range(0, 200, 2) for x in range(0, 320, 2)
                   if c.getpixel((x, y)) == ref.getpixel((x, y)))
        if best is None or same > best[0]:
            best = (same, left, top)
tot = len(range(0, 200, 2)) * len(range(0, 320, 2))
print("Kalibrasi: left=%d top=%d cocok %d/%d (%.1f%%)"
      % (best[1], best[2], best[0], tot, 100 * best[0] / tot))

left, top = best[1], best[2]
for g in range(1, 7):
    im = Image.open(os.path.join(IN, "goal%d.png" % g)).convert("RGB")
    nat = crop_native(im, left, top)
    nat.save(os.path.join(OUT, "gt_goal%d.png" % g))
    nat.resize((640, 400), Image.NEAREST).save(os.path.join(OUT, "gt_goal%d_big.png" % g))
print("6 ground-truth native tersimpan di", OUT)
