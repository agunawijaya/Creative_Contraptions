from PIL import Image, ImageDraw

orig = Image.open(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png").convert("RGB")
mine = Image.open(r"C:\Projects\Creative_Contraptions\port\scr_contraption.png").convert("RGB")
W = 900
orig = orig.resize((W, int(orig.height * W / orig.width)), Image.NEAREST)
mine = mine.resize((W, int(mine.height * W / mine.width)), Image.NEAREST)
gap = 26
out = Image.new("RGB", (W, orig.height + mine.height + gap * 2), (20, 20, 20))
dr = ImageDraw.Draw(out)
dr.text((6, 4), "ASLI (game):", fill=(255, 255, 0))
out.paste(orig, (0, 22))
y2 = 22 + orig.height + gap
dr.text((6, y2 - 18), "PORT (palet & warna kini SUDAH cocok; sprite/komponen masih perlu diperbaiki):", fill=(0, 255, 128))
out.paste(mine, (0, y2))
out.save(r"C:\Projects\Creative_Contraptions\work\compare_fix.png")
print("-> compare_fix.png")
