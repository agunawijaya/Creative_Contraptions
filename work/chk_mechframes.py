import os, sys
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
D = assets.find_data_dir()
mechs = assets.Archive(os.path.join(D, "MECHS"))
NAMES = {100: "Inclined Plane", 101: "Inclined Plane", 110: "Pulley", 111: "Pulley",
         112: "Pulley", 133: "Pulley", 115: "Wheel&Axle", 120: "Wedge", 130: "Pendulum",
         131: "Pendulum", 132: "Magnet", 135: "Screw", 140: "Lever", 141: "Lever", 150: "Spring"}
for mj in sorted(mechs.by_major):
    idxs = mechs.by_major[mj]
    print("major %3d (%-14s): %d record -> idx %s  ukuran %s" %
          (mj, NAMES.get(mj, "?"), len(idxs), [mechs.records[i]["idx"] for i in idxs],
           [(mechs.records[i]["w"], mechs.records[i]["h"]) for i in idxs]))
