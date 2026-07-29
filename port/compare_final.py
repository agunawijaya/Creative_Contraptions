"""Montase: render port (assembled) vs ground truth screenshot user, 6 goal."""
import os
from PIL import Image, ImageDraw

here = os.path.dirname(__file__)
scores = {1: 88, 2: 83, 3: 90, 4: 58, 5: 77, 6: 56}
rows = []
for g in range(1, 7):
    mine = Image.open(os.path.join(here, "asm_goal%d.png" % g)).convert("RGB")   # 640x400
    gt = Image.open(os.path.join(here, "gtu_goal%d.png" % g)).convert("RGB").resize((640, 400), Image.NEAREST)
    row = Image.new("RGB", (1290, 400), (20, 20, 20))
    row.paste(gt, (0, 0)); row.paste(mine, (650, 0))
    rows.append((g, row))

W = 1290
H = sum(r[1].height + 26 for r in rows)
sheet = Image.new("RGB", (W, H), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
y = 0
for g, row in rows:
    dr.text((6, y + 4), "GOAL %d  -  KIRI: game asli (ground truth)   KANAN: port (cocok zany %d%%)"
            % (g, scores[g]), fill=(255, 255, 0))
    sheet.paste(row, (0, y + 22))
    y += row.height + 26
sheet.save(os.path.join(here, "compare_final.png"))
print("-> compare_final.png", sheet.size)
