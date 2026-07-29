import json, sys
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
import os
D = assets.find_data_dir()
mechs = assets.Archive(os.path.join(D, "MECHS"))
graph = assets.Archive(os.path.join(D, "GRAPH"))

def mj(a, i):
    ar = mechs if a == "MECHS" else graph
    return ar.records[i]["major"] if a and 0 <= i < len(ar.records) else None

def show(path, label):
    d = json.load(open(path))
    print("---", label, "(%d entries)" % len(d))
    for e in sorted(d, key=lambda r: (r["arch"] or "", r["y"], r["x"])):
        print("   %-5s idx=%-4s (%3d,%3d) %2dx%-2d major=%s" %
              (e["arch"], e["idx"], e["x"], e["y"], e["w"], e["h"], mj(e["arch"], e["idx"])))

show(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal1.json", "EXISTING draws_goal1")
show(r"C:\Projects\Creative_Contraptions\work\emu_caps\draws_goal1_v0.json", "NEW v0")
show(r"C:\Projects\Creative_Contraptions\work\emu_caps\draws_goal1_v1.json", "NEW v1")
