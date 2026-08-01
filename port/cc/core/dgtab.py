"""Akses tabel di DGROUP (segmen data game).

Beberapa hal yang dibutuhkan port TIDAK ada di berkas aset (GRAPH/MECHS/...)
melainkan di dalam segmen data program: glif font khusus, sprite bola beserta
mask-nya, tabel menu, dan string. Modul ini menyediakannya sebagai byte mentah,
diindeks dengan alamat DGROUP yang sama seperti yang dipakai kode aslinya.

SUMBERNYA, berurutan:
  1. `port/cc/data/DGROUP.bin`  -- bagian dari bundel aset milik pengguna,
     dibuat `python port/import_assets.py`. Ini jalur normal.
  2. `work/unpack/CONTRAP_UNPACKED.EXE` -- jalur PENGEMBANGAN saja.

⚠ Sama seperti berkas aset lain, DGROUP.bin TIDAK ikut repo: ia turunan langsung
dari program yang masih berhak cipta. Pengguna menyediakan salinannya sendiri.

Alamat yang sudah diketahui (semuanya dari src_c yang byte-exact):
  0x1F70  glif font khusus, karakter >= 0x80, 8 byte per glif
  0x1FB2  sprite bola, 4 fase x 24 byte (8 baris x 12 piksel)
  0x2012  mask bola, 4 fase x 24 byte
  0x2CC   tblA: 4 penunjuk ke fase sprite
  0x2D4   tblB: 4 penunjuk ke fase mask
  0x71A   seed RNG
"""
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

DG_PARA = 0x907                  # DGROUP mulai di paragraf ini pada citra
DG_LEN = 9556

FONT_HI = 0x1F70                 # glif karakter >= 0x80
TBL_SPRITE = 0x2CC               # 4 penunjuk
TBL_MASK = 0x2D4                 # 4 penunjuk
SEED = 0x71A

_cache = None


def _dari_exe(path):
    b = open(path, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    return b[lb + DG_PARA * 16: lb + DG_PARA * 16 + DG_LEN]


def dgroup():
    """Byte DGROUP (9.556 byte). Di-cache."""
    global _cache
    if _cache is not None:
        return _cache
    bundel = os.path.join(HERE, "..", "data", "DGROUP.bin")
    if os.path.exists(bundel):
        _cache = open(bundel, "rb").read()
    else:
        dev = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
        if not os.path.exists(dev):
            raise FileNotFoundError(
                "DGROUP tidak ditemukan.\n"
                "  Jalankan dulu:  python port/import_assets.py <folder_game>\n"
                "  (jalur pengembangan: work/unpack/CONTRAP_UNPACKED.EXE)")
        _cache = _dari_exe(dev)
    if len(_cache) < DG_LEN:
        raise ValueError("DGROUP terlalu pendek: %d byte" % len(_cache))
    return _cache


def word(addr):
    return struct.unpack_from("<H", dgroup(), addr)[0]


def blok(addr, n):
    return dgroup()[addr:addr + n]


def fase_bola():
    """-> ([4 x sprite 24B], [4 x mask 24B]), dibaca lewat tabel penunjuknya.

    Penunjuknya dibaca, BUKAN dihitung: alamatnya memang berurutan 24 byte di
    biner ini, tapi yang menentukan adalah isi tblA/tblB.
    """
    spr = [blok(word(TBL_SPRITE + 2 * i), 24) for i in range(4)]
    msk = [blok(word(TBL_MASK + 2 * i), 24) for i in range(4)]
    return spr, msk
