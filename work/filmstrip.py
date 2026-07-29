"""Bentangkan frame GIF jadi filmstrip untuk verifikasi animasi."""
import os
from PIL import Image, ImageDraw, ImageSequence

G = r"C:\Projects\Creative_Contraptions\work\assets\_gif"
picks = [f for f in sorted(os.listdir(G)) if "4frames" in f or "5frames" in f or "3frames" in f][:8]

rows = []
for f in picks:
    im = Image.open(os.path.join(G, f))
    frames = [fr.convert("RGB").copy() for fr in ImageSequence.Iterator(im)]
    w = sum(x.width for x in frames) + 6 * len(frames)
    h = max(x.height for x in frames) + 22
    row = Image.new("RGB", (w, h), (30, 30, 30))
    x = 0
    for fr in frames:
        row.paste(fr, (x + 3, 18))
        x += fr.width + 6
    ImageDraw.Draw(row).text((4, 3), "%s  (%d frame)" % (f.replace(".gif", ""), len(frames)), fill=(255, 255, 0))
    rows.append(row)
    print("%-42s %d frame  %dx%d" % (f, len(frames), frames[0].width, frames[0].height))

W = max(r.width for r in rows)
H = sum(r.height + 8 for r in rows)
sheet = Image.new("RGB", (W, H), (20, 20, 20))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height + 8
sheet.save(r"C:\Projects\Creative_Contraptions\work\filmstrip.png")
print("\n-> filmstrip.png", sheet.size)
