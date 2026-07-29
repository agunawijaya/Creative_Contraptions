import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())


def snap():
    fb = cga.make_framebuffer(); g.draw(fb)
    return Image.frombytes("RGB", (640, 400),
                           pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))


def pal_idx(idm):
    for i, p in enumerate(g.palette):
        if idm in p[1]:
            return i
    return None


# uji SEMUA goal/varian: ikon palet == sprite yg ditempatkan (idx sama)?
bad = 0
for gid in g.goal_ids:
    for vi in range(len(g.draws_var.get(gid, {}))):
        for _ in range(400):
            g.start_play(gid, fill="mech")
            if g.cur_variant == vi:
                break
        for i, s in enumerate(g.slots):
            pi = pal_idx(s["correct"])
            pal_sprite = g.palette[pi][3]
            g.cur_slot = i; g.cur_part = pi; g._place()
            placed_sprite = s["sprite"]
            if pal_sprite != placed_sprite:
                print("  MISMATCH goal%d v%d slot%d: palet=%d placed=%d" %
                      (gid, vi, i, pal_sprite, placed_sprite))
                bad += 1
print("mismatch palet-vs-placed:", bad)

# bukti visual goal 3: isi Inclined Plane, tampilkan palet (terpilih) + hasil tempat
for _ in range(200):
    g.start_play(3, fill="mech")
    if g.cur_variant == 0:
        break
ip = pal_idx(100) if pal_idx(100) is not None else pal_idx(101)
g.cur_part = ip
# pilih slot inclined plane
for i, s in enumerate(g.slots):
    if g._cat_index(s["correct"]) == 0:   # Inclined Plane
        g.cur_slot = i; break
before = snap()          # palet Inclined Plane terpilih, slot masih kosong
g._place()
after = snap()           # slot terisi -> harus sama dgn ikon palet
m = Image.new("RGB", (640, 800)); m.paste(before, (0, 0)); m.paste(after, (0, 400))
m.save(r"C:\Projects\Creative_Contraptions\work\proof_g3_palette.png")
print("-> proof_g3_palette.png (atas: palet Inclined Plane terpilih; bawah: setelah ditaruh)")
pygame.quit()
