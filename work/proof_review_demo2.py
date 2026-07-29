import os, sys
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


# Review -> Pendulum (rev_i=4) -> ENTER (detail) -> SPACE (demo)
g.state = main.REVIEW; g.rev_i = 4
g.key(pygame.K_RETURN)
g.key(pygame.K_SPACE)
print("state==PLAYANIM:", g.state == main.PLAYANIM, "review_demo:", g.review_demo,
      "chosen_goal:", g.chosen_goal, "cur_variant:", g.cur_variant,
      "frames:", len(g.anim_frames))
imgs = []
for _ in range(len(g.anim_frames) + 10):
    g.tick(); imgs.append(snap())
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\proof_pendulum_demo2.gif",
             save_all=True, append_images=imgs[1:], duration=90, loop=0)
print("-> proof_pendulum_demo2.gif (%d frame)" % len(imgs))
# cek tiap mekanisme memuat goal7 varian yg benar
print("\ncek mapping mekanisme -> goal7 varian:")
for ri in range(9):
    g.state = main.REVIEW; g.rev_i = ri
    g.key(pygame.K_RETURN); g.key(pygame.K_SPACE)
    nm = main.MECH_CATEGORIES[ri][0]
    ok = g.chosen_goal == 7 and g.cur_variant == ri and len(g.anim_frames) > 0
    print("  rev_i=%d %-14s -> goal7 v%d frames=%d %s" %
          (ri, nm, g.cur_variant, len(g.anim_frames), "OK" if ok else "GAGAL"))
    g.review_demo = False
pygame.quit()
