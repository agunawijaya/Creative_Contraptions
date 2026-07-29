"""Pulihkan frame native 320x200 dari screenshot game asli (5x/6x) = GROUND TRUTH.
Dipakai harness pembanding (frame-diff) untuk memverifikasi port cocok dgn asli."""
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]


def _nearest_cga(rgb):
    best, bd = 0, 1e9
    for i, c in enumerate(CGA):
        d = sum((a - b) ** 2 for a, b in zip(rgb, c))
        if d < bd:
            bd, best = d, i
    return CGA[best]


def recover_native(shot_path, sx=5, sy=6):
    """Downsample screenshot -> Image 320x200 dgn warna di-snap ke palet CGA."""
    im = Image.open(shot_path).convert("RGB")
    out = Image.new("RGB", (320, 200))
    for y in range(200):
        for x in range(320):
            px = im.getpixel((min(x * sx + sx // 2, im.width - 1),
                              min(y * sy + sy // 2, im.height - 1)))
            out.putpixel((x, y), _nearest_cga(px))
    return out


if __name__ == "__main__":
    nat = recover_native(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png")
    nat.resize((960, 600), Image.NEAREST).save(
        r"C:\Projects\Creative_Contraptions\work\gt_goal1_native.png")
    nat.save(r"C:\Projects\Creative_Contraptions\work\gt_goal1_320.png")
    print("Ground truth native 320x200 dipulihkan -> gt_goal1_native.png")
