import os, glob, sys
from PIL import Image
G = sys.argv[1] if len(sys.argv) > 1 else "1"
F = r"C:\Projects\Creative_Contraptions\work\vframes_goal%s" % G
files = sorted(glob.glob(os.path.join(F, "v*.png")))
frames = [Image.open(f).convert("RGB").resize((640, 400), Image.NEAREST) for f in files]
out = r"C:\Projects\Creative_Contraptions\work\port_true_goal%s.gif" % G
frames[0].save(out, save_all=True, append_images=frames[1:], duration=70, loop=0)
print("frames:", len(frames), "->", out)
# contact sheet cek
idxs = [i for i in range(0, len(files), max(1, len(files)//8))][:8]
cols = 4; sw, sh = 160, 100
rows = (len(idxs)+cols-1)//cols
sheet = Image.new("RGB", (cols*sw, rows*sh))
for k, i in enumerate(idxs):
    sheet.paste(Image.open(files[i]).resize((sw, sh)), ((k % cols)*sw, (k//cols)*sh))
sheet.save(r"C:\Projects\Creative_Contraptions\work\true_contact.png")
print("contact ok")
