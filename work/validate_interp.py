import json, sys, os
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc.animvm import interp_2823

total = ok = 0
for goal in range(1, 7):
    p = r"C:\Projects\Creative_Contraptions\work\emu_caps\interp_goal%d.json" % goal
    if not os.path.exists(p):
        continue
    calls = json.load(open(p))
    for c in calls:
        pr = c["params"]
        got = interp_2823(pr["fx"], pr["fy"], pr["p32"], pr["p34"], pr["N"], pr["A"])
        exp = [tuple(t) for t in c["pts"]]
        total += 1
        if got == exp:
            ok += 1
        else:
            print("GOAL%d MISMATCH params=%s\n  got=%s\n  exp=%s" % (goal, pr, got, exp))
print("interp_2823 EKSAK: %d/%d panggilan" % (ok, total))
