"""Cari formula 2823 dari data tangkapan (param -> titik)."""
import json
c = json.load(open(r"C:\Projects\Creative_Contraptions\work\emu_caps\interp_goal1.json"))

def tdiv(a, b):
    # pembagian truncate-toward-zero (spt C int div)
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q

for k, call in enumerate(c):
    p = call["params"]; pts = call["pts"]
    fx, fy, tx, ty, N, A = p["fx"], p["fy"], p["p32"], p["p34"], p["N"], p["A"]
    print("\n#%d A=%d from=(%d,%d) to=(%d,%d) N=%d pts=%d" % (k, A, fx, fy, tx, ty, N, len(pts)))
    print("  actual:", pts)
    # model linear murni (truncate)
    lin = [(fx + tdiv((tx - fx) * i, N), fy + tdiv((ty - fy) * i, N)) for i in range(1, len(pts) + 1)]
    print("  linear:", lin)
    dev = [(pts[i][0] - lin[i][0], pts[i][1] - lin[i][1]) for i in range(len(pts))]
    print("  dev   :", dev)
