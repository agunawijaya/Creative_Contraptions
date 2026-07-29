import os, glob
from PIL import Image
F = r"C:\Projects\Creative_Contraptions\work\playframes"
files = sorted(glob.glob(os.path.join(F, "f*.png")))
frames = [Image.open(f).convert("RGB").resize((640,400), Image.NEAREST) for f in files]
out = r"C:\Projects\Creative_Contraptions\work\goal1_animation.gif"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=90, loop=0)
print("frames:", len(frames), "->", out)
