"""Bangkitkan layar mode "Fill in Mechanisms" LANGSUNG dari berkas aset — TANPA
menjalankan game.

BUKTI APA. Kalau dekompilasi kita benar, seluruh layar harus bisa disusun ulang
dari BERKAS DATA ASLI + ALGORITMA yang direkonstruksi, tanpa mengeksekusi satu
instruksi pun dari CONTRAP.EXE. Skrip ini melakukan itu.

⚠ ATURAN MAIN: skrip ini TIDAK BOLEH membaca apa pun dari `work/emu_caps/` atau
`port/cc/draws/` — itu tangkapan hasil MENJALANKAN program. Berkas-berkas itu
hanya dipakai oleh `--verifikasi`, dan hanya untuk MEMERIKSA hasilnya.

SUMBER ALGORITMA (semuanya dari src_c yang sudah byte-identical):
  loadarc.c  direktori arsip = record 12 byte berturut sampai id==0
  nvar.c     "record dengan `row` sama dengan sebelumnya DILEWATI" -> yang
             tersisa adalah VARIAN; varian yang punya pasangan `row+100`
             digambar sebagai DUA record
  place.c    ikuti RANTAI: record berikutnya ikut disalin kalau id sama dan
             row sama atau row+100
  f278e.c    blit(rec->spr, x + dx, y + dy, w, h) -- posisi layar = posisi
             komponen di CONTRAP DITAMBAH geser per-record
  assets.py  RLE escape 0xE4 <count> <value>; piksel CGA 2bpp row-major
  cga.py     palet CGA-1 low-intensity, background biru

TATA LETAK RECORD 12 BYTE (diturunkan dari biner, bukan ditebak):
  +0 id (bit7 = kelompok)   +1 row      +2 h        +3 w
  +4 dy                     +5 dx       +6 len(u16) +8 off(u32)
⚠ +4 adalah dy dan +5 adalah dx -- BUKAN sebaliknya. Diverifikasi: zany goal 1
  tipe 2 di (28,97) menghasilkan bagian kedua di (8,125) = (28-20, 97+28),
  dan record-nya berisi +4=28, +5=-20.

Pakai:
  python work/genscreens.py                 # tulis PNG semua goal x varian
  python work/genscreens.py --verifikasi    # + cocokkan ke tangkapan emulator
"""
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_ORIGINAL_READONLY")
OUT = os.path.join(ROOT, "work", "screens_gen")

PALETTE = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
BG = 1                                   # cyan = latar game
W, H = 320, 200


def sgn(v):
    """Pemulihan tanda untuk geser dx/dy pada PENEMPATAN STATIS: ambang 0x80.

    ⚠ Ada DUA ambang berbeda di biner dan keduanya benar di tempatnya:
      pickvar.c / place.c (menempatkan part di layar) -> `>= 0x80`
      f278e.c  (menggambar dari skrip ANIMASI)        -> `>= 0xC8`
    Memakai 0xC8 di sini membuat empat part meleset jauh: mis. zany tipe 71
    goal 3 punya dx=155, yang dengan 0x80 menjadi -101 (196-101 = 95, cocok
    dengan biner) tapi dengan 0xC8 tetap +155 dan mendarat di luar layar.
    """
    return v - 256 if v >= 0x80 else v


