"""Render keenam contraption via kode port -> satu montase (bukti port menangani semua)."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga, assets
from main import Game, GOAL_NAMES

pygame.init()
data = assets.find_data_dir()
g = Game(data)
fb = cga.make_framebuffer()

goals = [gid for gid in g.goal_ids if gid in GOAL_NAMES]  # 1..6
cols, rows = 2, 3
pad = 10
cw, ch = cga.WIDTH * 2, cga.HEIGHT * 2
font = pygame.font.SysFont("consolas", 22)
sheet = pygame.Surface((cols * (cw + pad) + pad, rows * (ch + 34) + pad))
sheet.fill((25, 25, 25))
for k, gid in enumerate(goals):
    g.render_goal(gid, fb)
    big = pygame.transform.scale(fb, (cw, ch))
    x = (k % cols) * (cw + pad) + pad
    y = (k // cols) * (ch + 34) + 28
    sheet.blit(big, (x, y))
    label = font.render("Goal %d: %s" % (gid, GOAL_NAMES[gid]), True, (255, 255, 0))
    sheet.blit(label, (x, y - 24))
out = os.path.join(os.path.dirname(__file__), "montage_goals.png")
pygame.image.save(sheet, out)
pygame.quit()
print("Tersimpan:", out)
