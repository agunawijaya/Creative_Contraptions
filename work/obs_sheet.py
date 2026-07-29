import os, glob, sys
from PIL import Image
mode = sys.argv[1] if len(sys.argv) > 1 else "review"
F = r"C:\Projects\Creative_Contraptions\work\obs_%s" % mode
files = sorted(glob.glob(os.path.join(F, "obs*.png")))
# dedupe visual berturut (kadang beda 1px)
uniq = []
prev = None
for f in files:
    im = Image.open(f).convert("RGB")
    b = im.tobytes()
    if b != prev:
        uniq.append(im); prev = b
print("total file:", len(files), "unik:", len(uniq))
cols = 6
sw, sh = 160, 100
rows = (len(uniq) + cols - 1) // cols
sheet = Image.new("RGB", (cols * sw, rows * sh), (10, 10, 10))
for i, im in enumerate(uniq):
    sheet.paste(im.resize((sw, sh)), ((i % cols) * sw, (i // cols) * sh))
sheet.save(r"C:\Projects\Creative_Contraptions\work\obs_%s_sheet.png" % mode)
print("-> obs_%s_sheet.png (%dx%d)" % (mode, sheet.size[0], sheet.size[1]))