def decode_rle(data):
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
    """Direktori record 12 byte, dibaca persis seperti loadarc.c."""

    def __init__(self, path):
        self.raw = open(path, "rb").read()
        self.recs = []
        i = 0
        while i + 12 <= len(self.raw):
            rid, row, h, w, dy, dx, ln, off = struct.unpack_from("<BBBBBBHI", self.raw, i)
            if rid == 0:                 # loadarc.c: id==0 -> direktori habis
                break
            # ⚠ Batas 0x78 di loadarc.c membatasi jumlah record yang DISIMPAN
            #   (sesudah disaring), BUKAN yang dipindai. Direktori GRAPH punya
            #   550 record; memotongnya di 120 membuang sebagian besar tipe.
            self.recs.append(dict(idx=len(self.recs), id=rid, row=row, w=w, h=h,
                                  dx=sgn(dx), dy=sgn(dy), ln=ln, off=off))
            i += 12
        self._c = {}

    def pixels(self, r):
        """Sprite -> list baris berisi indeks warna 0..3."""
        k = r["idx"]
        if k not in self._c:
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
            self._c[k] = rows
        return self._c[k]

    def variants(self, tipe):
        """Indeks record yang MENGAWALI tiap varian dari `tipe`.

        nvar.c: susuri direktori, ambil record yang (id & 0x7f) == tipe, dan
        LEWATI yang `row`-nya sama dengan record sebelumnya -- sisanya varian.
        Bagian lanjutan (row >= 100) bukan varian tersendiri.
        """
        out, last = [], None
        for r in self.recs:
            # loadarc.c: cocok kalau (id & 0x7f) == tipe ATAU id == tipe.
            # ⚠ Dua-duanya WAJIB. MECHS memakai id 100..150; untuk id >= 128
            #   masker 0x7f mengubah 130 jadi 2, jadi hanya perbandingan penuh
            #   yang cocok. Tanpa cabang kedua, SEMUA mekanisme id >= 128 hilang.
            if (r["id"] & 0x7F) != tipe and r["id"] != tipe:
                continue
            if r["row"] != last:
                if r["row"] < 100:
                    out.append(r["idx"])
                last = r["row"]
        return out

    def chain(self, start):
        """place.c: ikuti rantai record yang membentuk SATU part.

        Syarat lanjutnya, persis dari place.c:
            next.id == cur.id  &&  (next.row == cur.row || cur.row + 100 == next.row)
        Iteratif -- `cur` ikut maju, jadi satu part bisa terdiri lebih dari dua
        record (mis. batang tipis yang menempel di goal 1 varian 1).
        """
        r0 = self.recs[start]
        got = [r0]
        for r in self.recs[start + 1:]:
            if r["id"] != r0["id"]:
                break
            if r["row"] == r0["row"] + 100:
                got.append(r)
                break
        return got


def contrap(path):
    """CONTRAP -> {goal: [varian]}; tiap varian {mech:[(y,x,tipe)], zany:[...]}"""
    b = open(path, "rb").read()
    n = struct.unpack_from("<I", b, 2)[0] // 6
    goals = {}
    for i in range(n):
        gid, off = struct.unpack_from("<HI", b, i * 6)
        if gid == 0 or gid >= 128:
            continue
        p = off
        goal = struct.unpack_from("<H", b, p)[0]
        p += 2
        cA = struct.unpack_from("<H", b, p)[0]
        p += 2 + cA * 4
        cB = struct.unpack_from("<H", b, p)[0]
        p += 2
        mech = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cB)]
        p += cB * 6
        cC = struct.unpack_from("<H", b, p)[0]
        p += 2
        zany = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cC)]
        goals.setdefault(goal, []).append(dict(mech=mech, zany=zany))
    return goals


# Elemen TETAP di puncak layar: corong tempat bola mulai, 48x8 di (136,0).
# Muncul di SEMUA goal dan SEMUA varian. Sumbernya arsip MISC, dan record mana
# yang dipakai sudah dipastikan lewat tangkapan VRAM asli: MISC id=2 punya DUA
# record 48x8 (idx 2 dan 3, dua warna berbeda); idx 2 cocok 384/384 piksel di
# setiap tangkapan, idx 3 hanya 140/384. Jadi bukan tebakan.
CORONG = dict(arch="misc", rec_idx=2, x=136, y=0)


def draws(var, graph, mechs, pilih=0, isi_mekanisme=False):
    """Daftar blit untuk SATU varian struktur.

    `pilih` = indeks varian part yang dipakai untuk SETIAP slot. Di game
    aslinya pickpart() mengundinya acak (rnd()), jadi tidak ada satu jawaban
    "benar" -- di sini dibuat deterministik supaya hasilnya bisa diulang.

    `isi_mekanisme=False` = layar AWAL mode Fill in Mechanisms: slot mekanisme
    masih KOSONG (pemain yang mengisi). True = contraption lengkap.
    """
    out = []
    for kelompok, arc, gambar in (("zany", graph, True),
                                  ("mech", mechs, isi_mekanisme)):
        for (y, x, tipe) in var[kelompok]:
            vs = arc.variants(tipe)
            if not vs:
                continue
            if not gambar:
                out.append(dict(kind="slot", x=x, y=y, arch=kelompok))
                continue
            for r in arc.chain(vs[min(pilih, len(vs) - 1)]):
                out.append(dict(kind="blit", arch=kelompok, rec=r,
                                x=x + r["dx"], y=y + r["dy"],
                                w=r["w"], h=r["h"]))
    return out


def tambah_corong(out, misc):
    r = misc.recs[CORONG["rec_idx"]]
    out.append(dict(kind="blit", arch="misc", rec=r,
                    x=CORONG["x"], y=CORONG["y"], w=r["w"], h=r["h"]))
    return out


