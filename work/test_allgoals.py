import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
random.seed(1234)
g = main.Game(assets.find_data_dir())
print("kategori:", [nm for nm, _ in g.mech_types])


def palette_idx(idm):
    """indeks di palet (yg SUDAH diacak) yg berisi id jawaban."""
    for i, p in enumerate(g.palette):
        if idm in p[1]:
            return i
    return None


def play_once(gid, fill):
    g.start_play(gid, fill=fill)
    assert g.state == main.PLAY
    for i, s in enumerate(g.slots):
        pi = palette_idx(s["correct"])
        if pi is not None:
            g.cur_slot = i
            g.cur_part = pi
            g.key(pygame.K_RETURN)
    won = all(s["filled"] == s["correct"] for s in g.slots)
    g.key(pygame.K_SPACE)
    ok = won and g.state == main.PLAYANIM and g.anim_fail is None
    g.anim_fail = None
    g.running = False
    return g.cur_variant, won, ok


allok = True
for gid in g.goal_ids:
    # Jumlah varian dari CONTRAP, bukan dari berapa berkas tangkapan yang ada.
    # Dulu `len(g.draws_var[gid])` -- tes ini ikut membatasi dirinya pada
    # varian yang kebetulan sempat direkam emulator.
    nvar = len(g.k_goals.get(gid) or ()) or 1
    seen = {}
    # cukup trial utk menutup semua varian (acak, hindari-ulang)
    for _ in range(nvar * 12):
        vi, won, ok = play_once(gid, "mech")
        seen[vi] = seen.get(vi, (True, True))
        seen[vi] = (seen[vi][0] and won, seen[vi][1] and ok)
    covered = sorted(seen)
    all_win = all(w for w, o in seen.values()) and all(o for w, o in seen.values())
    allok = allok and all_win and len(covered) == nvar
    print("GOAL %d %-14s: varian=%d tercakup=%s semua-menang=%s" %
          (gid, main.GOAL_NAMES[gid], nvar, covered, all_win))

# cek Fill Zany & Mix Up juga jalan (varian acak)
for fill in ("zany", "both"):
    vi, won, ok = play_once(g.goal_ids[0], fill)
    print("fill=%s goal1: varian=%d menang=%s (state=%d)" % (fill, vi, won, g.state))

# cek palet benar-benar teracak (beberapa load, ada yg beda urutan)
orders = []
for _ in range(6):
    g.start_play(g.goal_ids[0], fill="mech")
    orders.append(tuple(p[0] for p in g.palette))
print("palet contoh:", orders[0][:5], "| teracak (ada urutan beda):", len(set(orders)) > 1)

print("\nSEMUA GOAL+VARIAN BISA DIMENANGKAN:", allok)
pygame.quit()
