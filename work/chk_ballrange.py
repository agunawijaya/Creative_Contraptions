import json
bs = json.load(open(r'C:\Projects\Creative_Contraptions\work\emu_caps\ballscreen_goal128.json'))
xs = [p[0] for p in bs]
ys = [p[1] for p in bs]
print("ball_screen titik:", len(bs))
print("x range:", min(xs), "..", max(xs))
print("y range:", min(ys), "..", max(ys))
# fase kasar: berapa titik di kiri (x<120, area ayam) vs kanan (x>200, area gajah)
left = sum(1 for x in xs if x < 120)
right = sum(1 for x in xs if x > 200)
print("titik kiri(ayam) x<120:", left, " kanan(gajah) x>200:", right)