def render(dl, graph, mechs, misc=None):
    fb = [[BG] * W for _ in range(H)]
    for d in dl:
        if d["kind"] == "slot":
            # drawslot.c, cabang slot KOSONG -- diambil apa adanya dari sumber:
            #     fillrect(x + 1, y, x + 0x1e, y + 0x17, 3)
            # yaitu blok PENUH warna 3, dari x+1..x+30 dan y..y+23. Bukan
            # tebakan: itu satu-satunya hal yang digambar untuk slot kosong.
            for yy in range(d["y"], min(d["y"] + 0x18, H)):
                for xx in range(d["x"] + 1, min(d["x"] + 0x1F, W)):
                    if 0 <= xx < W and 0 <= yy < H:
                        fb[yy][xx] = 3
            continue
        arc = {"zany": graph, "mech": mechs, "misc": misc}[d["arch"]]
        px = arc.pixels(d["rec"])
        for yy, line in enumerate(px):
            ty = d["y"] + yy
            if not (0 <= ty < H):
                continue
            for xx, c in enumerate(line):
                tx = d["x"] + xx
                if 0 <= tx < W:
                    fb[ty][tx] = c          # OPAQUE, seperti blitter 672f
    return fb


def simpan(fb, path):
    from PIL import Image
    im = Image.new("RGB", (W, H))
    im.putdata([PALETTE[c] for row in fb for c in row])
    im.save(path)


def main():
    verif = "--verifikasi" in sys.argv
    graph = Archive(os.path.join(DATA, "GRAPH"))
    mechs = Archive(os.path.join(DATA, "MECHS"))
    misc = Archive(os.path.join(DATA, "MISC"))
    cs = contrap(os.path.join(DATA, "CONTRAP"))
    os.makedirs(OUT, exist_ok=True)
    print("GRAPH %d record, MECHS %d record" % (len(graph.recs), len(mechs.recs)))
    total = 0
    for goal in sorted(cs):
        for vi, var in enumerate(cs[goal]):
            for isi, tag in ((False, "kosong"), (True, "penuh")):
                dl = tambah_corong(draws(var, graph, mechs, 0, isi), misc)
                fb = render(dl, graph, mechs, misc)
                p = os.path.join(OUT, "fillmech_goal%d_v%d_%s.png" % (goal, vi, tag))
                simpan(fb, p)
                total += 1
            print("  goal %d varian %d: %d zany, %d mekanisme -> %d blit"
                  % (goal, vi, len(var["zany"]), len(var["mech"]),
                     sum(1 for d in dl if d["kind"] == "blit")))
    print("%d PNG -> %s" % (total, OUT))

    if verif:
        verifikasi(cs, graph, mechs, misc)


def verifikasi(cs, graph, mechs, misc):
    """Setiap blit yang DITANGKAP emulator harus bisa dijelaskan oleh mesin ini.

    Varian part diundi acak saat runtime, jadi kita tidak bisa menebak pilihan
    emulator. Yang diperiksa: untuk tiap blit tertangkap, ADA kombinasi
    (kelompok, komponen, varian, mata rantai) yang menghasilkan (x,y,w,h)
    PERSIS sama. Kalau semuanya bisa dijelaskan, algoritmanya benar.
    """
    import json
    import glob
    print()
    print("VERIFIKASI terhadap tangkapan emulator (hanya sebagai pemeriksa):")
    tot = ok = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "port", "cc", "draws",
                                           "draws_goal*_v*.json"))):
        nama = os.path.basename(f)
        goal = int(nama.split("goal")[1].split("_")[0])
        vi = int(nama.split("_v")[1].split(".")[0])
        if goal not in cs or vi >= len(cs[goal]):
            continue
        var = cs[goal][vi]
        # semua (x,y,w,h) yang MUNGKIN dihasilkan mesin ini
        bisa = set()
        for kelompok, arc in (("zany", graph), ("mech", mechs)):
            for (y, x, tipe) in var[kelompok]:
                for v in arc.variants(tipe):
                    for r in arc.chain(v):
                        bisa.add((x + r["dx"], y + r["dy"], r["w"], r["h"]))
        # Corong MISC di (136,0): emulator tidak mengenali arsipnya (arch=None),
        # tapi kita TAHU record mana -- jadi ikut diverifikasi, bukan dilewati.
        rc = misc.recs[CORONG["rec_idx"]]
        bisa.add((CORONG["x"], CORONG["y"], rc["w"], rc["h"]))
        for e in json.load(open(f)):
            tot += 1
            if (e["x"], e["y"], e["w"], e["h"]) in bisa:
                ok += 1
            else:
                print("   TAK TERJELASKAN %s: %s" % (nama, e))
    print("   blit tertangkap yang TERJELASKAN: %d/%d (%.1f%%)"
          % (ok, tot, 100.0 * ok / max(1, tot)))


if __name__ == "__main__":
    main()
