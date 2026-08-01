"""Font teks — persis seperti `text.asm` @0x644A.

Aturan pemilihan glif, dibaca langsung dari assembly yang sudah byte-exact:

    AX = c * 8
    if AX < 0x400:                 (yaitu c < 0x80)
        SI = AX + 0xFA75 ; DS = 0xF000     -> font ROM BIOS IBM PC 8x8
    else:
        SI = (AX - 0x400) + 0x1F70 + 7     -> font khusus di DGROUP
    lalu: CX = 8 ; STD ; LODSB x8          -> 8 byte dibaca MUNDUR dari SI

Dua hal yang penting dan mudah terlewat:

1. Karakter < 0x80 TIDAK ada di dalam game. Mereka datang dari ROM BIOS mesin,
   di F000:FA6E. Itu sebabnya emulator kita dulu tidak pernah merender teks:
   wilayah F000 tidak diisi apa pun, jadi semua glif terbaca nol.

2. Glif khusus (c >= 0x80) ada di DGROUP 0x1F70. Yang berisi cuma empat:
       0x80  panah kiri      0x83  panah kanan
       0x81  potongan bar kiri   0x82  potongan bar kanan
   Itulah tanda `< >` yang mengapit nama part di layar pilihan.
   Sisanya (0x84..0x87) kosong atau sampah -- ruangnya memang cuma sampai
   0x1FB2, tempat sprite bola mulai.

⚠ Pembacaan MUNDUR (STD, mulai dari base+7) hanya menentukan urutan byte masuk
  ke penggambar, bukan bentuk glifnya. Byte 0..7 tetap baris 0..7 dari atas;
  sudah diperiksa dengan merender 'A' dan membandingkan bentuknya.
"""
import os

from . import dgtab

HERE = os.path.dirname(os.path.abspath(__file__))
ROM = os.path.join(HERE, "rom8x8.bin")

FONT_HI = dgtab.FONT_HI

_rom = None


def rom():
    global _rom
    if _rom is None:
        _rom = open(ROM, "rb").read()
        if len(_rom) < 2048:
            raise ValueError("rom8x8.bin harus 2048 byte, dapat %d" % len(_rom))
    return _rom


def glif(c):
    """8 byte glif untuk satu karakter. Baris 0 = paling atas."""
    c &= 0xFF
    if c < 0x80:
        return rom()[c * 8: c * 8 + 8]
    return dgtab.blok(FONT_HI + (c - 0x80) * 8, 8)


def baris_piksel(c):
    """Glif -> 8 baris x 8 bool (True = piksel menyala)."""
    return [[(b >> (7 - i)) & 1 == 1 for i in range(8)] for b in glif(c)]


def gambar(fb, teks, x, y, warna=3, w=320, h=200, skx=1, sky=1):
    """Tulis `teks` ke framebuffer indeks-warna pada (x, y). Kembalikan lebar.

    Piksel yang MATI tidak ditulis -- penggambar aslinya hanya menyalakan piksel
    yang menyala, jadi teks tidak menghapus latar di belakangnya.

    `skx`/`sky` = faktor perbesaran, yaitu argumen `w`/`h` pada `text()` di
    biner. Label huruf memakai (1, 1); judul "CREATIVE CONTRAPTIONS" yang
    digambar skrip animasi memakai (2, 2).
    """
    cx = x
    for ch in teks:
        g = baris_piksel(ord(ch))
        for r in range(8):
            for ry in range(sky):
                ty = y + r * sky + ry
                if not (0 <= ty < h):
                    continue
                for k in range(8):
                    if not g[r][k]:
                        continue
                    for rx in range(skx):
                        tx = cx + k * skx + rx
                        if 0 <= tx < w:
                            fb[ty][tx] = warna
        cx += 8 * skx
    return cx - x


def lebar(teks):
    return 8 * len(teks)
