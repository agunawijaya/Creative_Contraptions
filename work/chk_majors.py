import os, sys
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
for mj in (78, 79, 80, 81, 83):
    idxs = graph.by_major.get(mj, [])
    print("major %d: %d frames -> record idx %s" %
          (mj, len(idxs), [graph.records[i]["idx"] for i in idxs]))
    for i in idxs:
        r = graph.records[i]
        print("    idx %d  %dx%d  minor=%d" % (r["idx"], r["w"], r["h"], r["minor"]))
