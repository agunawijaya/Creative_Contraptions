"""Alat segmen DATA (DGROUP): dump beranotasi + banding .OBJ vs biner asli.

DGROUP biner asli ada di offset citra 0x9070 (= LOAD_SEG + 0x907 paragraf),
panjang 9.556 byte. Alamat yang dipakai kode (mis. 0x792, 0xa37) adalah
offset DI DALAM DGROUP, jadi bisa dipakai langsung sebagai indeks di sini.

    python src_c/verify/dgroup.py                 # ringkasan wilayah
    python src_c/verify/dgroup.py 0x840 64        # dump beranotasi
    python src_c/verify/dgroup.py --str           # semua string + offsetnya
    python src_c/verify/dgroup.py --cmp x.OBJ 0   # banding segmen DATA .OBJ
                                                   mulai dari offset DGROUP
"""
import os
import re
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXE = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
DG_PARA = 0x907


def dgroup():
    b = open(EXE, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    return b[lb + DG_PARA * 16:]


def strings(d):
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{4,}\x00", d):
        out.append((m.start(), m.group(0)[:-1].decode("ascii")))
    return out


def summary(d):
    print("DGROUP: %d byte (offset citra 0x%04x)" % (len(d), DG_PARA * 16))
    ss = strings(d)
    print("string  : %d buah, %d byte" % (ss, sum(len(s) + 1 for _, s in ss))
          if False else "string  : %d buah, %d byte" % (len(ss), sum(len(s) + 1 for _, s in ss)))
    # wilayah nol besar = kandidat BSS (variabel tanpa nilai awal)
    zr = [(m.start(), len(m.group(0))) for m in re.finditer(rb"\x00{32,}", d)]
    print("blok nol: %d buah, %d byte (kandidat BSS)" % (len(zr), sum(n for _, n in zr)))
    for o, n in zr[:8]:
        print("    0x%04x  %5d byte" % (o, n))
    if ss:
        print("rentang string pertama..terakhir: 0x%04x .. 0x%04x" % (ss[0][0], ss[-1][0]))


def dump(d, off, n):
    ss = dict(strings(d))
    for r in range(off, min(off + n, len(d)), 16):
        row = d[r:r + 16]
        hx = " ".join("%02x" % c for c in row)
        tx = "".join(chr(c) if 32 <= c < 127 else "." for c in row)
        note = ""
        for k in range(r, r + 16):
            if k in ss:
                note = "  <- \"%s\"" % ss[k][:40]
                break
        print("  %04x  %-47s  |%s|%s" % (r, hx, tx, note))


def compare_obj(path, at):
    """Banding segmen DATA sebuah .OBJ dengan DGROUP asli mulai offset `at`."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from objcode import read_omf
    segs = read_omf(path)
    if not segs:
        print("OBJ tanpa segmen")
        return 1
    # segmen DATA = yang BUKAN terbesar (kode); kalau cuma satu, pakai itu
    order = sorted(segs.items(), key=lambda kv: len(kv[1][0]), reverse=True)
    seg, (data, slots) = order[1] if len(order) > 1 else order[0]
    d = dgroup()
    orig = d[at:at + len(data)]
    diff = [k for k in range(min(len(data), len(orig))) if data[k] != orig[k]]
    print("segmen data .OBJ: seg%d, %d byte; dibanding DGROUP+0x%04x" % (seg, len(data), at))
    print("beda: %d byte" % len(diff))
    if diff:
        k = diff[0]
        print("beda pertama +%d" % k)
        print("  kita: " + " ".join("%02x" % c for c in data[max(0, k - 8):k + 24]))
        print("  asli: " + " ".join("%02x" % c for c in orig[max(0, k - 8):k + 24]))
    return 0 if not diff else 1


if __name__ == "__main__":
    d = dgroup()
    a = sys.argv[1:]
    if not a:
        summary(d)
    elif a[0] == "--str":
        for o, s in strings(d):
            print("  0x%04x  %r" % (o, s))
    elif a[0] == "--cmp":
        sys.exit(compare_obj(a[1], int(a[2], 0)))
    else:
        dump(d, int(a[0], 0), int(a[1], 0) if len(a) > 1 else 128)
