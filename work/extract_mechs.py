"""Ekstrak sprite MECHS -> contact sheet, untuk tahu komponen apa saja yang ada."""
import struct
from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
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


def sprite(dec, w, h, interleave):
    img = Image.new("RGB", (w, h), (0, 0, 0))
    px = img.load()
    wb = w // 4  # byte per baris @2bpp
    for r in range(h):
        if interleave:
            base = (r & 1) * (wb * ((h + 1) // 2)) + (r >> 1) * wb
        else:
            base = r * wb
        if base + wb > len(dec):
            continue
        for cb in range(wb):
            b = dec[base + cb]
            for p in range(4):
                px[cb * 4 + p, r] = CGA[(b >> (6 - 2 * p)) & 3]
    return img


b = open(D + "\\MECHS", "rb").read()
first = struct.unpack_from("<I", b, 8)[0]
n = first // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]

for il in (False, True):
    cols, cell = 8, 34
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell * 3, rows * (cell + 12) * 3), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    made = 0
    for i, (a, bb, h, w, f, ln, off) in enumerate(recs):
        if w == 0 or h == 0:
            continue
        dec = decode_e4(b[off:off + ln])
        s = sprite(dec, w, h, il).resize((w * 3, h * 3), Image.NEAREST)
        cx = (i % cols) * cell * 3
        cy = (i // cols) * (cell + 12) * 3
        sheet.paste(s, (cx + 4, cy + 4))
        dr.text((cx + 4, cy + h * 3 + 6), "id=%d.%d" % (a, bb), fill=(255, 255, 0))
        made += 1
    tag = "il" if il else "lin"
    sheet.save(D + "\\mechs_sheet_%s.png" % tag)
    print("mechs_sheet_%s.png : %d sprite" % (tag, made))

print("\nDaftar record MECHS:")
for a, bb, h, w, f, ln, off in recs:
    dec_len = len(decode_e4(b[off:off + ln])) if ln else 0
    raw_need = (w // 4) * h
    print("  id=%3d.%d  %2dx%-2d  packed=%3d -> decoded=%3d  (butuh %3d) %s"
          % (a, bb, w, h, ln, dec_len, raw_need,
             "OK" if dec_len == raw_need else "<-- selisih %+d" % (dec_len - raw_need)))
