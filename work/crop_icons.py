from PIL import Image
src = Image.open(r"C:\Projects\Creative_Contraptions\work\obs_menu\obs02.png").convert("RGB")
print("menu VRAM size:", src.size)
# 4 ikon menu di (48,39/66/93/120), 44x25
boxes = [(48, 39), (48, 66), (48, 93), (48, 120)]
names = ["review", "fillmech", "zany", "mixup"]
sheet = Image.new("RGB", (44 * 4, 25), (0, 0, 0))
import os
os.makedirs(r"C:\Projects\Creative_Contraptions\port\cc\anim\icons", exist_ok=True)
for i, (x, y) in enumerate(boxes):
    ic = src.crop((x, y, x + 44, y + 25))
    ic.save(r"C:\Projects\Creative_Contraptions\port\cc\anim\icons\%s.png" % names[i])
    sheet.paste(ic, (i * 44, 0))
sheet.resize((44 * 4 * 3, 25 * 3), Image.NEAREST).save(r"C:\Projects\Creative_Contraptions\work\menu_icons_check.png")
print("saved 4 icons + menu_icons_check.png")
