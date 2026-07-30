"""Bangkitkan src_c/src/gdata.c — rekonstruksi segmen DATA (DGROUP).

Cara kerja: susuri DGROUP biner asli dari offset 0 sampai habis. Di setiap
offset yang punya simbol terdokumentasi (dipanen dari komentar `/* @0xNNN */`
di src_c/src/*.c), pancarkan deklarasi bernama; di antaranya pancarkan array
pengisi. SEMUA deklarasi diberi nilai awal eksplisit dari byte biner.

Kenapa nilai awal eksplisit: variabel tanpa nilai awal masuk BSS dan TIDAK
dipancarkan ke .OBJ, sehingga tak bisa dibandingkan per-berkas. Dengan nilai
awal, segmen data .OBJ bisa langsung dibanding ke DGROUP asli
(`python src_c/verify/dgroup.py --cmp src_c/out/gdata.OBJ 0`).

    python src_c/build/gendata.py [batas_offset]
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src_c", "verify"))
from dgroup import dgroup                                    # noqa: E402

SRC = os.path.join(ROOT, "src_c", "src")
OUTC = os.path.join(SRC, "gdata.c")

# gdata.c mulai dari offset 4, BUKAN 0. Empat byte pertama DGROUP disumbang
# oleh C.OBJ (crt0) yang selalu di-link paling depan; kalau gdata.c ikut
# memancarkannya, seluruh DGROUP bergeser 4 byte dan tiap alamat jadi salah.
# Terbukti dari peta link: DATA+0x0004 = DGROUP+0x0000 biner asli.
START = 4

# Alamat DGROUP dipanen dari komentar di ujung deklarasi extern. Komentarnya
# boleh berisi teks lain sebelum alamatnya (mis. "tabel entri menu @0x1634").
DECL = re.compile(
    r"extern\s+(?:unsigned\s+)?(?:struct\s+(\w+)\s+)?(char|int|unsigned)?\s*\**\s*"
    r"(\w+)\s*(\[\s*\])?\s*;.*?@?0x([0-9a-fA-F]{2,4})")


def harvest():
    """name -> (addr, tipe, is_array); dipanen dari komentar di sumber kita."""
    out = {}
    for f in sorted(glob.glob(os.path.join(SRC, "*.c"))):
        if os.path.basename(f) == "gdata.c":
            continue
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for m in DECL.finditer(s):
            st, typ, name, arr, addr = m.groups()
            # penunjuk & struct diperlakukan sebagai kata/byte biasa di sini
            out.setdefault(name, (int(addr, 16), typ or ("char" if st else "int"), bool(arr)))
    return out


def words(d, a, n):
    return ["0x%04x" % (d[a + 2 * k] | (d[a + 2 * k + 1] << 8)) for k in range(n)]


def bytes_(d, a, n):
    return ["0x%02x" % d[a + k] for k in range(n)]


def emit_list(fh, items, per):
    for i in range(0, len(items), per):
        fh.write("    " + ", ".join(items[i:i + per]) +
                 ("," if i + per < len(items) else "") + "\n")


def main():
    d = dgroup()
    limit = int(sys.argv[1], 0) if len(sys.argv) > 1 else len(d)
    syms = sorted((a, n, t, arr) for n, (a, t, arr) in harvest().items()
                  if START <= a < limit)

    fh = io.open(OUTC, "w", encoding="utf-8", newline="")
    fh.write("/* gdata.c — DIBANGKITKAN oleh src_c/build/gendata.py. JANGAN disunting tangan.\n"
             " *\n"
             " * Rekonstruksi segmen DATA (DGROUP) biner asli. Simbol bernama diletakkan\n"
             " * pada offset yang sudah terdokumentasi di berkas sumber lain; celah di\n"
             " * antaranya diisi array `padN`. Semua diberi nilai awal eksplisit supaya\n"
             " * ikut dipancarkan ke .OBJ dan bisa dibandingkan byte-per-byte.\n"
             " *\n"
             " * Verifikasi:\n"
             " *   pwsh src_c/build/compile.ps1 -Name gdata\n"
             " *   python src_c/verify/dgroup.py --cmp src_c/out/gdata.OBJ 0\n"
             " */\n\n")

    pos = START
    pad = 0
    for k, (a, name, typ, arr) in enumerate(syms):
        if a < pos:
            continue                                    # tumpang tindih: lewati
        if a > pos:
            n = a - pos
            pad += 1
            fh.write("char pad%d[%d] = {\n" % (pad, n))
            emit_list(fh, bytes_(d, pos, n), 12)
            fh.write("};\n\n")
            pos = a
        nxt = syms[k + 1][0] if k + 1 < len(syms) else limit
        size = nxt - a
        if not arr:
            fh.write("int %s = %s;\n\n" % (name, words(d, a, 1)[0]))
            pos = a + 2
        elif typ == "char" or size % 2 or a % 2:
            # Ukuran/alamat GANJIL wajib pakai array byte: array int akan
            # dibulatkan ke atas dan menggeser seluruh sisa DGROUP satu byte.
            # (Kasus nyata: tune2 @0x1ddb, alamat ganjil.)
            fh.write("char %s[%d] = {\n" % (name, size))
            emit_list(fh, bytes_(d, a, size), 12)
            fh.write("};\n\n")
            pos = a + size
        else:
            nw = size // 2
            fh.write("int %s[%d] = {\n" % (name, nw))
            emit_list(fh, words(d, a, nw), 8)
            fh.write("};\n\n")
            pos = a + nw * 2

    if pos < limit:
        n = limit - pos
        pad += 1
        fh.write("char pad%d[%d] = {\n" % (pad, n))
        emit_list(fh, bytes_(d, pos, n), 12)
        fh.write("};\n")
    fh.close()
    print("gdata.c dibangkitkan: %d simbol bernama, %d blok pengisi, sampai offset 0x%04x"
          % (len(syms), pad, limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
