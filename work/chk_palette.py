import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())

# 1) apakah tiap kategori punya sprite MECHS yg valid (first_of_major)?
print("=== ikon palet 9 kategori (mech) ===")
mont = pygame.Surface((9 * 40, 40)); mont.fill(cga.PALETTE[1])
for i, (nm, ids) in enumerate(main.MECH_CATEGORIES):
    rec = g.mechs.first_of_major(ids[0])
    spr = g.mechs.sprite(rec) if rec else None
    ok = spr is not None
    print("  %-15s ids=%s first_of_major(%d)=%s %s" %
          (nm, ids, ids[0], "idx%d %dx%d" % (rec["idx"], rec["w"], rec["h"]) if rec else "NONE",
           "" if ok else "  <-- KOSONG!"))
    if spr:
        mont.blit(spr, (i * 40 + 4, 8))
Image.frombytes("RGB", (9 * 40 * 3, 120),
                pygame.image.tostring(pygame.transform.scale(mont, (9 * 40 * 3, 120)), "RGB")
                ).save(r"C:\Projects\Creative_Contraptions\work\palette_icons.png")
print("-> palette_icons.png")

# 2) tiap varian: apakah tiap slot punya entri palet yg cocok?
print("\n=== cek matchability semua varian ===")
import random
random.seed(1)
bad = 0
for gid in g.goal_ids:
    for vi in range(len(g.draws_var.get(gid, {}))):
        for _ in range(400):
            g.start_play(gid, fill="mech")
            if g.cur_variant == vi:
                break
        for i, s in enumerate(g.slots):
            match = [p[0] for p in g.palette if s["correct"] in p[1]]
            if not match:
                print("  goal %d v%d slot %d type=%d -> TIDAK ADA di palet!" %
                      (gid, vi, i, s["correct"]))
                bad += 1
print("slot tanpa match:", bad)
pygame.quit()
