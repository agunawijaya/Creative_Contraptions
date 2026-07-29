import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()

def snap(g):
    fb = cga.make_framebuffer(); g.draw(fb)
    return Image.frombytes("RGB", (640, 400), pygame.image.tostring(
        pygame.transform.scale(fb, (640, 400)), "RGB"))

def fresh():
    return main.Game(assets.find_data_dir())

shots = []
# 0 Review Mechanisms
g = fresh(); g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)
assert g.state == main.REVIEW; shots.append(("0 Review Mechanisms", snap(g)))
# 1 Fill in Mechanisms
g = fresh(); g.key(pygame.K_RETURN); g.key(pygame.K_DOWN); g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)
assert g.state == main.PLAY and g.fill_mode == "mech"; shots.append(("1 Fill in Mechanisms", snap(g)))
# 2 Fill in Zany Objects
g = fresh(); g.key(pygame.K_RETURN)
for _ in range(2): g.key(pygame.K_DOWN)
g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)
assert g.state == main.PLAY and g.fill_mode == "zany"; shots.append(("2 Fill in Zany Objects", snap(g)))
# 3 Mix Up
g = fresh(); g.key(pygame.K_RETURN)
for _ in range(3): g.key(pygame.K_DOWN)
g.key(pygame.K_RETURN); g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)
assert g.state == main.PLAY and g.fill_mode == "both"; shots.append(("3 Contraption Mix Up", snap(g)))

sheet = Image.new("RGB", (640, 400 * len(shots)), (0, 0, 0))
for k, (name, im) in enumerate(shots):
    sheet.paste(im, (0, k * 400)); print("OK:", name)
sheet.save(r"C:\Projects\Creative_Contraptions\work\all_modes.png")
print("-> all_modes.png")
pygame.quit()
