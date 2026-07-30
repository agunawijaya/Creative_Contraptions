"""Daftar simbol PUBDEF (didefinisikan) dan EXTDEF (dibutuhkan) dari semua .OBJ.

Dipakai untuk tahu stub apa saja yang harus dibuat sebelum bisa LINK.

    python src_c/verify/symbols.py
"""
import glob
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src_c", "out")


def names(path):
    """Kembalikan (set PUBDEF, set EXTDEF) dari satu .OBJ (format OMF)."""
    b = open(path, "rb").read()
    pub, ext = set(), set()
    i = 0
    while i + 3 <= len(b):
        t = b[i]
        ln = struct.unpack_from("<H", b, i + 1)[0]
        body = b[i + 3:i + 3 + ln - 1]
        if t == 0x90 and len(body) >= 3:          # PUBDEF
            j = 2 if (body[0] or body[1]) else 2  # basegrp+baseseg (indeks 1 byte)
            j = 2
            while j < len(body):
                n = body[j]
                if n == 0 or j + 1 + n > len(body):
                    break
                pub.add(body[j + 1:j + 1 + n].decode("ascii", "replace"))
                j += 1 + n + 2 + 1               # nama + offset(2) + type(1)
        elif t == 0x8C:                           # EXTDEF
            j = 0
            while j < len(body):
                n = body[j]
                if n == 0 or j + 1 + n > len(body):
                    break
                ext.add(body[j + 1:j + 1 + n].decode("ascii", "replace"))
                j += 1 + n + 1                   # nama + type(1)
        i += 3 + ln - 1 + 1
    return pub, ext


def main():
    objs = sorted(glob.glob(os.path.join(OUT, "*.OBJ")))
    allpub, allext = set(), set()
    for p in objs:
        if os.path.basename(p).lower().startswith("probe"):
            continue
        pub, ext = names(p)
        allpub |= pub
        allext |= ext
    missing = sorted(allext - allpub)
    print("%d .OBJ diperiksa" % len(objs))
    print("didefinisikan : %d simbol" % len(allpub))
    print("dibutuhkan    : %d simbol" % len(allext))
    print()
    print("BELUM ADA (%d) -- perlu stub atau rekonstruksi:" % len(missing))
    for i in range(0, len(missing), 6):
        print("   " + "  ".join("%-12s" % m for m in missing[i:i + 6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
