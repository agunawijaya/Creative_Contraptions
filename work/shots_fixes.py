import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
random.seed(3)
g = main.Game(assets.find_data_dir())
OUT = r"C:\Projects\Creative_Contraptions\work"


def snap():
    fb = cga.make_framebuffer(); g.draw(fb)
    return Image.frombytes("RGB", (640, 400),
                           pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))


# TITLE animasi -> GIF (bola keluar dari ayam, dst)
g.state = main.TITLE
frames = []
for t in range(0, 320, 2):
    g.title_tick = t
    frames.append(snap())
frames[0].save(os.path.join(OUT, "fix_title.gif"), save_all=True,
               append_images=frames[1:], duration=80, loop=0)
print("fix_title.gif frames=%d title_frames=%d" % (len(frames), len(g.title_frames)))

# FILL MECH play screen dgn strip palet penuh
g.start_play(1, fill="mech")
snap().save(os.path.join(OUT, "fix_fillmech_palette.png"))
print("fix_fillmech_palette.png (palet strip, %d opsi)" % len(g.palette))

# REVIEW screen (segitiga selector menghadap atas)
g.state = main.REVIEW; g.rev_i = 3
snap().save(os.path.join(OUT, "fix_review.png"))
print("fix_review.png (rev_i=3, pointer up)")
pygame.quit()
