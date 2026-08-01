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


def setupscr(fb, mode, nbola=1, misc=None, sub=0, schi_sclo=0):
    """`setupscr()` @0x33xx — SELURUH latar layar, ditulis apa adanya:

        fillrect(0, 0, 0x13f, 7, 3);          pita atas, abu-abu
        fillrect(0, 8, 0x13f, 0x9f, 1);       arena, cyan
        col = (mode == 0 || mode == 1) ? 1 : 0;
        if (mode == 4 && (schi|sclo) != 0)  fillrect(0, 0xa8, 0x13f, 199, 0);
        else                                fillrect(0, 0xa0, 0x13f, 199, col);
        blit(hdrspr, 0, 0x88, 8, 0x30);
        for (i = 0; i < goal; i++) setball(0, i * 10);
        if (sub == 1 && mode != 0 && mode != 1)
            fillrect(0x10, 0xc0, 0x12f, 199, 1);

    ⭐ `hdrspr` @0x526 adalah BUFFER, bukan data statis: isinya nol di DGROUP dan
    diisi saat program berjalan dari MISC record 2. Jadi corong yang dulu kita
    identifikasi lewat tangkapan VRAM memang benar -- sekarang dengan sebabnya.

    Ikon bola di pita atas dipasang `setball(0, i*10)`, dan justru panggilan itu
    yang membongkar penamaan yang menyesatkan: ikonnya berjajar MENDATAR padahal
    yang bertambah adalah argumen kedua, yang disimpan ke global bernama `bally`.
    Jadi @0x25e memegang X dan @0x260 memegang Y -- lihat catatan di dgtab.py.

    ⚠ `nbola` menggantikan global yang di sumbernya bernama `goal` (@0x718).
    Namanya menyesatkan: itu BUKAN nomor kontraption melainkan JUMLAH BOLA yang
    tersisa -- `goal = 1` sebelum layar design, `goal = 6` di mode Contraption
    Mix Up, dan `goal++` di animvm ketika pemain mendapat bola tambahan. Layar
    design selalu menampilkan satu ikon, berapa pun nomor goal-nya; sempat
    terukur sebagai beda 50 piksel per nomor goal sebelum ini disadari.
    """
    fillrect(fb, 0, 0, 0x13F, 7, 3)
    fillrect(fb, 0, 8, 0x13F, 0x9F, 1)
    col = 1 if mode in (0, 1) else 0
    if mode == 4 and schi_sclo != 0:
        fillrect(fb, 0, 0xA8, 0x13F, 199, 0)
    else:
        fillrect(fb, 0, 0xA0, 0x13F, 199, col)
    if misc is not None:
        r = misc.recs[contrap.CORONG_REC]
        blit(fb, misc, r, contrap.CORONG_XY[0], contrap.CORONG_XY[1])
    for i in range(nbola):
        bola(fb, i * 10, 0)
    if sub == 1 and mode not in (0, 1):
        fillrect(fb, 0x10, 0xC0, 0x12F, 199, 1)
    return fb


def bola(fb, x, y):
    """Gambar bola di (x, y) LAYAR. Fase pra-geser `x % 4`, kolom byte `x // 4`.

    ⭐ TIDAK ADA transform logis->layar. Selama berbulan-bulan dicatat bahwa
    "`FUN_1000_5e3b` menerapkan transform per-part + sub-pixel, jadi posisi layar
    harus dibaca dari VRAM". Itu keliru, dan sebabnya nama global yang tertukar:
    begitu diketahui @0x25e memegang X dan @0x260 memegang Y, keduanya ternyata
    koordinat LAYAR langsung. `xform()` hanya memilih fase dan memanggil
    penggambarnya -- tidak ada transform di dalamnya.

    Diukur, bukan disimpulkan: pada frame rujukan f0008 goal 1, VRAM berbeda 52
    piksel dari frame sebelumnya; menggambar bola di (x=51, y=24) -- persis isi
    @0x25e dan @0x260 saat itu -- membuat bedanya NOL.

    Sprite dan mask dibaca lewat tabel penunjuk di DGROUP (tblA/tblB), bukan
    dihitung -- lihat dgtab.fase_bola(). Bola di pita atas memakai fungsi yang
    SAMA; ia memang bola biasa di (i*10, 0), bukan ikon tersendiri.
    """
    from . import dgtab
    spr, msk = dgtab.fase_bola()
    fase = x & 3
    x0 = (x >> 2) * 4
    s, m = spr[fase], msk[fase]
    for row in range(8):
        ty = y + row
        if not (0 <= ty < H):
            continue
        for cb in range(3):                       # 3 byte = 12 piksel
            sb, mb = s[row * 3 + cb], m[row * 3 + cb]
            for p in range(4):
                tx = x0 + cb * 4 + p
                if not (0 <= tx < W):
                    continue
                geser = 6 - 2 * p
                if (mb >> geser) & 3 == 0:        # mask 0 = piksel bola
                    fb[ty][tx] = (sb >> geser) & 3


