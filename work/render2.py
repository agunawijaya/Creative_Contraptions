"""Render CGA 320x200 dengan interleave bank yang benar.

Layout framebuffer CGA:
  0x0000..0x1F3F : bank 0 = baris genap (0,2,4..198), 100 baris x 80 byte = 8000
  0x1F40..0x1FFF : padding 192 byte
  0x2000..0x3F3F : bank 1 = baris ganjil (1,3,5..199), 8000 byte
  total 16384
"""
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_e4(data, start=0):
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


def render_cga(dec, path, scale=2):
    img = Image.new("RGB", (320, 200), (0, 0, 0))
    px = img.load()
    for row in range(200):
        bank = row & 1
        line = row >> 1
        base = (0x2000 if bank else 0) + line * 80
        if base + 80 > len(dec):
            continue
        for cb in range(80):
            b = dec[base + cb]
            for p in range(4):
                px[cb * 4 + p, row] = CGA[(b >> (6 - 2 * p)) & 3]
    img = img.resize((320 * scale, 200 * scale), Image.NEAREST)
    img.save(path)


for name in ["LG.CMP", "BLOGO.CMP"]:
    raw = open(D + "\\" + name, "rb").read()
    dec = decode_e4(raw)
    print("%s: compressed=%d decoded=%d (framebuffer CGA=16384, selisih=%+d)"
          % (name, len(raw), len(dec), len(dec) - 16384))
    render_cga(dec, D + "\\fixed_%s.png" % name.split(".")[0])
