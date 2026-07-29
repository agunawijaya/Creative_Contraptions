import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN)                 # TITLE->MENU
g.key(pygame.K_DOWN); g.key(pygame.K_RETURN)   # Fill in Mechanisms -> GOAL
g.key(pygame.K_RETURN)                 # goal1 -> PLAY (Fill)
assert g.state == main.PLAY
print("Masuk Fill. Slot:", [(chr(0x41+i), s["correct"]) for i, s in enumerate(g.slots)])

typ_to_partidx = {t: i for i, (t, _) in enumerate(main.MECH_TYPES)}


def place(slot_i, typ, correct=True):
    g.cur_slot = slot_i
    use_typ = typ if correct else next(t for t, _ in main.MECH_TYPES if t != typ)
    g.cur_part = typ_to_partidx[use_typ]
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