def labels(fb, pos, warna=3):
    """`f15d0()`: huruf 'A'+i di tiap entri postab, warna 3.

        for (i = 0; i < cnt; i++) { s = i + 'A';
            text(&s, tab[i*2+1], tab[i*2], 1, 1, 3); }

    ⚠ `text()` memakai urutan (X, Y) -- KEBALIKAN `blit()` yang (Y, X). Dengan
    struct pos {int a; int b;}, panggilan `text(&s, b, a)` berarti X = b dan
    Y = a, jadi entri (45, 0) menaruh huruf 'A' di (x=0, y=45). Diperiksa
    terhadap ketujuh label yang terlihat di tangkapan VRAM, bukan diterka.
    """
    from . import font
    for i, (a, b) in enumerate(pos):
        font.gambar(fb, chr(ord("A") + i), b, a, warna, W, H)
    return fb


SLOT_W, SLOT_H = 0x1E, 0x17      # kotak slot: 30 lebar, 23 tinggi (dari x+1)


def drawslot(k, slots, isi=None, arsip=None):
    """`drawslot()` @0x3F0F — isi tiap slot kontraption.

    ⭐ Slot KOSONG bukan kotak bergaris dengan huruf di tengahnya, melainkan
    PETAK PENUH warna 3:

        fillrect(x + 1, y, x + 0x1e, y + 0x17, 3);

    Slot yang sudah terisi digambar sprite-nya, 0x18 x 0x20 di (y, x).

    Terukur vs tangkapan VRAM (goal 1 mode isian, ketiga slot mekanisme):
    2.160/2.160 piksel. Port lama menggambar kotak bergaris + huruf di dalam
    kotak, dan itu karangan sendiri.

    `slots` = daftar (y, x); `isi(i)` -> (arsip, record) untuk slot yang sudah
    terisi, atau None kalau masih kosong.
    """
    for i, (y, x) in enumerate(slots):
        pasangan = isi(i) if isi is not None else None
        if pasangan is None:
            k.fillrect(x + 1, y, x + SLOT_W, y + SLOT_H, 3)
            continue
        arc, rec = pasangan
        k.blit(arc, rec, x, y)


def drawbox(k, y, x):
    """`drawbox()` @0x3886 — kotak sorotan, EMPAT garis warna 3, digambar XOR.

        ybot = y + 0x17;  xlf = x + 1;  xrt = x + 0x1e;
        line(xlf,   y,      x + 0x1d, y,      3);
        line(xrt,   y,      xrt,      y+0x16, 3);
        line(x + 2, ybot,   xrt,      ybot,   3);
        line(xlf,   y + 1,  xlf,      ybot,   3);

    Perhatikan ujung-ujungnya tidak simetris (x+0x1d di atas, x+2 di bawah):
    itu memang begitu di biner, bukan salah salin.
    """
    ybot = y + 0x17
    xlf = x + 1
    xrt = x + 0x1E
    k.xor(xlf, y, x + 0x1D, y, 3)
    k.xor(xrt, y, xrt, y + 0x16, 3)
    k.xor(x + 2, ybot, xrt, ybot, 3)
    k.xor(xlf, y + 1, xlf, ybot, 3)


# ---- keluaran -----------------------------------------------------------
def to_rgb(fb):
    """Daftar tuple RGB, urut baris — untuk PIL."""
    return [PALETTE[c] for row in fb for c in row]


