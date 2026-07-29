"""Pulihkan native 320x200 dari 6 capture fullscreen (6x) + validasi goal1 vs screenshot user."""
import os
from PIL import Image

CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
IN = r"C:\Projects\Creative_Contraptions\work\caps_goals"
OUT = r"C:\Projects\Creative_Contraptions\work\gt"
os.makedirs(OUT, exist_ok=True)


def snap(rgb):
    return min(CGA, key=lambda c: sum((a - b) ** 2 for a, b in zip(rgb, c)))


def recover(path, sx, sy):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            px = im.getpixel((min(x * sx + sx // 2, w - 1), min(y * sy + sy // 2, h - 1)))
            out.putpixel((x, y), snap(px))
    return out


for g in range(1, 7):
    nat = recover(os.path.join(IN, "goal%d.png" % g), 6, 6)
    nat.save(os.path.join(OUT, "gt_goal%d.png" % g))
    nat.resize((640, 400), Image.NEAREST).save(os.path.join(OUT, "gt_goal%d_big.png" % g))

# validasi goal1 vs screenshot user (recover 5x/6x)
user = recover(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png", 5, 6)
mine = Image.open(os.path.join(OUT, "gt_goal1.png"))
same = sum(1 for y in range(200) for x in range(320)
           if user.getpixel((x, y)) == mine.getpixel((x, y)))
print("Validasi goal1: capture-ku vs screenshot-user cocok %d/64000 pixel (%.1f%%)"
      % (same, 100 * same / 64000))
