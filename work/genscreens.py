"""Bangkitkan layar "Fill in Mechanisms" dari BERKAS ASET — tanpa menjalankan game.

BUKTI APA. Kalau dekompilasi kita benar, seluruh layar harus bisa disusun ulang
dari berkas data asli + algoritma yang direkonstruksi, tanpa mengeksekusi satu
instruksi pun dari CONTRAP.EXE.

⚠ ATURAN MAIN: skrip ini TIDAK BOLEH membaca apa pun dari `work/emu_caps/` atau
`port/cc/draws/` -- itu tangkapan hasil MENJALANKAN program. Berkas itu hanya
dipakai oleh `--verifikasi`, dan hanya untuk MEMERIKSA hasilnya.

⭐ Aturan arsip dan penempatannya TIDAK lagi ditulis di sini. Semuanya ada di
`port/cc/core/` dan dipakai BERSAMA dengan port. Dulu keduanya punya jalur kode
sendiri-sendiri untuk aturan yang sama, dan salah satunya salah berbulan-bulan
tanpa ketahuan (bagian bawah part id 94 hilang di katalog). Dua implementasi
satu aturan bukan redundansi -- itu dua kesempatan untuk salah secara terpisah.

Pakai:
  python work/genscreens.py                 # tulis PNG semua goal x varian
  python work/genscreens.py --verifikasi    # + cocokkan ke tangkapan emulator
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "port"))
from cc.core import contrap                                   # noqa: E402
from cc.core import render as rend                            # noqa: E402
from cc.core.archive import Archive, decode_rle, sgn          # noqa: E402,F401

DATA = os.path.join(ROOT, "_ORIGINAL_READONLY")
OUT = os.path.join(ROOT, "work", "screens_gen")

PALETTE = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]
BG = 1
W, H = 320, 200


def contrap_goals(path):
    """Nama lama yang masih dipakai skrip lain."""
    return contrap.parse(path)


def render(dl):
    """Daftar gambar -> framebuffer indeks warna. Delegasi ke penggambar BERSAMA
    di port/cc/core/render.py -- jangan tulis ulang primitifnya di sini."""
    return rend.apply(rend.new_fb(), dl)


def simpan(fb, path):
    rend.simpan_png(fb, path)


def main():
    graph = Archive(os.path.join(DATA, "GRAPH"))
    mechs = Archive(os.path.join(DATA, "MECHS"))
    misc = Archive(os.path.join(DATA, "MISC"))
    cs = contrap.parse(os.path.join(DATA, "CONTRAP"))
    os.makedirs(OUT, exist_ok=True)
    print("GRAPH %d record, MECHS %d record, MISC %d record"
          % (len(graph.recs), len(mechs.recs), len(misc.recs)))
    total = 0
    for goal in sorted(cs):
        for vi, var in enumerate(cs[goal]):
            for isi, tag in ((False, "kosong"), (True, "penuh")):
                dl = contrap.draw_list(var, graph, mechs, misc, 0, isi)
                simpan(render(dl),
                       os.path.join(OUT, "fillmech_goal%d_v%d_%s.png" % (goal, vi, tag)))
                total += 1
            print("  goal %d varian %d: %d zany, %d mekanisme -> %d blit"
                  % (goal, vi, len(var["zany"]), len(var["mech"]),
                     sum(1 for d in dl if d["kind"] == "blit")))
    print("%d PNG -> %s" % (total, OUT))
    if "--verifikasi" in sys.argv:
        verifikasi(cs, graph, mechs, misc)


def verifikasi(cs, graph, mechs, misc):
    """Setiap blit yang DITANGKAP emulator harus bisa dijelaskan oleh mesin ini."""
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
        bisa = contrap.semua_kemungkinan(cs[goal][vi], graph, mechs, misc)
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
