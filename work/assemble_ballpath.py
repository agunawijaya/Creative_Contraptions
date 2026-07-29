"""Rakit jalur bola LENGKAP: op diskret (2714) + interpolasi (2823) + state,
cocokkan dgn ballpath emulator. Pakai param 2823 tertangkap (to/A/N)."""
import json, os, sys
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import animvm

GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT = r"C:\Projects\Creative_Contraptions\work\emu_caps"
scripts = json.load(open(os.path.join(OUT, "scripts_goal%d.json" % GOAL)))
ballbases = json.load(open(os.path.join(OUT, "ballbases_goal%d.json" % GOAL)))
interp = json.load(open(os.path.join(OUT, "interp_goal%d.json" % GOAL)))
ballpath = json.load(open(os.path.join(OUT, "ball_mode2_goal%d.json" % GOAL)))

base = {}
for p, x, y in ballbases:
    base.setdefault(p, (x, y))


def sgn(v):
    return v - 256 if v >= 0xc8 else v


gen = []
ic = 0   # indeks panggilan 2823 berikutnya
for pi, sc in enumerate(scripts):
    nodes, _ = animvm.parse(bytes(sc["bytes"]))
    bx, by = base.get(pi, (0x140, 0x140))
    for node in nodes:
        tag = node[0]
        if tag == "waypoints":
            for (dx, dy) in node[1]:
                gen.append((sgn(dx) + bx, sgn(dy) + by))
        elif tag in ("op08", "op0a"):
            gen.append((sgn(node[1][0]) + bx, sgn(node[1][1]) + by))
        elif tag in ("op03", "op0c"):
            pr = interp[ic]["params"]; ic += 1
            gen.extend(animvm.interp_2823(pr["fx"], pr["fy"], pr["p32"], pr["p34"], pr["N"], pr["A"]))

# dedupe berurutan spt ballpath
gend = []
for p in gen:
    if not gend or gend[-1] != list(p):
        gend.append([p[0], p[1]])

m = sum(1 for a, b in zip(gend, ballpath) if a == b)
print("gen=%d  emu=%d  cocok berurutan=%d/%d" % (len(gend), len(ballpath), m, min(len(gend), len(ballpath))))
if gend != ballpath:
    for i in range(min(len(gend), len(ballpath))):
        if gend[i] != ballpath[i]:
            print("  divergen di %d: gen=%s emu=%s" % (i, gend[i], ballpath[i]))
            print("  gen sekitar :", gend[max(0,i-2):i+4])
            print("  emu sekitar :", ballpath[max(0,i-2):i+4])
            break
else:
    print("  *** JALUR BOLA IDENTIK 100% ***")
