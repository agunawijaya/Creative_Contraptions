"""Ekstrak seluruh aset Creative Contraptions -> PNG + GIF animasi.

PNG  : setiap record jadi satu file
GIF  : record dengan id sama = frame animasi -> digabung jadi GIF
"""
import struct
import os
from collections import defaultdict
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work"
OUT = D + r"\assets"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1])
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def to_img(dec, w, h, scale=4):
    img = Image.new("RGB", (w, h), (0, 0, 0))
    px = img.load()
    wb = w // 4
    for r in range(h):
        base = r * wb
        if base + wb > len(dec):
            break
        for cb in range(wb):
            byte = dec[base + cb]
            for p in range(4):
                px[cb * 4 + p, r] = CGA[(byte >> (6 - 2 * p)) & 3]
    return img.resize((w * scale, h * scale), Image.NEAREST)


def process(name):
    b = open(D + "\\" + name, "rb").read()
    first = struct.unpack_from("<I", b, 8)[0]
    n = first // 12
    outdir = os.path.join(OUT, name)
    os.makedirs(outdir, exist_ok=True)
    groups = defaultdict(list)
    made = skipped = 0
    for i in range(n):
        a, bb, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
        if w == 0 or h == 0 or ln == 0:
            continue
        dec = decode_e4(b[off:off + ln])
        need = (w // 4) * h
        if len(dec) < need:
            skipped += 1
            continue
        img = to_img(dec, w, h)
        fn = "%s_id%03d-%02d_i%03d_%dx%d.png" % (name, a, bb, i, w, h)
        img.save(os.path.join(outdir, fn))
        groups[(a, bb)].append(img)
        made += 1
    # GIF untuk grup multi-frame
    gifdir = os.path.join(OUT, "_gif")
    os.makedirs(gifdir, exist_ok=True)
    gifs = 0
    for (a, bb), frames in groups.items():
        if len(frames) < 2:
            continue
        w = max(f.width for f in frames)
        h = max(f.height for f in frames)
        canv = []
        for f in frames:
            c = Image.new("RGB", (w, h), (0, 0, 0))
            c.paste(f, (0, 0))
            canv.append(c)
        canv[0].save(os.path.join(gifdir, "%s_id%03d-%02d_%dframes.gif" % (name, a, bb, len(canv))),
                     save_all=True, append_images=canv[1:], duration=250, loop=0)
        gifs += 1
    print("%-8s : %3d PNG, %2d GIF, %d dilewati (data kurang)" % (name, made, gifs, skipped))
    return made, gifs


os.makedirs(OUT, exist_ok=True)
tot = 0
for f in ["GRAPH", "MECHS", "MISC", "ANIMATE"]:
    m, g = process(f)
    tot += m
print("\nTotal %d PNG di %s" % (tot, OUT))
