from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
real = Image.open(D + r"\shots\20_contraption.png").convert("RGB")
recon = Image.open(D + r"\reconstruct_goal1.png").convert("RGB")

W = 900
real = real.resize((W, int(real.height * W / real.width)), Image.NEAREST)
recon = recon.resize((W, int(recon.height * W / recon.width)), Image.NEAREST)

gap = 30
out = Image.new("RGB", (W, real.height + recon.height + gap * 2 + 20), (20, 20, 20))
dr = ImageDraw.Draw(out)
dr.text((8, 6), "ASLI (game di DOSBox):", fill=(255, 255, 0))
out.paste(real, (0, 24))
y2 = 24 + real.height + gap
dr.text((8, y2 - 18), "REKONSTRUKSI dari aset kita + posisi dari data CONTRAP:", fill=(0, 255, 128))
out.paste(recon, (0, y2))
out.save(D + r"\compare_goal1.png")
print("-> compare_goal1.png", out.size)
