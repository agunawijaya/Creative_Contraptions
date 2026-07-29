"""Cari font 8x8 di biner: render region sbg grid glyph, cari yg terbaca."""
from PIL import Image

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()


def render_window(start, cols=32, rows=16, scale=3):
    """Render `cols*rows` glyph 8x8 mulai `start` (forward, 8 byte/glyph)."""
    img = Image.new("RGB", (cols * 9 * scale, rows * 9 * scale), (20, 20, 40))
    px = img.load()
    for g in range(cols * rows):
        base = start + g * 8
        gx = (g % cols) * 9 * scale
        gy = (g // cols) * 9 * scale
        for row in range(8):
            if base + row >= len(b):
                break
            bits = b[base + row]
            for col in range(8):
                if bits & (0x80 >> col):
                    for sy in range(scale):
                        for sx in range(scale):
                            X = gx + col * scale + sx
                            Y = gy + row * scale + sy
                            if X < img.width and Y < img.height:
                                px[X, Y] = (255, 255, 255)
    return img


# Render beberapa jendela kandidat di seluruh file
import sys
starts = [0x1E00, 0x2000, 0x2200, 0x2400, 0x8B00, 0x9000, 0x9500, 0xA000, 0xB000]
sheet = Image.new("RGB", (32 * 9 * 3, len(starts) * (16 * 9 * 3 + 16)), (0, 0, 0))
from PIL import ImageDraw
dr = ImageDraw.Draw(sheet)
y = 0
for s in starts:
    w = render_window(s, 32, 12, 3)
    dr.text((4, y), "offset 0x%X" % s, fill=(255, 255, 0))
    sheet.paste(w, (0, y + 12))
    y += 12 * 9 * 3 + 16
sheet.save(r"C:\Projects\Creative_Contraptions\work\font_hunt.png")
print("-> font_hunt.png")
