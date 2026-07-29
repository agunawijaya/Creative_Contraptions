import os, sys, json
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
D = assets.find_data_dir()
goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))

def major_of(arch, idx):
    return arch.records[idx]["major"] if 0 <= idx < len(arch.records) else None

for gid in range(1, 8):
    dp = r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal%d.json" % gid
    if not os.path.exists(dp):
        continue
    draws = json.load(open(dp))
    var0 = goals[gid][0]
    # CONTRAP entries as (x,y,type,kind)
    cc = [(x, y, t, "mech") for (y, x, t) in var0["mech"]] + \
         [(x, y, t, "zany") for (y, x, t) in var0["zany"]]
    print("=== GOAL", gid, "=== draws=%d  contrap=%d (mech=%d zany=%d)" %
          (len([d for d in draws if d["idx"] >= 0]), len(cc), len(var0["mech"]), len(var0["zany"])))
    used = [False] * len(cc)
    for d in draws:
        if d["idx"] < 0:
            continue
        arch = graph if d["arch"] == "GRAPH" else mechs
        mj = major_of(arch, d["idx"])
        # cari CONTRAP entry dgn (x,y) sama
        hit = None
        for i, (x, y, t, k) in enumerate(cc):
            if not used[i] and x == d["x"] and y == d["y"]:
                hit = i; break
        if hit is not None:
            used[hit] = True
            x, y, t, k = cc[hit]
            tag = "OK" if t == mj else ("~cat" if abs(t - mj) < 10 else "TYPE!=")
            print("  draw %-5s idx=%-4d (%3d,%3d) major=%-3s -> CONTRAP %s type=%-3d [%s]" %
                  (d["arch"], d["idx"], d["x"], d["y"], mj, k, t, tag))
        else:
            print("  draw %-5s idx=%-4d (%3d,%3d) major=%-3s -> NO CONTRAP MATCH (background?)" %
                  (d["arch"], d["idx"], d["x"], d["y"], mj))
    miss = [cc[i] for i in range(len(cc)) if not used[i]]
    if miss:
        print("  CONTRAP entries WITHOUT a draw:", miss)
