"""Dump sprite MISC (21 record) -> cari sprite bola & elemen UI."""
import struct
from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_e4(d):
    o = bytearray(); i = 0
    while i < len(d):
        if d[i] == 0xE4 and i + 2 < len(d):
            o.extend(bytes([d[i + 2]]) * d[i + 1]); i += 3
        else:
            o.append(d[i]); i += 1
    return bytes(o)


b = open(D + "\\MISC", "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
tiles = []
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
    if not (w and h and ln):
        continue
    dec = decode_e4(b[off:off + ln])
    im = Image.new("RGB", (w, h), CGA[0])
    for r in range(h):
        for cb in range(w // 4):
            if r * (w // 4) + cb < len(dec):
                by = dec[r * (w // 4) + cb]
                for p in range(4):
                    im.putpixel((cb * 4 + p, r), CGA[(by >> (6 - 2 * p)) & 3])
    tiles.append(("id%d.%d %dx%d" % (a, mi, w, h), im.resize((w * 4, h * 4), Image.NEAREST)))

cols = 6
cw = max(t[1].width for t in tiles) + 10
ch = max(t[1].height for t in tiles) + 22
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * ch), (40, 40, 40))
dr = ImageDraw.Draw(sheet)
for k, (lab, im) in enumerate(tiles):
    x = (k % cols) * cw + 4; y = (k // cols) * ch + 16
    sheet.paste(im, (x, y)); dr.text((x, y - 12), lab, fill=(255, 255, 0))
sheet.save(D + "\\misc_sheet.png")
print("-> misc_sheet.png (%d sprite)" % len(tiles))
