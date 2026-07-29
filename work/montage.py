import os
import shutil
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work\assets"

# ANIMATE bukan bitmap -> buang render-nya yang menyesatkan
an = os.path.join(D, "ANIMATE")
if os.path.isdir(an):
    shutil.rmtree(an)
    print("dihapus: render ANIMATE (bukan data bitmap)")

files = sorted(os.listdir(os.path.join(D, "GRAPH")))
print("GRAPH PNG: %d" % len(files))

sel = files[:60]
cols, cw, ch = 10, 200, 150
sheet = Image.new("RGB", (cols * cw, ((len(sel) + cols - 1) // cols) * ch), (30, 30, 30))
for i, f in enumerate(sel):
    im = Image.open(os.path.join(D, "GRAPH", f))
    im.thumbnail((cw - 8, ch - 8), Image.NEAREST)
    x = (i % cols) * cw + 4
    y = (i // cols) * ch + 4
    sheet.paste(im, (x, y))
sheet.save(r"C:\Projects\Creative_Contraptions\work\graph_montage.png")
print("montage -> graph_montage.png", sheet.size)

gifs = sorted(os.listdir(os.path.join(D, "_gif")))
print("\nGIF (%d) contoh:" % len(gifs))
for g in gifs[:14]:
    print("  " + g)
