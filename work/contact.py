import os, glob
from PIL import Image
F = r"C:\Projects\Creative_Contraptions\work\playframes"
files = sorted(glob.glob(os.path.join(F, "f*.png")))
cols, sw, sh = 6, 160, 100
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * sw, rows * sh), (20, 20, 20))
for i, f in enumerate(files):
    im = Image.open(f).resize((sw, sh))
    sheet.paste(im, ((i % cols) * sw, (i // cols) * sh))
sheet.save(os.path.join(F, "..", "contact_play.png"))
print("contact.png", sheet.size, len(files), "frames")
