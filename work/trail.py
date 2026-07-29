import os, glob
from PIL import Image
import colorsys
F = r"C:\Projects\Creative_Contraptions\work\frames"
files = sorted(glob.glob(os.path.join(F, "f*.png")))
imgs = [Image.open(f).convert("RGB") for f in files]
W, H = imgs[0].size
base = imgs[0].load()
# background = frame 0 (kontraption statis). Ball & animasi = piksel yg berubah.
trail = Image.new("RGB", (W, H), (0, 0, 0))
tp = trail.load()
# gambar background redup
for y in range(H):
    for x in range(W):
        r, g, b = base[x, y]
        tp[x, y] = (r // 4, g // 4, b // 4)
centroids = []
for fi, im in enumerate(imgs):
    px = im.load()
    hue = fi / max(1, len(imgs) - 1)
    cr, cg, cb = [int(c * 255) for c in colorsys.hsv_to_rgb(hue * 0.85, 1, 1)]
    xs = ys = n = 0
    for y in range(H):
        for x in range(W):
            if px[x, y] != base[x, y]:
                tp[x, y] = (cr, cg, cb)
                xs += x; ys += y; n += 1
    centroids.append((round(xs / n, 1), round(ys / n, 1)) if n else None)
trail.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(F, "..", "trail.png"))
print("trail.png saved; per-frame changed-pixel centroid:")
print(centroids)
