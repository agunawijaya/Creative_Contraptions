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
# ⚠ Alur pembuka gim: TITLE -> ENTER -> CREDITS -> ENTER -> SET UP
# (dua pertanyaan Y/N) -> MENU. Ini dari `main_.c`, bukan tambahan port.
g.key(pygame.K_RETURN)               # TITLE -> CREDITS
g.key(pygame.K_RETURN)               # CREDITS -> SET UP
g.key(pygame.K_y); g.key(pygame.K_y) # dua pertanyaan -> MENU
assert g.state == main.MENU, g.state
# ⚠ USANG lalu DIPERBAIKI: "Review Mechanisms" TIDAK lagi lewat pemilih goal.
# Sejak ensiklopedia mekanisme ada, sel 0 langsung ke REVIEW. Uji ini masih
# menegaskan alur LAMA dan gagal diam-diam. Lihat juga test_review2.py dan
# test_review_enc.py yang menguji jalur ensiklopedianya.
# Yang diuji di sini sekarang: demo "how it works" satu mekanisme.
g.key(pygame.K_RETURN); assert g.state == main.REVIEW, g.state
# ENTER -> detail satu mekanisme, lalu SPACE -> demo "how it works"
g.key(pygame.K_RETURN); assert g.state == main.REVIEW_DETAIL, g.state
g.key(pygame.K_SPACE); assert g.state == main.PLAYANIM, g.state
print("REVIEW -> REVIEW_DETAIL -> demo PLAYANIM OK")
print("mode=", g.mode, "rev_i=", g.rev_i)
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
