import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
# ⚠ Layar LEVEL ditambahkan belakangan; uji ini sempat MELEWATKANNYA dan
# gagal diam-diam. `MECH_TYPES` juga sudah berganti nama jadi MECH_CATEGORIES.
# ⚠ Alur pembuka gim: TITLE -> ENTER -> CREDITS -> ENTER -> SET UP
# (dua pertanyaan Y/N) -> MENU. Ini dari `main_.c`, bukan tambahan port.
g.key(pygame.K_RETURN)                 # TITLE -> CREDITS
g.key(pygame.K_RETURN)                 # CREDITS -> SET UP
g.key(pygame.K_y); g.key(pygame.K_y)   # -> MENU
g.key(pygame.K_DOWN); g.key(pygame.K_RETURN)   # Fill in Mechanisms -> LEVEL
g.key(pygame.K_RETURN)                 # Apprentice -> INSTRUKSI (menu9)
g.key(pygame.K_RETURN)                 # ENTER -> GOAL
g.key(pygame.K_RETURN)                 # goal1 -> PLAY (Fill)
assert g.state == main.PLAY
print("Masuk Fill. Slot:", [(chr(0x41+i), s["correct"]) for i, s in enumerate(g.slots)])

# Entri palet = (nama, ids, arsip, sprite). Slot dicocokkan lewat `ids`,
# bukan lewat indeks tetap -- paletnya DIKOCOK tiap muat.
def pal_of(idm):
    for i, entry in enumerate(g.palette):
        if idm in entry[1]:
            return i
    return None


def place(slot_i, typ, correct=True):
    g.cur_slot = slot_i
    if correct:
        c = pal_of(typ)
    else:
        c = next(i for i, e in enumerate(g.palette) if typ not in e[1])
    if c is None:
        print("  (tak ada entri palet untuk tipe %d)" % typ)
        return
    use_typ = g.palette[c][1][0]
    g.cur_part = c
    g.key(pygame.K_RETURN)
    print("  place slot %c type %d -> %s" % (0x41 + slot_i, use_typ, g.message))


# coba salah dulu di slot A
place(0, g.slots[0]["correct"], correct=False)
# SPACE saat belum lengkap -> bola jalan & GAGAL; tunggu selesai
g.key(pygame.K_SPACE)
print("SPACE belum lengkap -> running=%s fail_slot=%s" % (g.running, g.run_fail_slot))
for _ in range(400):
    g.tick()
    if not g.running and g.ball_i < 0:
        break
print("  run gagal selesai: msg=%s" % g.message)
g.run_fail_slot = None
# isi semua benar
for i, s in enumerate(g.slots):
    place(i, s["correct"], correct=True)
print("skor=", g.score, "semua terisi benar=",
      all(s["filled"] == s["correct"] for s in g.slots))
# SPACE -> menang, animasi jalan
g.key(pygame.K_SPACE)
print("SPACE lengkap -> state=%d (PLAYANIM=%d) from_play=%s frames=%d" %
      (g.state, main.PLAYANIM, g.anim_from_play, len(g.anim_frames)))
for _ in range(600):
    g.tick()
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\fill_win.png")
print("anim selesai i=%d msg render OK" % g.anim_i)
pygame.quit()
