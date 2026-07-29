"""Overlay posisi komponen DARI DATA CONTRAP ke SCREENSHOT ASLI game.
Bukti: marker mendarat di sprite yang benar."""
import struct
from PIL import Image, ImageDraw

MECH = {100: "Ramp", 101: "Ramp", 110: "Pulley", 111: "Pulley", 112: "Pulley",
        115: "Wheel", 120: "Wedge", 130: "Pendulm", 131: "Pendulm", 132: "Magnet",
        133: "Pulley", 135: "Screw", 140: "Lever", 141: "Lever", 150: "Spring"}

b = open(r"C:\Projects\Creative_Contraptions\work\CONTRAP", "rb").read()
recs = [struct.unpack_from("<HI", b, i * 6) for i in range(36)]
off = next(o for (i, o) in recs if i == 1)
p = off + 2
cA = struct.unpack_from("<H", b, p)[0]; p += 2 + cA * 4
cB = struct.unpack_from("<H", b, p)[0]; p += 2
recB = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(cB)]; p += cB * 6
cC = struct.unpack_from("<H", b, p)[0]; p += 2
recC = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(cC)]

img = Image.open(r"C:\Projects\Creative_Contraptions\work\shots\20_contraption.png").convert("RGB")
W, H = img.size
sx = W / 320.0
sy = H / 200.0
dr = ImageDraw.Draw(img)


def mark(x, y, label, col):
    cx, cy = x * sx, y * sy
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(255, 255, 0), width=2)
    dr.line([cx - 9, cy, cx + 9, cy], fill=(255, 255, 0))
    dr.line([cx, cy - 9, cx, cy + 9], fill=(255, 255, 0))
    dr.text((cx + 9, cy - 6), label, fill=col)


for f0, f1, f2 in recB:
    mark(f1, f0, MECH.get(f2, "?"), (255, 0, 255))
for f0, f1, f2 in recC:
    mark(f1, f0, "z%d" % f2, (120, 200, 255))

img.save(r"C:\Projects\Creative_Contraptions\work\overlay_goal1.png")
print("-> overlay_goal1.png  (img %dx%d, skala %.2fx%.2f)" % (W, H, sx, sy))
