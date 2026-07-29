import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
# masuk Fill, isi semua benar
g.key(pygame.K_RETURN); g.key(pygame.K_DOWN); g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)
tp = {t: i for i, (t, _) in enumerate(main.MECH_TYPES)}
for i, s in enumerate(g.slots):
    g.cur_slot = i; g.cur_part = tp[s["correct"]]; g.key(pygame.K_RETURN)
print("all correct:", all(s["filled"] == s["correct"] for s in g.slots))
g.key(pygame.K_SPACE)
print("state after SPACE:", g.state, "PLAYANIM=", main.PLAYANIM, "frames=", len(g.anim_frames))
fb = cga.make_framebuffer()
# render beberapa frame fase fisika, tumpuk
idxs = [i for i in [50, 80, 110, 140, 170] if i < len(g.anim_frames)]
sheet = Image.new("RGB", (640, 400 * len(idxs)))
for k, fi in enumerate(idxs):
    g.anim_i = fi
    g.draw(fb)
    im = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
    sheet.paste(im, (0, k * 400))
sheet.save(r"C:\Projects\Creative_Contraptions\work\inspect_fillrun.png")
print("saved frames", idxs)
pygame.quit()
