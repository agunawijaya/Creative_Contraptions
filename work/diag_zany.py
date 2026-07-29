import os, sys, struct
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
alltypes = set()
for gid in g.goal_ids:
    var = g.goals[gid][0]
    zt = [z[2] for z in var["zany"]]
    zdraws = [d for d in g.draws.get(gid, []) if d["arch"] == "GRAPH"]
    print("GOAL %d (%s): %d zany; tipe(id_major GRAPH)=%s; GRAPH draws=%d" %
          (gid, main.GOAL_NAMES[gid], len(var["zany"]), zt, len(zdraws)))
    alltypes.update(zt)
print("\nSemua tipe zany dipakai:", sorted(alltypes), "(%d unik)" % len(alltypes))
# berapa id_major di GRAPH total
graw = open(os.path.join(assets.find_data_dir(), "GRAPH"), "rb").read()
n = struct.unpack_from("<I", graw, 8)[0] // 12
gmaj = sorted({graw[i*12] for i in range(n)})
print("GRAPH id_major total: %d ->" % len(gmaj), gmaj)
pygame.quit()
