"""REGRESI TABEL LAYAR: alamat + jumlah entri diadu dgn sumber byte-exact.

Kenapa uji ini ada, dan kenapa BUKAN perbandingan piksel
--------------------------------------------------------
Sebelas layar bertabel di gim ini digambar oleh SATU fungsi, `setsel()`
@0x3769. Empat di antaranya sudah diadu piksel dgn VRAM emulator dan cocok
64.000/64.000 (menu utama, level, pemilih goal, credits tahap 0). Yang belum
terfoto adalah `askopts` dan ketiga layar instruksi.

Enam percobaan menangkapnya gagal, dan sebabnya dicatat di `menu.py`. Tapi
menangkapnya juga tidak akan menjawab banyak: RENDERER-nya sudah terbukti pada
empat tabel, dan BYTE tabelnya pasti benar (segmen DATA cocok 9.556/9.556 di
`src_c/verify/verifyall.py`). Yang tersisa sebagai hipotesis cuma dua angka per
layar: ALAMAT tabel dan JUMLAH entri. Itulah yang diuji di sini.

Sumbernya `src_c/src/*.c`, yang `.EXE`-nya sudah terbukti byte-identik dgn
biner asli. Jadi ini bukan "kode saya vs kode saya" -- pembandingnya sumber
yang identitasnya sudah dibuktikan alat lain.

⚠ Uji ini TIDAK membuktikan pikselnya. Ia membuktikan masukannya benar; yang
membuktikan pikselnya adalah `test_nav.py`/`test_menu*` pada empat tabel yang
memakai renderer yang sama.

Bagian kedua memeriksa hal yang cross-check tekstual TIDAK bisa lihat: bahwa
tiap entri benar-benar terdekode -- koordinatnya di dalam layar dan tiap
rujukan sprite/teksnya ada. Alamat yang salah ketik akan lolos bagian satu
hanya kalau salahnya ada di KEDUA berkas; bagian dua tetap menangkapnya.
"""
import os
import re
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "port"))

from cc.core import menu                                       # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

SRC = os.path.join(AKAR, "src_c", "src")

# nama tabel di sumber C -> konstanta port. `setsel(X, n)` / `show(X, n)`.
PETA = {
    "mtabmn": menu.MTABMN,
    "mtablv": menu.MTABLV,
    "menu": menu.MTABGL,
    "mtab9": menu.MTAB9,
    "mtab11": menu.MTAB11,
    "mtab12": menu.MTAB12,
    "ta1": menu.MTAB_SETUP1,
    "ta2": menu.MTAB_SETUP2,
    "t1": menu.MTAB_CREDITS[0],
    "t2": menu.MTAB_CREDITS[1],
    "t3": menu.MTAB_CREDITS[2],
    "t4": menu.MTAB_CREDITS[3],
}

gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-34s %-22s %s" % (nama, dapat if ok else "%s != %s"
                                % (dapat, harap), "OK" if ok else "GAGAL"))


def dari_sumber():
    """-> {nama: (alamat, jumlah)} dibaca dari src_c/src/*.c."""
    alamat, jumlah = {}, {}
    for f in os.listdir(SRC):
        if not f.endswith(".c"):
            continue
        s = open(os.path.join(SRC, f), encoding="utf-8", errors="replace").read()
        for nm, a in re.findall(
                r"extern\s+(?:char|struct\s+\w+)\s+(\w+)\s*\[\s*\]\s*;"
                r"\s*/\*[^*]*@0x([0-9a-fA-F]+)", s):
            alamat[nm] = int(a, 16)
        for fn, nm, n in re.findall(r"\b(setsel|show)\(\s*(\w+)\s*,\s*(\d+)\s*\)", s):
            jumlah[nm] = int(n)
    return {nm: (alamat[nm], jumlah[nm])
            for nm in set(alamat) & set(jumlah)}


def uji_silang():
    print("  alamat + jumlah entri vs src_c/src/*.c")
    src = dari_sumber()
    for nm, port in sorted(PETA.items()):
        if nm not in src:
            gagal.append("tabel '%s' tak ditemukan di sumber" % nm)
            print("  %-34s TAK ADA DI SUMBER" % nm)
            continue
        a, n = src[nm]
        cek("%s (@0x%04x, %d entri)" % (nm, a, n), tuple(port), (a, n))


def uji_dekode(misc):
    """Tiap entri harus terdekode: koordinat di layar, teksnya ASCII nyata.

    Ini yang cross-check tekstual tidak bisa lihat. Alamat yang meleset --
    walau meleset di KEDUA berkas -- akan menunjuk byte sembarang di DGROUP,
    dan gejalanya langsung: teks berisi sampah biner, atau koordinat di luar
    layar 320x200.
    """
    from cc.core import dgtab
    print("  tiap entri terdekode: koordinat di layar, untai layak")
    dg = dgtab.dgroup()
    daftar = list(PETA.items()) + [("mtabgl", menu.MTABGL)]
    for nm, (addr, n) in sorted(dict(daftar).items()):
        buruk = []
        for it in menu.tabel(addr, n):
            if not (0 <= it["x"] < 320 and 0 <= it["y"] < 200):
                buruk.append("koordinat (%d,%d)" % (it["x"], it["y"]))
            if not (0 < it["w"] <= 320 and 0 < it["h"] <= 200):
                buruk.append("ukuran %dx%d" % (it["w"], it["h"]))
            if it["teks"]:
                p = it["ptr"]
                s = bytes(dg[p:dg.index(0, p)]) if p < len(dg) else b""
                # 0x18/0x19 dan 0x80..0x83 SAH: itu glif PANAH milik font gim
                # ("Press \x19 or \x18 to move box"). Batas 0x20..0x7e sempat
                # dipakai di sini dan menjatuhkan tujuh tabel yang pikselnya
                # justru sudah terbukti -- alat ukurnya yang salah, bukan
                # datanya. Yang benar-benar menandakan alamat meleset adalah
                # byte KENDALI (<0x18); data acak di DGROUP penuh dengannya.
                if not (0 < len(s) <= 64 and all(c >= 0x18 for c in s)):
                    buruk.append("teks @0x%x bukan untai layak" % p)
        cek("%-8s @0x%04x %2d entri" % (nm, addr, n), buruk or "bersih", "bersih")


def main():
    misc = Archive(os.path.join(AKAR, "_ORIGINAL_READONLY", "MISC"))
    uji_silang()
    uji_dekode(misc)
    print("\n%s" % ("TABEL LAYAR COCOK DGN SUMBER BYTE-EXACT" if not gagal
                    else "GAGAL: %s" % ", ".join(map(str, gagal))))
    return 1 if gagal else 0


sys.exit(main())
