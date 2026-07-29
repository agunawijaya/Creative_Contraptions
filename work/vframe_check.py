import glob, os
from PIL import Image
F = r"C:\Projects\Creative_Contraptions\work\vframes_goal1"
files = sorted(glob.glob(os.path.join(F, "v*.png")))
# ambil frame fase fisika (setelah ~frame 60, saat bola bergerak di mesin)
idxs = [70, 90, 110, 130]
sheet = Image.new("RGB", (320, 200*len(idxs)))
for k, i in enumerate(idxs):
    if i < len(files):
        sheet.paste(Image.open(files[i]).convert("RGB"), (0, k*200))
sheet.save(r"C:\Projects\Creative_Contraptions\work\vframe_check.png")
print("total", len(files), "saved")
