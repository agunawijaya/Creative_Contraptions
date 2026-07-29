import os, sys, json
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
D = assets.find_data_dir()
goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
graph = assets.Archive(os.path.join(D, "GRAPH"))

def major_of(arch, idx):
    return arch.records[idx]["major"] if 0 <= idx < len(arch.records) else None

for gid in sorted(goals):
    print("=== GOAL", gid, " variants:", len(goals[gid]), "===")
    for vi, var in enumerate(goals[gid]):
        print(" var%d mech(y,x,type)=%s" % (vi, var["mech"]))
        print("      zany(y,x,type)=%s" % (var["zany"],))
    # bandingkan var0 vs draws_goal (jika ada)
    dp = r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal%d.json" % gid
    if os.path.exists(dp):
        draws = json.load(open(dp))
        dm = [(d["x"], d["y"], major_of(mechs, d["idx"])) for d in draws if d["arch"] == "MECHS"]
        print("   draws MECHS (x,y,major)=%s" % dm)
        v0 = goals[gid][0]["mech"]
        print("   var0 MECHS (x,y,type)=%s" % [(x, y, t) for (y, x, t) in v0])
