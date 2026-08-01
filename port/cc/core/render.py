"""Penggambar — framebuffer INDEKS WARNA 320x200, bukan Surface.

Kenapa indeks dan bukan langsung pygame: supaya keluaran port bisa dibandingkan
piksel-per-piksel dengan alat bukti (`work/genscreens.py`) dan dengan tangkapan
VRAM emulator tanpa perantara. Konversi ke Surface dilakukan SEKALI per frame,
di ujung.

Primitifnya meniru yang ada di biner:

    blit()     @0x672F  menulis SEMUA piksel, termasuk yang berwarna latar.
                        Cyan adalah warna latar game, BUKAN penanda transparan --
                        memakai colorkey akan melubangi bagian dalam sprite yang
                        memang berwarna cyan.
    fillrect() @0x6869  fillrect(x0, y0, x1, y1, warna), batas INKLUSIF.
"""
W, H = 320, 200
PALETTE = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
BG = 1                                   # cyan = latar game

from . import contrap                                          # noqa: E402


def new_fb(warna=BG):
    return [[warna] * W for _ in range(H)]


def fillrect(fb, x0, y0, x1, y1, c):
    """Batas INKLUSIF di kedua ujung, seperti fillrect() @0x6869."""
    for y in range(max(0, y0), min(y1 + 1, H)):
        row = fb[y]
        for x in range(max(0, x0), min(x1 + 1, W)):
            row[x] = c


def blit(fb, arc, rec, x, y):
    """OPAQUE: setiap piksel sprite ditulis, termasuk yang berwarna latar."""
    for yy, line in enumerate(arc.pixels(rec)):
        ty = y + yy
        if not (0 <= ty < H):
            continue
        row = fb[ty]
        for xx, c in enumerate(line):
            tx = x + xx
            if 0 <= tx < W:
                row[tx] = c


def apply(fb, dl):
    """Terapkan daftar gambar dari contrap.draw_list()."""
    for d in dl:
        if d["kind"] == "slot":
            # drawslot.c cabang slot KOSONG: fillrect(x+1, y, x+0x1e, y+0x17, 3)
            fillrect(fb, d["x"] + 1, d["y"],
                     d["x"] + contrap.SLOT_W, d["y"] + contrap.SLOT_H,
                     contrap.SLOT_WARNA)
        else:
            blit(fb, d["arc"], d["rec"], d["x"], d["y"])
    return fb


def baris_status(fb):
    """redraw() @0x5936: fillrect(0x10, 0xc0, 0x12f, 0xc7, 1)."""
    fillrect(fb, 0x10, 0xC0, 0x12F, 0xC7, 1)


# ---- keluaran -----------------------------------------------------------
def to_rgb(fb):
    """Daftar tuple RGB, urut baris — untuk PIL."""
    return [PALETTE[c] for row in fb for c in row]


def simpan_png(fb, path):
    from PIL import Image
    im = Image.new("RGB", (W, H))
    im.putdata(to_rgb(fb))
    im.save(path)


def to_surface(fb, pygame=None):
    """Framebuffer indeks -> pygame.Surface. Impor pygame ditunda supaya modul
    ini tetap bisa dipakai alat baris-perintah tanpa pygame terpasang."""
    if pygame is None:
        import pygame as pygame
    surf = pygame.Surface((W, H))
    buf = pygame.PixelArray(surf)
    for y in range(H):
        row = fb[y]
        for x in range(W):
            buf[x, y] = surf.map_rgb(PALETTE[row[x]])
    del buf
    return surf
