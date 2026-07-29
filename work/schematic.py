"""Rekonstruksi tata letak goal 1 DARI DATA CONTRAP -> skema berlabel 320x200.
Uji konvensi koordinat: (x=f1, y=f0)."""
import struct
from PIL import Image, ImageDraw

MECH = {100: "Ramp", 101: "Ramp", 110: "Pulley", 111: "Pulley", 112: "Pulley",
        115: "Wheel", 120: "Wedge", 130: "Pendulm", 131: "Pendulm", 132: "Magnet",
        133: "Pulley", 135: "Screw", 140: "Lever", 141: "Lever", 150: "Spring"}

b = open(r"C:\Projects\Creative_Contraptions\work\CONTRAP", "rb").read()
recs = [struct.unpack_from("<HI", b, i * 6) for i in range(36)]
off = next(o for (i, o) in recs if i == 1)
p = off + 2
countA = struct.unpack_from("<H", b, p)[0]; p += 2 + countA * 4
countB = struct.unpack_from("<H", b, p)[0]; p += 2
recB = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(countB)]; p += countB * 6
countC = struct.unpack_from("<H", b, p)[0]; p += 2
recC = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(countC)]

S = 3
img = Image.new("RGB", (320 * S, 200 * S), (0, 128, 128))  # cyan-ish spt CGA game
dr = ImageDraw.Draw(img)


def mark(x, y, label, col):
    cx, cy = x * S, y * S
    dr.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=(255, 255, 255), fill=col)
    dr.text((cx + 7, cy - 5), label, fill=(255, 255, 255))


# Mekanisme (recB): x=f1, y=f0
for f0, f1, f2 in recB:
    mark(f1, f0, "%s (%d,%d)" % (MECH.get(f2, "?"), f1, f0), (200, 0, 200))
# Zany/scenery (recC): x=f1, y=f0
for f0, f1, f2 in recC:
    mark(f1, f0, "obj%d (%d,%d)" % (f2, f1, f0), (0, 0, 160))

dr.text((6, 6), "GOAL 1 'Up and At Em' - rekonstruksi DARI DATA CONTRAP", fill=(255, 255, 0))
dr.text((6, 20), "magenta=mekanisme (slot)   biru=zany object   [x=f1, y=f0]", fill=(255, 255, 0))
img.save(r"C:\Projects\Creative_Contraptions\work\schematic_goal1.png")
print("-> schematic_goal1.png")
print("Mekanisme:", [(MECH.get(f2), f1, f0) for f0, f1, f2 in recB])
print("Zany:", [(f2, f1, f0) for f0, f1, f2 in recC])
