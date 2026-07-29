import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
OUT = r"C:\Projects\Creative_Contraptions\work"


def snap():
    fb = cga.make_framebuffer(); g.draw(fb)
    return Image.frombytes("RGB", (640, 400),
                           pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))


def force(gid, vi, fill="mech"):
    for _ in range(300):
        g.start_play(gid, fill=fill)
        if g.cur_variant == vi:
            return True
    return False


def pal_idx(idm):
    for i, p in enumerate(g.palette):
        if idm in p[1]:
            return i
    return None


# --- WIN animasi goal1 v1 (isi semua benar, SPACE) ---
assert force(1, 1, "mech"), "gagal paksa v1"
for i, s in enumerate(g.slots):
    g.cur_slot = i; g.cur_part = pal_idx(s["correct"]); g.key(pygame.K_RETURN)
g.key(pygame.K_SPACE)
frames = []
for _ in range(200):
    g.tick(); frames.append(snap())
frames[0].save(os.path.join(OUT, "final_g1v1_win.gif"), save_all=True,
               append_images=frames[1:], duration=70, loop=0)
print("WIN v1 -> final_g1v1_win.gif (state=%d, %d frame anim)" % (g.state, len(g.anim_frames)))

# --- FAIL run goal1 v1 (biarkan 1 kotak salah, SPACE -> bola jalan di atas build v1) ---
assert force(1, 1, "mech")
for i, s in enumerate(g.slots[:-1]):   # isi semua KECUALI terakhir
    g.cur_slot = i; g.cur_part = pal_idx(s["correct"]); g.key(pygame.K_RETURN)
g.key(pygame.K_SPACE)
frames = []
for _ in range(120):
    g.tick(); frames.append(snap())
frames[0].save(os.path.join(OUT, "final_g1v1_fail.gif"), save_all=True,
               append_images=frames[1:], duration=70, loop=0)
print("FAIL v1 -> final_g1v1_fail.gif (running=%s fail_slot=%s)" %
      (g.running, g.run_fail_slot))
pygame.quit()
