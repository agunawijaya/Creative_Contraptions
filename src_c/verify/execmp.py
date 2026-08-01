# execmp.py -- bandingkan SELURUH .EXE hasil link dengan biner asli, byte-per-byte.
#
# ⚠⚠ INI SATU-SATUNYA ALAT YANG MELIHAT IDENTITAS SIMBOL.
#
# `verifyall.py`/`aligncmp.py` membandingkan .OBJ terhadap biner asli dengan slot
# relokasi di-WILDCARD -- terpaksa, karena di .OBJ alamatnya belum diisi. Efek
# sampingnya: kalau kode kita menunjuk simbol yang SALAH, byte-nya tetap
# dilaporkan COCOK. Pada 2026-08-01 alat ini menemukan 24 byte semacam itu di
# empat fungsi yang semuanya berstatus "COCOK byte-per-byte":
#
#   main_    2 B  prevtop/prevx tertukar (urutan simpanan)
#   animvm  12 B  prevtop/prevx tertukar di enam situs
#   drawball 6 B  ballx/ballrow/bally dan prevrow/prevy/prevx bergeser satu putaran
#   loadcon  4 B  nzany/nmech tertukar (kompiler meng-CSE nmech, memuatnya duluan)
#
# Jalankan SETIAP KALI sesudah link. Kalau hasilnya bukan 0 atau 1 byte, ada
# simbol yang salah -- bukan sekadar bentuk kode.
#
#   python src_c/verify/execmp.py           # ringkasan
#   python src_c/verify/execmp.py -v        # + daftar byte + fungsi pemiliknya
#
# SATU byte yang memang tidak bisa dicocokkan: 0x5485 di `load` -- byte TINGGI
# dari immediate sampah `add ax,9449h` yang dipancarkan MS C untuk perbandingan
# `p == -1L` yang rusak. Nilainya ALAMAT HEAP INTERNAL kompiler. Sudah diukur:
# mengganti nama berkas sumber menggesernya (LOAD=0x38, LD/L=0x3a, LOADIT=0x36,
# LOADREC=0x34, RDBLK/GETREC/LOADX=0x36) tapi TIDAK PERNAH sampai 0x94. Jadi ia
# ditentukan tata letak memori mesin yang mengompilasi, bukan oleh sumber C.
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIG = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
OURS = os.path.join(ROOT, "src_c", "out", "CONTRAP.EXE")
MANIFEST = os.path.join(ROOT, "src_c", "src", "manifest.txt")
ARTEFAK = {0x5485}


def muatan(path):
    """(load module, header) -- bagian .EXE yang benar-benar dimuat ke memori."""
    b = open(path, "rb").read()
    lastpage, pages, nreloc, hdrpar = struct.unpack_from("<HHHH", b, 2)
    img = (pages - 1) * 512 + (lastpage or 512)
    return b[hdrpar * 16:img], b


def fungsi():
    out = []
    for ln in open(MANIFEST, encoding="utf-8"):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        p = ln.split()
        if int(p[2]) == 0:
            continue
        out.append((int(p[1], 16), int(p[2]), p[0]))
    return sorted(out)


def main():
    verbose = "-v" in sys.argv
    lo, bo = muatan(ORIG)
    lm, bm = muatan(OURS)
    print("muatan  : asli %d byte, kita %d byte  (%s)"
          % (len(lo), len(lm), "SAMA" if len(lo) == len(lm) else "BEDA"))
    for nama, off in (("cs:ip", 20), ("ss:sp", 14), ("nreloc", 6)):
        a = bo[off:off + 4]
        m = bm[off:off + 4]
        print("  %-7s: %s" % (nama, "sama" if a == m else "BEDA %s vs %s"
                              % (a.hex(), m.hex())))
    n = min(len(lo), len(lm))
    bad = [i for i in range(n) if lo[i] != lm[i]]
    nyata = [i for i in bad if i not in ARTEFAK]
    print("BEDA    : %d byte (%d di antaranya artefak kompiler yang diketahui)"
          % (len(bad), len(bad) - len(nyata)))
    if verbose and bad:
        fs = fungsi()

        def milik(a):
            for ad, sz, nm in fs:
                if ad <= a < ad + sz:
                    return "%s+%d" % (nm, a - ad)
            return "?"
        for i in bad:
            print("   0x%04x  asli %02x  kita %02x   %s%s"
                  % (i, lo[i], lm[i], milik(i),
                     "   [ARTEFAK KOMPILER]" if i in ARTEFAK else ""))
    if not nyata:
        print("=> .EXE IDENTIK dengan biner asli (kecuali artefak kompiler).")
        return 0
    print("=> %d byte BEDA NYATA -- kemungkinan besar IDENTITAS SIMBOL, "
          "bukan bentuk kode. Jalankan dengan -v." % len(nyata))
    return 1


if __name__ == "__main__":
    sys.exit(main())
