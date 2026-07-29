"""Pack frame animasi layar judul (vframes_goal128 = contraption goal 128 berjalan:
bola keluar dari ayam, dst) -> port/cc/anim/title.dat. Teks 'CREATIVE CONTRAPTIONS'
ditumpuk oleh port (font tak dirender emulator)."""
import os, glob, struct, zlib, sys
from PIL import Image
CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
LUT = {c: i for i, c in enumerate(CGA)}
OUT = r"C:\Projects\Creative_Contraptions\port\cc\anim"
F = r"C:\Projects\Creative_Contraptions\work\vframes_goal128"
NFRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 160   # 1 siklus loop


def nearest(c):
    if c in LUT:
        return LUT[c]
    best, bi = 1e9, 1
    for i, cc in enumerate(CGA):
        d = sum((a - b) ** 2 for a, b in zip(c, cc))
        if d < best:
            best, bi = d, i
    return bi


files = sorted(glob.glob(os.path.join(F, "v*.png")))[:NFRAMES]
blob = bytearray()
for f in files:
    im = Image.open(f).convert("RGB"); px = im.load()
    for y in range(200):
        for xb in range(0, 320, 4):
            b = 0
            for p in range(4):
                b = (b << 2) | nearest(px[xb + p, y])
            blob.append(b)
packed = zlib.compress(bytes(blob), 9)
with open(os.path.join(OUT, "title.dat"), "wb") as fo:
    fo.write(b"CCA1" + struct.pack("<HH", 128, len(files)) + packed)
print("title.dat: %d frame -> %d KB" % (len(files), (len(packed) + 8) // 1024))
