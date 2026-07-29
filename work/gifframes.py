from PIL import Image
g = Image.open(r"C:\Projects\Creative_Contraptions\work\port_full_goal1.gif")
idxs = [20, 28, 36, 44]
w, h = g.size
sheet = Image.new("RGB", (w, h * len(idxs)), (0, 0, 0))
for k, i in enumerate(idxs):
    g.seek(i)
    sheet.paste(g.convert("RGB"), (0, k * h))
sheet.save(r"C:\Projects\Creative_Contraptions\work\port_ball_frames.png")
print("saved", sheet.size)