def simpan_png(fb, path):
    from PIL import Image
    im = Image.new("RGB", (W, H))
    im.putdata(to_rgb(fb))
    im.save(path)


def sprite_surface(arc, rec, pygame=None):
    """Satu record arsip -> pygame.Surface seukuran sprite-nya.

    Latarnya diisi warna latar game lebih dulu, karena `blit()` menulis SEMUA
    piksel termasuk yang berwarna latar -- tidak ada colorkey di sini.
    """
    fb = [[BG] * rec["w"] for _ in range(rec["h"])]
    for yy, baris in enumerate(arc.pixels(rec)):
        for xx, c in enumerate(baris):
            if xx < rec["w"]:
                fb[yy][xx] = c
    return to_surface(fb, pygame)


def to_surface(fb, pygame=None):
    """Framebuffer indeks -> pygame.Surface. Impor pygame ditunda supaya modul
    ini tetap bisa dipakai alat baris-perintah tanpa pygame terpasang."""
    if pygame is None:
        import pygame as pygame
    h = len(fb)
    w = len(fb[0]) if h else 0
    surf = pygame.Surface((w, h))
    buf = pygame.PixelArray(surf)
    for y in range(h):
        row = fb[y]
        for x in range(w):
            buf[x, y] = surf.map_rgb(PALETTE[row[x]])
    del buf
    return surf


# ---- kanvas: satu antarmuka, dua sasaran --------------------------------
class KanvasFB:
    """Kanvas di atas framebuffer indeks-warna."""

    def __init__(self, fb):
        self.fb = fb

    def fillrect(self, x0, y0, x1, y1, c):
        fillrect(self.fb, x0, y0, x1, y1, c)

    def teks(self, s, x, y, c, skx=1, sky=1):
        from . import font
        font.gambar(self.fb, s, x, y, c, W, H, skx, sky)

    def blit(self, arc, rec, x, y):
        blit(self.fb, arc, rec, x, y)

    def xor(self, x0, y0, x1, y1, c):
        for yy in range(max(0, y0), min(y1 + 1, H)):
            baris = self.fb[yy]
            for xx in range(max(0, x0), min(x1 + 1, W)):
                baris[xx] ^= c


class KanvasSurface:
    """Kanvas di atas pygame.Surface, untuk menggambar LANGSUNG ke layar.

    Ada supaya `hud.py` tidak perlu dua versi: aturan penempatan dan
    percabangannya ditulis SEKALI, sasarannya yang berganti. Glifnya tetap
    dari `font.baris_piksel()`, jadi bentuk hurufnya juga satu sumber.
    """

    def __init__(self, surf, pygame):
        self.surf = surf
        self.pygame = pygame

    def _w(self, c):
        return PALETTE[c]

    def fillrect(self, x0, y0, x1, y1, c):
        self.surf.fill(self._w(c), (x0, y0, x1 - x0 + 1, y1 - y0 + 1))

    def teks(self, s, x, y, c, skx=1, sky=1):
        from . import font
        warna = self._w(c)
        cx = x
        for ch in s:
            g = font.baris_piksel(ord(ch))
            for r in range(8):
                for ry in range(sky):
                    ty = y + r * sky + ry
                    if not (0 <= ty < H):
                        continue
                    for k in range(8):
                        if not g[r][k]:
                            continue
                        for rx in range(skx):
                            tx = cx + k * skx + rx
                            if 0 <= tx < W:
                                self.surf.set_at((tx, ty), warna)
            cx += 8 * skx

    def blit(self, arc, rec, x, y):
        self.surf.blit(sprite_surface(arc, rec, self.pygame), (x, y))

    def xor(self, x0, y0, x1, y1, c):
        buf = self.pygame.PixelArray(self.surf)
        for yy in range(max(0, y0), min(y1 + 1, H)):
            for xx in range(max(0, x0), min(x1 + 1, W)):
                lama = self.surf.unmap_rgb(buf[xx, yy])[:3]
                idx = PALETTE.index(lama) if lama in PALETTE else 0
                buf[xx, yy] = self.surf.map_rgb(PALETTE[idx ^ c])
        del buf
