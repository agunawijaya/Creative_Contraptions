"""Arsip aset (GRAPH / MECHS / MISC / ANIMATE) — aturan dari sumber terverifikasi.

⚠ INI SATU-SATUNYA implementasi aturan arsip di proyek. `work/genscreens.py` dan
port memakai modul yang SAMA. Alasannya pahit: dulu katalog part dan penggenerasi
layar punya jalur kode sendiri-sendiri untuk aturan yang sama, dan salah satunya
salah selama berbulan-bulan tanpa ketahuan. Dua implementasi satu aturan bukan
redundansi -- itu dua kesempatan untuk salah secara terpisah.

Sumber tiap aturan (semuanya sudah cocok byte-per-byte dengan biner asli):

  loadarc.c  direktori = record 12 byte berturut sampai id == 0;
             cocok kalau (id & 0x7f) == tipe ATAU id == tipe -- KEDUANYA wajib
  nvar.c     record yang `row`-nya sama dengan sebelumnya DILEWATI;
             sisanya varian. row >= 100 = bagian lanjutan, bukan varian
  place.c    rantai satu part = record awal + record ber-id sama dengan
             row == awal.row + 100
  pickvar.c  pemulihan tanda geser memakai ambang 0x80 (BUKAN 0xC8; yang 0xC8
             hanya untuk penggambar skrip animasi f278e.c)

Tata letak record 12 byte:
  +0 id (bit7 = penanda kelompok)  +1 row   +2 h   +3 w
  +4 dy                           +5 dx    +6 len(u16)  +8 off(u32)
⚠ +4 adalah dy dan +5 adalah dx, bukan sebaliknya. Konsisten dengan urutan
  argumen blit yang terbaca dari drawslot.c: blit(spr, Y, X, H, W).
"""
import struct


def sgn(v):
    """Pemulihan tanda untuk geser dx/dy pada PENEMPATAN STATIS: ambang 0x80."""
    return v - 256 if v >= 0x80 else v


def decode_rle(data):
    """RLE: E4 <jumlah> <nilai> -> ulangi; byte lain -> salin apa adanya."""
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


class Archive:
    def __init__(self, path):
        self.raw = open(path, "rb").read()
        self.recs = []
        i = 0
        while i + 12 <= len(self.raw):
            rid, row, h, w, dy, dx, ln, off = struct.unpack_from("<BBBBBBHI", self.raw, i)
            if rid == 0:                      # loadarc.c: id == 0 -> direktori habis
                break
            self.recs.append(dict(idx=len(self.recs), id=rid, row=row, w=w, h=h,
                                  dx=sgn(dx), dy=sgn(dy), ln=ln, off=off))
            i += 12
        self._cache = {}

    # ---- piksel ----------------------------------------------------------
    def pixels(self, r):
        """Sprite -> list baris berisi indeks warna 0..3 (CGA 2 bpp, row-major)."""
        k = r["idx"]
        if k not in self._cache:
            dec = decode_rle(self.raw[r["off"]:r["off"] + r["ln"]])
            wb = r["w"] // 4
            need = wb * r["h"]
            if len(dec) < need:
                dec = dec + bytes(need - len(dec))
            rows = []
            for y in range(r["h"]):
                line = []
                for cb in range(wb):
                    byte = dec[y * wb + cb]
                    for p in range(4):
                        line.append((byte >> (6 - 2 * p)) & 3)
                rows.append(line)
            self._cache[k] = rows
        return self._cache[k]

    # ---- aturan pemilihan ------------------------------------------------
    def cocok(self, r, tipe):
        """loadarc.c: (id & 0x7f) == tipe ATAU id == tipe.

        Cabang kedua WAJIB: MECHS memakai id 100..150, dan untuk id >= 128
        masker 0x7f mengubah 130 jadi 2 -- cocok dengan tipe yang salah.
        """
        return (r["id"] & 0x7F) == tipe or r["id"] == tipe

    def variants(self, tipe):
        """Indeks record yang MENGAWALI tiap varian dari `tipe` (nvar.c)."""
        out, last = [], None
        for r in self.recs:
            if not self.cocok(r, tipe):
                continue
            if r["row"] != last:
                if r["row"] < 100:
                    out.append(r["idx"])
                last = r["row"]
        return out

    def kelompok(self, start):
        """FRAME ANIMASI satu part: record berurutan yang berbagi (id, row).

        Ini BUKAN `chain()` dan bukan `variants()`. Ketiganya mengelompokkan
        record dengan cara berbeda, dan membingungkannya akan salah diam-diam:

            variants()  record yang MENGAWALI tiap varian (row berganti)
            chain()     record awal + potongan bawahnya (row + 100)
            kelompok()  record awal + frame-frame animasinya (row SAMA)

        Contoh GRAPH: id=1 row=2 punya lima record (idx 1..5). Yang pertama
        adalah bentuk diam; sisanya frame yang dipasang `animvm()` saat part
        itu bergerak.

        ⚠ Frame animasi ada di GRAPH/MECHS, BUKAN di ANIMATE. Berkas ANIMATE
        berisi SKRIP (arus opcode) yang menentukan frame mana dipakai kapan --
        nama berkasnya menyesatkan. Diperiksa dengan mencari record mana yang
        mencocokkan frame rujukan f0020 goal 1: GRAPH idx 3 menurunkan beda
        di kotak part itu dari 528 piksel jadi 49; tak satu pun dari 240
        record ANIMATE mendekati.
        """
        r0 = self.recs[start]
        got = []
        for r in self.recs[start:]:
            if r["id"] != r0["id"] or r["row"] != r0["row"]:
                break
            got.append(r["idx"])
        return got

    def chain(self, start):
        """place.c: record awal + pasangannya di row+100 (kalau ada)."""
        r0 = self.recs[start]
        got = [r0]
        for r in self.recs[start + 1:]:
            if r["id"] != r0["id"]:
                break
            if r["row"] == r0["row"] + 100:
                got.append(r)
                break
        return got

    def bbox(self, start):
        """Kotak pembatas SATU part utuh, dihitung dari SELURUH rantainya."""
        ch = self.chain(start)
        return (min(r["dx"] for r in ch), min(r["dy"] for r in ch),
                max(r["dx"] + r["w"] for r in ch), max(r["dy"] + r["h"] for r in ch))
