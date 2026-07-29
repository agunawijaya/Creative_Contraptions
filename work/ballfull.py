import json, os
D = json.load(open(r"C:\Projects\Creative_Contraptions\work\emu_caps\draworder_goal1.json"))
pts = [(x, y) for (sptr, x, y, w, h) in D if sptr == 0x05e6]
print("total ball(0x5e6) draws:", len(pts))
# dedupe berurutan
seq = []
for p in pts:
    if not seq or seq[-1] != p:
        seq.append(p)
print("urutan penuh (%d):" % len(seq))
for i, p in enumerate(seq):
    print("  %2d: %s" % (i, p))
