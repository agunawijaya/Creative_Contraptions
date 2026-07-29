"""Render kandidat CGA 2bpp -> PNG, dan uji beberapa varian aturan RLE.

Uji lakmus: kalau salah satu render menghasilkan logo yang terbaca mata,
hipotesis RLE + CGA terbukti sekaligus.
"""
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work"

# Palet CGA palette 1 high-intensity (hitam, cyan, magenta, putih)
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_v1(data, start=0):
    """0xE4 <count> <value>  -> value x count"""
    out = bytearray()
    i, n = start, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1])
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def render(dec, w_bytes, path, interleave=False):
    rows = len(dec) // w_bytes
    if rows == 0:
        return None
    img = Image.new("RGB", (w_bytes * 4, rows))
    px = img.load()
    for r in range(rows):
        for cb in range(w_bytes):
            b = dec[r * w_bytes + cb]
            for p in range(4):
                val = (b >> (6 - 2 * p)) & 3
                px[cb * 4 + p, r] = CGA[val]
    if interleave:
        # CGA: baris genap di bank 0, ganjil di bank 1
        h = rows
        out = Image.new("RGB", (w_bytes * 4, h))
        half = h // 2
        for r in range(half):
            out.paste(img.crop((0, r, img.width, r + 1)), (0, r * 2))
            out.paste(img.crop((0, half + r, img.width, half + r + 1)), (0, r * 2 + 1))
        img = out
    img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    img.save(path)
    return img.size


for name in ["BLOGO.CMP", "LG.CMP"]:
    raw = open(D + "\\" + name, "rb").read()
    for skip in (0, 2):
        dec = decode_v1(raw, skip)
        for wb in (80, 40):
            for il in (False, True):
                tag = "%s_s%d_w%d_%s" % (name.split(".")[0], skip, wb, "il" if il else "lin")
                sz = render(dec, wb, D + "\\out_%s.png" % tag)
                if sz:
                    print("%-28s decoded=%5d  -> %s" % (tag, len(dec), sz))
