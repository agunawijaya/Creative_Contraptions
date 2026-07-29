import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()

# TITLE -> ENTER -> MENU
g.key(pygame.K_RETURN); assert g.state == main.MENU, g.state
# pilih Review (sel 0) -> ENTER -> GOAL
g.key(pygame.K_RETURN); assert g.state == main.GOAL, g.state
# pilih goal 1 (sel 0) -> ENTER -> CONTRAPTION (Review)
g.key(pygame.K_RETURN); assert g.state == main.CONTRAPTION, g.state
print("mode=", g.mode, "chosen_goal=", g.chosen_goal, "state=CONTRAPTION OK")
# SPACE -> PLAYANIM
g.key(pygame.K_SPACE); assert g.state == main.PLAYANIM, g.state
print("PLAYANIM: %d frame dimuat" % len(g.anim_frames))
# jalankan beberapa tick, render mid-frame
for _ in range(120):
    g.tick()
g.draw(fb)
print("anim_i setelah 120 tick =", g.anim_i)
big = pygame.transform.scale(fb, (640, 400))
pygame.image.save(big, r"C:\Projects\Creative_Contraptions\work\test_review_mid.png")
# lanjut ke akhir
for _ in range(500):
    g.tick()
print("anim_i akhir =", g.anim_i, "/", len(g.anim_frames))
g.draw(fb)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\test_review_end.png")
print("OK render tanpa error")
pygame.quit()
