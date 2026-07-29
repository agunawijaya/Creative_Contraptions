import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())


def pal_idx(idm):
    for i, p in enumerate(g.palette):
        if idm in p[1]:
            return i
    return None


def force(gid, vi):
    for _ in range(400):
        g.start_play(gid, fill="mech")
        if g.cur_variant == vi:
            return True
    return False


allok = True
for gid in g.goal_ids:
    for vi in range(len(g.draws_var.get(gid, {}))):
        assert force(gid, vi), "force gagal %d v%d" % (gid, vi)
        # MENANG: isi semua benar -> anim frames > 0
        for i, s in enumerate(g.slots):
            g.cur_slot = i; g.cur_part = pal_idx(s["correct"]); g.key(pygame.K_RETURN)
        g.key(pygame.K_SPACE)
        nwin = len(g.anim_frames)
        win_ok = g.state == main.PLAYANIM and nwin > 0
        # GAGAL: ulang, kosongkan 1 -> bola jalan
        g.state = main.MENU; force(gid, vi)
        for i, s in enumerate(g.slots[:-1]):
            g.cur_slot = i; g.cur_part = pal_idx(s["correct"]); g.key(pygame.K_RETURN)
        g.key(pygame.K_SPACE)
        fail_ok = g.running and g.run_fail_slot is not None and len(g.ball_path) >= 2
        g.running = False
        print("goal %d v%d: WIN frames=%d ok=%s | FAIL ball=%d ok=%s" %
              (gid, vi, nwin, win_ok, len(g.ball_path), fail_ok))
        allok = allok and win_ok and fail_ok
print("\nSEMUA VARIAN: animasi run (menang) + bola (gagal) OK:", allok)
pygame.quit()
