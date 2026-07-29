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


# Review -> pilih Pendulum (rev_i=4) -> detail -> SPACE (demo)
g.state = main.REVIEW; g.rev_i = 4
g.key(pygame.K_RETURN)          # -> REVIEW_DETAIL
print("state REVIEW_DETAIL:", g.state == main.REVIEW_DETAIL, "rev_i=", g.rev_i)
print("pendulum frame seq (record idx):", g._mech_frames_seq(main.MECH_CATEGORIES[4][1][0]))
g.key(pygame.K_SPACE)           # -> demo ON
imgs = []
for _ in range(48):
    g.tick(); imgs.append(snap())
imgs[0].save(r"C:\Projects\Creative_Contraptions\work\proof_pendulum_demo.gif",
             save_all=True, append_images=imgs[1:], duration=140, loop=0)
print("rev_demo:", g.rev_demo, "-> proof_pendulum_demo.gif")
# frame kunci utk lihat sprite beda
for k in (0, 5, 10, 15):
    g.rev_demo_frame = k
    snap().save(r"C:\Projects\Creative_Contraptions\work\pend_%d.png" % k)
pygame.quit()
