"""Font teks 8x8 milik ROM BIOS — dipakai HANYA untuk pesan bergaya `printf`.

Kenapa ada dua font di port ini
-------------------------------
Gim menulis teks lewat DUA jalur yang sama sekali berbeda, dan keduanya
memakai font yang berbeda pula:

    text() @0x6453   font GIM (tabel di DGROUP)  -> menu, nama goal, prompts()
    printf() @0x6a48 font ROM BIOS lewat DOS     -> pesan dalam permainan

Terukur: `printf` mengeluarkan teksnya lewat `INT 21h AH=02h`, satu panggilan
per karakter (36 panggilan untuk 36 karakter), jadi yang menggambar adalah
driver konsol DOS + BIOS — bukan gim. Warnanya pun ditentukan di sana: 3.

Font ROM bukan bagian dari gim, jadi repo TIDAK mendistribusikannya. Ia
diekstrak sekali oleh `python port/import_romfont.py` ke `port/cc/data/`
(di-.gitignore), persis seperti aset gim lewat `import_assets.py`.

Kalau bundelnya belum ada, `tersedia()` mengembalikan False dan pemanggil
jatuh ke font gim. Itu terlihat sedikit berbeda, dan memang begitu adanya —
lebih baik daripada diam-diam mengaku setia.
"""
import os

AWAL, AKHIR = 32, 126
_JALUR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                      "romfont.bin")
_FONT = [None]


def _muat():
    if _FONT[0] is None:
        try:
            d = open(_JALUR, "rb").read()
            _FONT[0] = d if len(d) == (AKHIR - AWAL + 1) * 8 else b""
        except OSError:
            _FONT[0] = b""
    return _FONT[0]


def tersedia():
    return bool(_muat())


def glyph(ch):
    """-> 8 byte bitmap (bit 0x80 = piksel paling kiri), atau None."""
    d = _muat()
    c = ord(ch)
    if not d or not (AWAL <= c <= AKHIR):
        return None
    i = (c - AWAL) * 8
    return d[i:i + 8]


def gambar(k, teks, x, y, warna):
    """Gambar `teks` dgn font ROM di (x, y). -> True kalau fontnya ada.

    Menggambar HANYA piksel yang menyala, seperti teletype BIOS di mode grafis:
    latar sel tidak disentuh.
    """
    if not tersedia():
        return False
    for i, ch in enumerate(teks):
        g = glyph(ch)
        if g is None:
            continue
        for row, b in enumerate(g):
            if not b:
                continue
            for col in range(8):
                if b & (0x80 >> col):
                    k.piksel(x + i * 8 + col, y + row, warna)
    return True
