"""Pemeriksa: komentar blok yang MENELAN baris kode.

Bug ini sudah tiga kali memakan beberapa putaran (keyhit, unrle, autofill):
komentar `/* ... */` multi-baris yang dimulai di ujung sebuah pernyataan akan
menelan baris-baris berikutnya, sehingga kode tidak pernah ikut terkompilasi —
dan hasilnya terlihat seperti "hipotesis saya salah".

Dijalankan otomatis oleh buildall.ps1 SEBELUM kompilasi.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))


def main():
    bad = []
    for f in sorted(glob.glob(os.path.join(ROOT, "*.c"))):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"/\*.*?\*/", s, re.S):
            body = m.group(0)
            if "\n" not in body:
                continue
            for ln in body.split("\n")[1:]:
                t = ln.strip()
                # baris di dalam komentar yang tampak seperti pernyataan C
                if t.endswith(";") and not t.startswith("*"):
                    bad.append((os.path.basename(f), t))
                    break
    if bad:
        print("GAGAL: komentar menelan kode --")
        for f, t in bad:
            print("   %-16s %s" % (f, t))
        return 1
    print("lint: ok (tidak ada kode tertelan komentar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
