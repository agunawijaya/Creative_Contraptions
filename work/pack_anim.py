"""Pack frame animasi (vframes_goalN[_vV] PNG) -> port/cc/anim/goalN[_vV].dat (2bpp+zlib).
Sekarang PER-VARIAN: tiap (goal,varian) punya .dat + ball + reach sendiri, semuanya
diturunkan dari eksekusi game asli (emulator), tanpa tebakan.
Format .dat: header 'CCA1' + u16 goal + u16 nframes, lalu zlib(concat frame 2bpp 16000B)."""
import os, glob, struct, zlib, json
from PIL import Image

CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
LUT = {c: i for i, c in enumerate(CGA)}
OUT = r"C:\Projects\Creative_Contraptions\port\cc\anim"
CAP = r"C:\Projects\Creative_Contraptions\work\emu_caps"
WORK = r"C:\Projects\Creative_Contraptions\work"
DRAWS = r"C:\Projects\Creative_Contraptions\port\cc\draws"
os.makedirs(OUT, exist_ok=True)

# jumlah varian per goal (dari direktori CONTRAP). Goal 7 = 9 demo mekanisme (Review).
VARIANTS = {1: 2, 2: 1, 3: 2, 4: 2, 5: 1, 6: 2, 7: 9}


def nearest(c):
    if c in LUT:
        return LUT[c]
    best, bi = 1e9, 1
    for i, cc in enumerate(CGA):
        d = sum((a - b) ** 2 for a, b in zip(c, cc))
        if d < best:
            best, bi = d, i
    return bi


def pack(goal, variant):
    vt = "_v%d" % variant
    F = os.path.join(WORK, "vframes_goal%d%s" % (goal, vt))
    files = sorted(glob.glob(os.path.join(F, "v*.png")))
    if not files:
        print("goal %d%s: tak ada frame" % (goal, vt)); return
    blob = bytearray()
    for f in files:
        im = Image.open(f).convert("RGB")
        px = im.load()
        for y in range(200):
            for xb in range(0, 320, 4):
                b = 0
                for p in range(4):
                    b = (b << 2) | nearest(px[xb + p, y])
                blob.append(b)
    packed = zlib.compress(bytes(blob), 9)
    with open(os.path.join(OUT, "goal%d%s.dat" % (goal, vt)), "wb") as fo:
        fo.write(b"CCA1" + struct.pack("<HH", goal, len(files)) + packed)
    # jalur bola LAYAR (ballscreen) per-varian
    bs = json.load(open(os.path.join(CAP, "ballscreen_goal%d%s.json" % (goal, vt))))
    ballpath = [[p[0], p[1]] for p in bs]
    json.dump(ballpath, open(os.path.join(OUT, "ball%d%s.json" % (goal, vt)), "w"))
    # reach INDEX per slot mekanisme dari adegan statis varian ini
    draws = json.load(open(os.path.join(DRAWS, "draws_goal%d%s.json" % (goal, vt))))
    mech = [d for d in draws if d["arch"] == "MECHS" and d["idx"] >= 0]
    reach = []
    for d in mech:
        cx, cy = d["x"] + 16, d["y"] + 12
        best, bi = 1e9, len(ballpath) - 1
        for i, (bx, by) in enumerate(ballpath):
            dist = (bx - cx) ** 2 + (by - cy) ** 2
            if dist < best:
                best, bi = dist, i
        reach.append({"x": d["x"], "y": d["y"], "reach": bi, "dist": int(best ** 0.5)})
    json.dump(reach, open(os.path.join(OUT, "reach%d%s.json" % (goal, vt)), "w"))
    print("goal %d%s: %d frame -> %d KB; ballpath=%d; reach=%s" %
          (goal, vt, len(files), (len(packed) + 8) // 1024, len(ballpath),
           [(r["reach"], r["dist"]) for r in reach]))


for goal, nv in VARIANTS.items():
    for v in range(nv):
        pack(goal, v)
