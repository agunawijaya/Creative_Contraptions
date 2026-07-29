"""Model layar CGA 320x200 4-warna untuk port Creative Contraptions.

Prinsip (metode sama dgn DOSBox):
- 320x200, 2 bit/pixel, palet CGA-1 LOW intensity (bg biru; disampel dari game asli).
- SEMUA render ke framebuffer 320x200 native (sumber kebenaran) — resolusi asli.
- Hanya TAMPILAN FINAL yang di-scale: integer nearest-neighbor (tajam), seperti
  DOSBox 'Scaler normal Nx'. Logika game tak pernah menyentuh piksel yang sudah di-scale.
"""
import pygame

WIDTH, HEIGHT = 320, 200

# Palet ASLI game (disampel dari screenshot): CGA palette 1 LOW intensity,
# dengan register background (warna 0) di-set BIRU. Terverifikasi eksak.
#   0 = biru (0,0,170)   1 = cyan (0,170,170)
#   2 = magenta (170,0,170)   3 = abu/putih (170,170,170)
PALETTE = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
BG_INDEX = 1  # cyan = latar game (warna dominan)


def make_framebuffer():
    """Surface 320x200 tempat semua digambar."""
    fb = pygame.Surface((WIDTH, HEIGHT))
    fb.fill(PALETTE[BG_INDEX])
    return fb


def best_integer_scale(avail_w, avail_h, aspect_43=False):
    """Skala integer terbesar yang muat. aspect_43: pixel non-persegi 1:1.2."""
    vh = 240 if aspect_43 else HEIGHT
    s = min(avail_w // WIDTH, avail_h // vh)
    return max(1, s)


def scale_native(fb, s, aspect_43=False):
    """Kembalikan Surface hasil scale integer nearest-neighbor (metode DOSBox normal Nx).
    aspect_43: koreksi pixel non-persegi CGA (tinggi x1.2) untuk tampilan ala CRT 4:3."""
    dst_w = WIDTH * s
    dst_h = (240 if aspect_43 else HEIGHT) * s
    return pygame.transform.scale(fb, (dst_w, dst_h))   # transform.scale = nearest, tajam


def present(screen, fb, scale=None, aspect_43=False):
    """Tampilkan framebuffer native ke layar. scale=None -> integer terbesar yg muat."""
    sw, sh = screen.get_size()
    s = scale if scale else best_integer_scale(sw, sh, aspect_43)
    scaled = scale_native(fb, s, aspect_43)
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((sw - scaled.get_width()) // 2, (sh - scaled.get_height()) // 2))
    pygame.display.flip()


def set_dpi_aware():
    """Windows: hindari blur akibat DPI scaling OS."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
