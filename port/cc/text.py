"""Renderer teks untuk menu port.

CATATAN: ini font SEMENTARA (pygame SysFont monospace). Game asli memakai font
8x8 yang diperbesar-jadi-blok (FUN_1000_6453). Ekstraksi font asli = polish;
pengalamatannya tidak lurus (char*8 - 0x58b), perlu penelusuran tersendiri.
Struktur di sini dibuat agar mudah menukar ke font asli nanti.
"""
import pygame
from . import cga

_font_cache = {}


def _font(size):
    if size not in _font_cache:
        f = pygame.font.SysFont("consolas,couriernew,monospace", size, bold=True)
        _font_cache[size] = f
    return _font_cache[size]


def draw(fb, text, x, y, color=2, size=12, center_x=None):
    """Gambar teks ke framebuffer 320x200. color = index palet CGA."""
    surf = _font(size).render(text, False, cga.PALETTE[color])
    if center_x is not None:
        x = center_x - surf.get_width() // 2
    fb.blit(surf, (x, y))
    return surf.get_width()


def draw_center(fb, text, y, color=2, size=12):
    return draw(fb, text, 0, y, color, size, center_x=cga.WIDTH // 2)
