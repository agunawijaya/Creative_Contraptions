import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main
pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN)              # TITLE->MENU
g.key(pygame.K_RETURN)              # Review (sel 0) -> REVIEW browse
assert g.state == main.REVIEW, g.state
g.draw(fb)
browse = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
# ENTER -> detail (mech 0 Inclined Plane)
g.key(pygame.K_RETURN)
assert g.state == main.REVIEW_DETAIL, g.state
g.draw(fb)
det0 = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
# back, cycle to Pendulum (idx 4), detail
g.key(pygame.K_RETURN)             # back to browse
for _ in range(4): g.key(pygame.K_RIGHT)
g.key(pygame.K_RETURN)             # detail mech 4
g.draw(fb)
det4 = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
sheet = Image.new("RGB", (640, 1200))
sheet.paste(browse, (0, 0)); sheet.paste(det0, (0, 400)); sheet.paste(det4, (0, 800))
sheet.save(r"C:\Projects\Creative_Contraptions\work\review2.png")
print("OK: browse + detail(InclinedPlane) + detail(Pendulum) rendered")
pygame.quit()
