"""Pemuat aset Creative Contraptions — baca file ASLI apa adanya saat runtime.

Format (hasil reverse-engineering, lihat CODE_MAP.md / ARCHITECTURE.md):
- Arsip 12-byte record: {u8 id_major, u8 id_minor, u8 h, u8 w, u16 flags, u16 len, u32 off}
  blob = RLE dgn escape 0xE4 <count> <value>, pixel CGA 2bpp row-major.
- CONTRAP: directory 36 x {u16 id, u32 off}; per contraption:
  goal_id, countA, u32[A], countB, rec6[B]=mekanisme{y,x,tipe}, countC, rec6[C]=zany, arrD.
"""
import os
import struct
import pygame
from . import cga


def decode_rle(data):
    """RLE: 0xE4 <count> <value> -> value*count; selain itu literal."""
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1])
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def _sprite_surface(dec, w, h):
    """Pixel CGA 2bpp -> Surface OPAQUE (spt blitter asli FUN_1000_672f yg menulis SEMUA
    piksel, termasuk cyan). Latar game juga cyan, jadi area 'kosong' sprite (cyan) menyatu
    dgn latar; saat sprite bertumpuk, yg belakangan MENIMPA (persis game). Tanpa colorkey
    supaya warna cyan di dalam sprite TIDAK hilang saat digambar di atas kotak/sprite lain."""
    surf = pygame.Surface((w, h))
    surf.fill(cga.PALETTE[cga.BG_INDEX])
    wb = w // 4
    for r in range(h):
        base = r * wb
        for cb in range(wb):
            if base + cb >= len(dec):
                break
            byte = dec[base + cb]
            for p in range(4):
                idx = (byte >> (6 - 2 * p)) & 3
                surf.set_at((cb * 4 + p, r), cga.PALETTE[idx])
    return surf


class Archive:
    """Arsip 12-byte record (GRAPH/MECHS/MISC). Sprite di-cache per (id_major,id_minor,seq)."""

    def __init__(self, path):
        b = open(path, "rb").read()
        self.raw = b
        first = struct.unpack_from("<I", b, 8)[0]
        n = first // 12
        self.records = []          # list of dict
        self.by_major = {}         # id_major -> list index
        for i in range(n):
            a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
            if w == 0 or h == 0 or ln == 0:
                continue
            rec = dict(idx=i, major=a, minor=mi, h=h, w=w, flags=f, off=off, ln=ln)
            self.records.append(rec)
            self.by_major.setdefault(a, []).append(len(self.records) - 1)
        self._cache = {}

    def sprite(self, rec):
        key = rec["idx"]
        if key not in self._cache:
            dec = decode_rle(self.raw[rec["off"]:rec["off"] + rec["ln"]])
            need = (rec["w"] // 4) * rec["h"]
            if len(dec) < need:
                dec = dec + bytes(need - len(dec))
            self._cache[key] = _sprite_surface(dec, rec["w"], rec["h"])
        return self._cache[key]

    def first_of_major(self, major):
        idxs = self.by_major.get(major)
        return self.records[idxs[0]] if idxs else None

    def sprite_by_idx(self, idx):
        """Sprite dari indeks record absolut (dipakai tabel sprite terverifikasi)."""
        if 0 <= idx < len(self.records):
            return self.sprite(self.records[idx])
        return None


def parse_contrap(path):
    """Kembalikan dict goal_id -> list of variant dict{mech:[(y,x,tipe)], zany:[(y,x,tipe)]}."""
    b = open(path, "rb").read()
    dirn = struct.unpack_from("<I", b, 2)[0] // 6
    entries = [struct.unpack_from("<HI", b, i * 6) for i in range(dirn)]
    goals = {}
    for gid, off in entries:
        if gid == 0 or gid >= 128:
            continue
        p = off
        goal_id = struct.unpack_from("<H", b, p)[0]; p += 2
        cA = struct.unpack_from("<H", b, p)[0]; p += 2 + cA * 4
        cB = struct.unpack_from("<H", b, p)[0]; p += 2
        # posisi (y,x) SIGNED (sprite bisa sedikit keluar tepi kiri/atas), type unsigned
        mech = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cB)]; p += cB * 6
        cC = struct.unpack_from("<H", b, p)[0]; p += 2
        zany = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cC)]
        goals.setdefault(goal_id, []).append(dict(mech=mech, zany=zany))
    return goals


_NEEDED = ("GRAPH", "MECHS", "ANIMATE", "CONTRAP")


def find_data_dir():
    """Folder aset yang dipakai port.

    URUTAN SENGAJA: bundel milik port (`cc/data/`) DULU, baru folder game asli.
    Begitu bundel ada, port MANDIRI — folder game boleh dipindah/di-rename/dihapus.
    Isi bundel dibuat oleh `python port/import_assets.py` dan tidak ikut ke git.
    """
    here = os.path.dirname(__file__)
    bundle = os.path.abspath(os.path.join(here, "data"))
    if all(os.path.exists(os.path.join(bundle, n)) for n in _NEEDED):
        return bundle

    # Cadangan: folder game asli di dalam repo kerja (mode pengembangan).
    for cand in ("_ORIGINAL_READONLY", "Creative-Contraptions", "work"):
        d = os.path.abspath(os.path.join(here, "..", "..", cand))
        if all(os.path.exists(os.path.join(d, n)) for n in _NEEDED):
            return d

    raise FileNotFoundError(
        "Aset tidak ditemukan.\n"
        "  Jalankan dulu:  python port/import_assets.py <folder_game_asli>\n"
        "  Folder itu harus berisi: " + ", ".join(_NEEDED))
