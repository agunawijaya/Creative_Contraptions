"""Rekonstruksi contraption DARI ASET KITA di posisi dari data CONTRAP.
Uji: hasil harus menyerupai game asli."""
import struct
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]
BG = CGA[1]  # cyan = latar game


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1]); i += 3
        else:
            out.append(data[i]); i += 1
    return bytes(out)


def load_dir(name):
    """Kembalikan dict id_major -> list of (w,h,pixels[])."""
    b = open(D + "\\" + name, "rb").read()
    first = struct.unpack_from("<I", b, 8)[0]
    n = first // 12
    out = {}
    for i in range(n):
        a, bb, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
        if w == 0 or h == 0 or ln == 0:
            continue
        dec = decode_e4(b[off:off + ln])
        if len(dec) < (w // 4) * h:
            continue
        out.setdefault(a, []).append((w, h, dec))
    return out


def sprite_img(w, h, dec):
    im = Image.new("RGB", (w, h), BG)
    px = im.load()
    wb = w // 4
    for r in range(h):
        for cb in range(wb):
            byte = dec[r * wb + cb]
            for p in range(4):
                px[cb * 4 + p, r] = CGA[(byte >> (6 - 2 * p)) & 3]
    return im


def blit(canvas, spr, x, y):
    """Paste, cyan (BG) transparan."""
    cpx = canvas.load()
    spx = spr.load()
    for j in range(spr.height):
        for i in range(spr.width):
            c = spx[i, j]
            if c == BG:
                continue
            X, Y = x + i, y + j
            if 0 <= X < canvas.width and 0 <= Y < canvas.height:
                cpx[X, Y] = c


GRAPH = load_dir("GRAPH")
MECHS = load_dir("MECHS")
print("GRAPH id_major: %s" % sorted(GRAPH))
print("MECHS id_major: %s" % sorted(MECHS))

# Parse goal 1
b = open(D + "\\CONTRAP", "rb").read()
recs = [struct.unpack_from("<HI", b, i * 6) for i in range(36)]
off = next(o for (i, o) in recs if i == 1)
p = off + 2
cA = struct.unpack_from("<H", b, p)[0]; p += 2 + cA * 4
cB = struct.unpack_from("<H", b, p)[0]; p += 2
recB = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(cB)]; p += cB * 6
cC = struct.unpack_from("<H", b, p)[0]; p += 2
recC = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(cC)]

canvas = Image.new("RGB", (320, 200), BG)

# Zany objects (recC) dari GRAPH id_major==f2 (frame pertama)
for f0, f1, f2 in recC:
    if f2 in GRAPH:
        w, h, dec = GRAPH[f2][0]
        blit(canvas, sprite_img(w, h, dec), f1, f0)
        print("  zany f2=%d @(%d,%d) %dx%d" % (f2, f1, f0, w, h))
    else:
        print("  zany f2=%d TAK ADA di GRAPH" % f2)

# Mekanisme (recB) dari MECHS id_major==f2
for f0, f1, f2 in recB:
    if f2 in MECHS:
        w, h, dec = MECHS[f2][0]
        blit(canvas, sprite_img(w, h, dec), f1, f0)
        print("  mech f2=%d @(%d,%d) %dx%d" % (f2, f1, f0, w, h))
    else:
        print("  mech f2=%d TAK ADA di MECHS" % f2)

canvas.resize((320 * 3, 200 * 3), Image.NEAREST).save(D + "\\reconstruct_goal1.png")
print("-> reconstruct_goal1.png")
