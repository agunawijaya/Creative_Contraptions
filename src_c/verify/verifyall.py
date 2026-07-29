"""Verifikasi SEMUA fungsi yang sudah direkonstruksi terhadap biner asli.

Membaca src_c/src/manifest.txt berisi baris:  <nama> <alamat_hex> <ukuran>
lalu membandingkan src_c/out/<nama>.OBJ dengan potongan biner yang sesuai.

    python src_c/verify/verifyall.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from objcode import read_omf, pick_code_segment, TARGET, IMAGE_BASE   # noqa: E402

MANIFEST = os.path.join(ROOT, "src", "manifest.txt")
OUT = os.path.join(ROOT, "out")


def entries():
    for ln in open(MANIFEST, encoding="utf-8"):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        p = ln.split()
        yield p[0], int(p[1], 16), int(p[2])


def main():
    tgt = open(TARGET, "rb").read()
    rows, ok_bytes, tot_bytes = [], 0, 0
    for name, addr, size in entries():
        tot_bytes += size
        obj = os.path.join(OUT, name + ".OBJ")
        if not os.path.exists(obj):
            rows.append((name, addr, size, "TIDAK ADA .OBJ", 0))
            continue
        segs = read_omf(obj)
        if not segs:
            rows.append((name, addr, size, "OBJ kosong", 0))
            continue
        _, (code, slots) = pick_code_segment(segs)
        orig = tgt[IMAGE_BASE + addr: IMAGE_BASE + addr + size]
        if len(code) != len(orig):
            rows.append((name, addr, size, "panjang %d != %d" % (len(code), len(orig)), 0))
            continue
        real = [k for k in range(len(orig)) if code[k] != orig[k] and k not in slots]
        if real:
            rows.append((name, addr, size, "%d byte beda (mis. +%d)" % (len(real), real[0]), 0))
        else:
            rows.append((name, addr, size, "COCOK", size))
            ok_bytes += size

    w = max(len(r[0]) for r in rows) if rows else 8
    print("%-*s  %-7s %6s  %s" % (w, "fungsi", "alamat", "ukuran", "hasil"))
    print("-" * (w + 30))
    for name, addr, size, res, _ in rows:
        print("%-*s  0x%04x  %6d  %s" % (w, name, addr, size, res))
    n_ok = sum(1 for r in rows if r[3] == "COCOK")
    print()
    print("COCOK %d/%d fungsi   |   %d byte terverifikasi (dari %d byte yang digarap)"
          % (n_ok, len(rows), ok_bytes, tot_bytes))
    print("Target seluruh kode C game: ~26.000 byte (perkiraan dari wilayah alamat)  ->  %.1f%% selesai"
          % (ok_bytes / 26000.0 * 100))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
