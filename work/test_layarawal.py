"""REGRESI LAYAR PEMBUKA & INSTRUKSI: diadu piksel dgn VRAM gim asli.

Tujuh layar yang selama ini HANYA punya bukti tidak langsung. Semuanya
digambar `setsel()` @0x3769 atau `show()` @0x381A dari tabel DGROUP:

    credits tahap 0, 1, 2, 3   setsel(t1,2) / show(t2,2) / show(t3,2) / show(t4,1)
    askopts pertanyaan 1       setsel(ta1, 3)
    askopts pertanyaan 2       show(ta2, 2)  -- ditumpuk di atas pertanyaan 1
    instruksi Fill in Mech     menu9()  @0x30BB -> setsel(mtab9, 9)
    instruksi Fill in Zany     menu11() @0x30E0 -> setsel(mtab11, 11)
    instruksi Contraption Mix  menu12() @0x3105 -> setsel(mtab12, 12)

Kenapa dulu "tidak bisa ditangkap" -- tiga sebab, semuanya HARNESS SENDIRI
---------------------------------------------------------------------------
1. `menu9()` @0x30BB DI-STUB TANPA SYARAT di `work/emu.py`, jadi layar
   instruksi Fill in Mechanisms memang tidak pernah digambar. Padanannya
   `menu11()`/`menu12()` tidak pernah di-hook sama sekali -- keduanya sudah
   menggambar sendiri sejak dulu, tinggal ditangkap. Sekarang 0x30BB ikut
   patuh pada `CC_NOMENUSTUB`.

2. `credits()`/`askopts()` di-stub, dan melepasnya (`CC_NOSTARTSTUB=1`) saja
   tidak cukup: keduanya menunggu di `while (keyhit() == 0);`. Memaksa
   `keyhit()` selalu mengembalikan ENTER membuat `kbflush()` @0x36EF --
   `while (keyhit() != 0) { ...; getkey(); }` -- menguras antrean yang TAK
   PERNAH HABIS. Itulah "emulator menggantung sesudah layar credits" yang
   terbaca enam kali.

3. Dgn antrean berhingga pun `kbflush()` MEMAKAN satu tombol (terukur:
   hilang di `ret=0x3707`), seluruh urutan bergeser satu, dan `credits()`
   lalu menolak 'Y' sampai antrean habis. Jawabannya sudah ada di berkas
   yang sama, di jalur OBSERVE: LIHAT SIAPA PEMANGGILNYA. Dari dalam
   `kbflush`, `keyhit()` harus bilang "buffer kosong".

4. Pertanyaan KEDUA `askopts` butuh satu lapis lagi. `tone2()` di depannya
   memanggil `delay(5)` @0x2692, dan `delay()` gelung sibuk MURNI pada
   `ticks` -- tanpa `vbwait()`, jadi CC_SNDISR pun tak menolong. Men-stub-nya
   dengan `force_ret_near()` di alamat MASUK justru GAGAL DIAM-DIAM: terukur
   dgn `CC_DBGSP`, puncak tumpukan di 0x2692 berisi **0x0005** -- ARGUMEN
   `delay(5)`, bukan alamat balik -- jadi ia melompat ke IP=5, mengembara,
   dan muncul lagi di `main_`. Gejalanya persis seperti bug alur gim:
   "askopts kembali ke awal". Yang benar tidak menyentuh tumpukan sama
   sekali: nol-kan `ticks` di UJI GELUNGNYA (0x26A2) dan biarkan `delay()`
   keluar sendiri.

⚠ ALAT UKUR PUN BISA BERBOHONG: penyelidik `CC_DBGSP` mula-mula didaftarkan
SESUDAH `hook_waitn` pada alamat yang sama, jadi yang terbaca keadaan
SESUDAH force_ret_near -- SP dua byte terlalu tinggi dan puncaknya nilai
basi. Bacaan itu "mustahil" dan sempat menyesatkan. Ia kini didaftarkan di
depan.
"""
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import menu                                       # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
TOMBOL = ",".join(["0d"] * 10)
gagal = []

