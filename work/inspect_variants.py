"""Tampilkan SEMUA record utk id_major yg dipakai goal 1 recC -> pilih frame benar."""
import struct
from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1]); i += 3
        else:
            out.append(data[i]); i += 1
    return bytes(out)


def sprite_img(w, h, dec):
    im = Image.new("RGB", (w, h), CGA[1])
    px = im.load()
    wb = w // 4
    for r in range(h):
        for cb in range(wb):
            if r * wb + cb >= len(dec):
                break
            byte = dec[r * wb + cb]
            for p in range(4):
                px[cb * 4 + p, r] = CGA[(byte >> (6 - 2 * p)) & 3]
    return im


b = open(D + "\\GRAPH", "rb").read()
first = struct.unpack_from("<I", b, 8)[0]
n = first // 12
allrec = []
for i in range(n):
    a, bb, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
    allrec.append((i, a, bb, h, w, f, ln, off))

want = [1, 2, 4, 5, 8, 9, 10]
tiles = []
for idm in want:
    recs = [r for r in allrec if r[1] == idm and r[4] and r[3]]
    for (i, a, bb, h, w, f, ln, off) in recs:
        dec = decode_e4(b[off:off + ln])
        if len(dec) < (w // 4) * h:
            continue
        im = sprite_img(w, h, dec).resize((w * 2, h * 2), Image.NEAREST)
        tiles.append(("id%d.%d rec#%d %dx%d f=%d" % (a, bb, i, w, h, f), im))

cols = 6
cw = max(t[1].width for t in tiles) + 12
ch = max(t[1].height for t in tiles) + 26
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * ch), (30, 30, 30))
dr = ImageDraw.Draw(sheet)
for k, (label, im) in enumerate(tiles):
    x = (k % cols) * cw + 6
    y = (k // cols) * ch + 20
    sheet.paste(im, (x, y))
    dr.text((x, y - 14), label, fill=(255, 255, 0))
sheet.save(D + "\\variants_goal1.png")
print("-> variants_goal1.png  (%d tiles)" % len(tiles))
for idm in want:
    recs = [(r[0], r[2], r[3], r[4]) for r in allrec if r[1] == idm and r[4]]
    print("id_major %d: %d record -> (rec#,minor,h,w): %s" % (idm, len(recs), recs[:8]))
