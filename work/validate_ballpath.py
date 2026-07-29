"""Validasi: interpreter (scripts + base per-part) mereproduksi ballpath emulator."""
import json, os, sys
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import animvm

GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT = r"C:\Projects\Creative_Contraptions\work\emu_caps"
scripts = json.load(open(os.path.join(OUT, "scripts_goal%d.json" % GOAL)))
ballbases = json.load(open(os.path.join(OUT, "ballbases_goal%d.json" % GOAL)))
ballpath = json.load(open(os.path.join(OUT, "ball_mode2_goal%d.json" % GOAL)))

# base per part (part_idx -> (bx,by)); ambil kemunculan pertama
base = {}
for p, x, y in ballbases:
    base.setdefault(p, (x, y))


def sgn(v):
    return v - 256 if v >= 0xc8 else v   # ambang 0xc8 spt 2714


# hasilkan titik bola dari op0x00/08/0a tiap part berurutan
gen = []
for pi, sc in enumerate(scripts):
    b = bytes(sc["bytes"])
    nodes, _ = animvm.parse(b)
    bx, by = base.get(pi, (0x140, 0x140))
    for node in nodes:
        tag = node[0]
        if tag == "waypoints":
            for (dx, dy) in node[1]:
                gen.append((sgn(dx) + bx, sgn(dy) + by))
        elif tag in ("op08", "op0a"):
            dx, dy = node[1][0], node[1][1]
            gen.append((sgn(dx) + bx, sgn(dy) + by))

# ballpath emulator sudah dedupe berurutan; dedupe gen juga
gend = []
for p in gen:
    if not gend or gend[-1] != list(p):
        gend.append(list(p))

print("gen(mentah)=%d gen(dedupe)=%d  ballpath=%d" % (len(gen), len(gend), len(ballpath)))
# cocokkan
m = sum(1 for a, b in zip(gend, ballpath) if a == b)
print("cocok berurutan: %d / %d" % (m, min(len(gend), len(ballpath))))
print("gen[:12] :", gend[:12])
print("emu[:12] :", ballpath[:12])