# nama, argumen emu.py, env tambahan, alamat tangkap, layar yang DIHARAPKAN
KASUS = [
    ("credits bertahap", ("1", "2"),
     dict(OBSERVE="fillmech", CC_NOSTARTSTUB="1", CC_NOWAIT="1",
          CC_OBSKEYS="0d,0d,59,59,0d,0d"),
     "3885", ["credits1", "credits2", "credits3"]),
    ("credits tahap 0 + askopts q1", ("1", "2"),
     dict(OBSERVE="fillmech", CC_NOSTARTSTUB="1", CC_NOWAIT="1",
          CC_OBSKEYS="0d,0d,59,59,0d,0d"),
     "3819", ["credits0", "setup"]),
    ("askopts q2 (show ta2)", ("1", "2"),
     dict(OBSERVE="fillmech", CC_NOSTARTSTUB="1", CC_NOWAIT="1",
          CC_OBSKEYS="0d,0d,59,59,0d,0d"),
     "36ef", ["credits3", "setup", "setup2"]),
    ("instruksi Fill in Mechanisms", ("1", "2"),
     dict(OBSERVE="fillmech", CC_NOSKIP="1", CC_OBSKEYS=TOMBOL),
     "3819", ["level", "goal", "instruksi_mech"]),
    ("instruksi Fill in Zany", ("1", "3"),
     dict(OBSERVE="zany", CC_NOSKIP="1", CC_OBSKEYS=TOMBOL),
     "3819", ["level", "goal", "instruksi_zany"]),
    ("instruksi Contraption Mix Up", ("1", "4"),
     dict(OBSERVE="mixup", CC_NOSKIP="1", CC_OBSKEYS=TOMBOL),
     "3819", ["level", "instruksi_mixup"]),
]


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def kandidat(misc):
    k = {n: menu.layar(misc, n)[0] for n in
         ("utama", "level", "goal", "setup", "instruksi_mech",
          "instruksi_zany", "instruksi_mixup")}
    for i in range(len(menu.MTAB_CREDITS)):
        k["credits%d" % i] = menu.tumpuk(misc, menu.MTAB_CREDITS, sampai=i)
    k["setup2"] = menu.tumpuk(misc, (menu.MTAB_SETUP1, menu.MTAB_SETUP2))
    return k


def tangkap(folder, nama, argv, env_extra, off, batas):
    seq = os.path.join(folder, nama.replace(" ", "_"))
    if os.path.isdir(seq) and glob.glob(os.path.join(seq, "*.png")):
        return seq
    print("  [emu] menangkap %s ..." % nama)
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out_" + nama.replace(" ", "_")),
               CC_NOMENUSTUB="1", CC_MAXINSN="400000000",
               CC_VRAMSEQ="%s=%s:%d" % (off, seq, batas))
    env.update(env_extra)
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py")]
                   + list(argv), env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def main(folder):
    misc = Archive(os.path.join(AKAR, "_ORIGINAL_READONLY", "MISC"))
    kand = kandidat(misc)
    terbukti = set()
    for nama, argv, env_extra, off, harap in KASUS:
        seq = tangkap(folder, nama, argv, env_extra, off, len(harap))
        fs = sorted(glob.glob(os.path.join(seq, "*.png")))
        print("  %s: %d tangkapan" % (nama, len(fs)))
        # Cocokkan tiap tangkapan ke kandidat TERDEKAT, lalu tuntut nol beda.
        # Mencocokkan by-urutan TIDAK dipakai: jumlah panggilan bisa berubah
        # kalau alur navigasi berubah, dan itu akan menyamarkan kegagalan
        # sebagai "urutan bergeser".
        for f in fs:
            ref = muat(f)
            nm, beda = min(((n, sum(1 for y in range(200) for x in range(320)
                                    if fb[y][x] != ref[y][x]))
                            for n, fb in kand.items()), key=lambda t: t[1])
            tanda = "OK" if beda == 0 else "GAGAL"
            if beda:
                gagal.append("%s/%s" % (nama, os.path.basename(f)))
            else:
                terbukti.add(nm)
            print("    %-14s -> %-16s %6d/64000 %s"
                  % (os.path.basename(f), nm, 64000 - beda, tanda))
        for h in harap:
            if h not in terbukti:
                gagal.append("%s: layar '%s' tidak muncul" % (nama, h))

    print("\n  layar terbukti identik: %s" % ", ".join(sorted(terbukti)))
    print("%s" % ("LAYAR PEMBUKA & INSTRUKSI IDENTIK DENGAN GAME ASLI"
                  if not gagal else "GAGAL: %s" % ", ".join(map(str, gagal))))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "awalseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
