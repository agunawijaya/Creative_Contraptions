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


def snap(name):
    fb = cga.make_framebuffer()
    g.draw(fb)
    big = pygame.transform.scale(fb, (640, 400))
    return Image.frombytes("RGB", (640, 400), pygame.image.tostring(big, "RGB"))


# --- TITLE animasi -> GIF ---
g.state = main.TITLE
frames = []
for t in range(64):
    g.title_tick = t
    frames.append(snap("t"))
frames[0].save(os.path.join(OUT, "final_title.gif"), save_all=True,
               append_images=frames[1:], duration=90, loop=0)
print("-> final_title.gif")


def force_variant(gid, vi, fill="mech"):
    for _ in range(200):
        g.start_play(gid, fill=fill)
        if g.cur_variant == vi:
            return True
    return False


# --- Fill in Mechanisms: varian berbeda utk goal yg sama ---
imgs = []
for gid in (1, 3, 4, 6):
    for vi in range(len(g.draws_var.get(gid, {}))):
        if force_variant(gid, vi, "mech"):
            im = snap("m")
            im.save(os.path.join(OUT, "final_g%d_v%d.png" % (gid, vi)))
            imgs.append((gid, vi, im))
            print("-> final_g%d_v%d.png" % (gid, vi))

# montase goal 1 v0 vs v1 berdampingan
g1 = [im for (gid, vi, im) in imgs if gid == 1]
if len(g1) >= 2:
    m = Image.new("RGB", (640, 800))
    m.paste(g1[0], (0, 0)); m.paste(g1[1], (0, 400))
    m.save(os.path.join(OUT, "final_g1_variants.png"))
    print("-> final_g1_variants.png (v0 atas, v1 bawah)")
pygame.quit()
