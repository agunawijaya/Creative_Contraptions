"""VERIFIKASI scaling (bukan klaim): native 320x200, scale integer nearest = tajam.
Bukti tajam: warna di hasil scale HARUS subset palet native (nol warna campuran)."""
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga, assets
from main import Game

pygame.init()
g = Game(assets.find_data_dir())
g.start_play(1)
fb = cga.make_framebuffer()
g.draw(fb)

print("1) Framebuffer native = %s  (harus 320x200): %s"
      % (fb.get_size(), fb.get_size() == (320, 200)))

pal = set(cga.PALETTE)
for s in (2, 3, 4, 6):
    scaled = cga.scale_native(fb, s)
    w, h = scaled.get_size()
    dims_ok = (w, h) == (320 * s, 200 * s)
    # cek warna hasil scale ada di palet native (sampling grid) -> nol campuran = tajam
    cols = set()
    for x in range(0, w, 7):
        for y in range(0, h, 7):
            cols.add(scaled.get_at((x, y))[:3])
    extra = cols - pal
    # cek satu blok: pixel sumber (10,10) -> blok s x s seragam
    src = fb.get_at((10, 10))[:3]
    block_uniform = all(scaled.get_at((10 * s + dx, 10 * s + dy))[:3] == src
                        for dx in range(s) for dy in range(s))
    print("2) scale %dx: dim=%s(%s)  warna_campuran_baru=%d(%s)  blok %dx%d seragam=%s"
          % (s, (w, h), "OK" if dims_ok else "SALAH", len(extra),
             "TAJAM" if not extra else "BLUR!", s, s, block_uniform))
pygame.quit()
