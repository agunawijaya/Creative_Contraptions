import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
mt = {t for t, _ in main.MECH_TYPES}
for gi, gid in enumerate(g.goal_ids):
    g.start_play(gid)
    print("GOAL %d (%s): %d slot" % (gid, main.GOAL_NAMES.get(gid, "?"), len(g.slots)))
    for i, s in enumerate(g.slots):
        ok = "OK" if s["correct"] in mt else "TIDAK ADA di MECH_TYPES!"
        print("   %c correct=%d sprite=%d  %s" % (0x41 + i, s["correct"], s["sprite"], ok))
    reach = g._reach(gid); bp = g._ballpath(gid)
    print("   reach=%s ballpath_len=%d" % (reach, len(bp)))
pygame.quit()
