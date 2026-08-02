"""REGRESI PEMBUKA animvm(): jam pasir + bilah bola, diadu piksel dgn gim.

`animvm()` @0x18db tidak langsung menggambar bola. Ia membuka dengan dua gelung
di PITA ATAS: jam pasir berkedip, lalu bilah 16x8 meluncur dari x=0x78 ke posisi
`goal * 10`. Keadaan AKHIR-nya sudah lama terbukti identik (animasi
1.210/1.210), tapi PERALIHANNYA belum pernah diadu -- port melompatinya.

Kenapa baru sekarang bisa diukur
--------------------------------
Dua cacat di HARNESS SENDIRI, bukan di gim, dan keduanya menyembunyikan intro:

  1. `ticks` @0x2e4 dihitung mundur ISR timer, dan emulator tidak menjalankan
     interupsi. Jadi gelung jam pasir tak pernah selesai. `CC_NOWAIT=1` selama
     ini "menyelesaikannya" dengan MELEWATI gelungnya -- yang berarti intronya
     memang tidak pernah dijalankan sekali pun.
  2. `CC_SNDISR=1` memasang ISR sungguhan (`sndisr` @0x670E memang
     mengurangi `ticks`), tapi pelepas penjaganya terdaftar di 0x5D98 --
     alamat yang SAMA dengan pemicunya. Penjaganya lepas pada instruksi yang
     sama saat dipasang, jadi `IRET` yang kembali ke 0x5D98 memicu ISR lagi,
     selamanya. Sekarang pelepasnya di `vbend` @0x5DA1.

Sesudah keduanya beres, intronya langsung terlihat: `keyhit()` @0x1791
dipanggil di UJUNG kedua gelung, jadi tangkapan di sana memperlihatkan keadaan
SESUDAH tiap gambar -- 2 bingkai jam pasir, 56 langkah bilah.

Yang dibandingkan PITA ATAS (320x8 = 2.560 piksel per bingkai): itu satu-satunya
bagian layar yang disentuh intro. Keadaan awalnya dibangun port sendiri lewat
`setupscr()`, yang pikselnya sudah terbukti sebagai bagian layar attract.
"""
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import adegan, render as rend                     # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
PITA = 8                        # tinggi pita atas
gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-34s %9s/%-9s %s" % (nama, dapat, harap, "OK" if ok else "GAGAL"))


def tangkap(folder):
    seq = os.path.join(folder, "intro")
    if os.path.isdir(seq) and glob.glob(os.path.join(seq, "*.png")):
        return seq
    print("  [emu] menangkap pembuka animvm ...")
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out"), CC_SNDISR="1",
               CC_MAXINSN="500000000", CC_VRAMSEQ="1791=%s:120" % seq)
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    "1", "1"], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def pita(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(PITA)]


def main(folder):
    seq = tangkap(folder)
    fs = sorted(glob.glob(os.path.join(seq, "*.png")))
    if not fs:
        print("  emulator tidak menghasilkan tangkapan")
        return 1
    ref = [pita(f) for f in fs]

    # Berapa bola: DIUKUR dari panjang luncuran, bukan ditebak. Bilah berhenti
    # di x = nbola * 10 dan bergeser 2 piksel per bingkai dari 0x78, jadi tepi
    # KIRI daerah yang berubah pun mundur 2 piksel tiap kali. Itu tanda yang
    # tidak bisa tertukar dengan bingkai `shftr` sesudahnya.
    #
    # ⚠ Dua detektor yang lebih sederhana KELIRU, dan keduanya sempat dipakai:
    #   - "sampai perubahan berhenti di sebelah kiri 0x78" -- `shftr` juga
    #     menyentuh x kecil, jadi kelebihan satu langkah dan bolanya jadi 0;
    #   - tepi KANAN -- `fillrect(i+0x10, .., i+0x11, ..)` menyapu jejak di
    #     kanan sprite, jadi tepi kanan DIAM dua bingkai pertama dan
    #     luncurannya terbaca cuma 1 langkah.
    def beda_x(i):
        return [x for y in range(PITA) for x in range(320)
                if ref[i][y][x] != ref[i - 1][y][x]]

    langkah, kanan = 0, None   # `kanan` = tepi kiri bingkai sebelumnya
    for i in range(2, len(ref)):
        b = beda_x(i)
        if not b or (kanan is not None and min(b) != kanan - 2):
            break
        langkah, kanan = langkah + 1, min(b)
    nbola = (adegan.BILAH_AWAL - 2 * (langkah - 1)) // 10
    print("  gim: %d langkah bilah -> %d bola (x akhir %d)"
          % (langkah, nbola, nbola * 10))

    misc = Archive(os.path.join(AKAR, "_ORIGINAL_READONLY", "MISC"))
    fb = rend.new_fb()
    rend.setupscr(fb, 1, nbola=nbola, misc=misc)
    k = rend.KanvasFB(fb)

    n = 0
    cocok = 0
    for i, _ in enumerate(adegan.intro(k, misc, nbola)):
        if i >= len(ref):
            break
        n += 1
        cocok += sum(1 for y in range(PITA) for x in range(320)
                     if fb[y][x] == ref[i][y][x])
    cek("bingkai pembuka", n, langkah + 3)          # 2 jam pasir + N + penutup
    cek("piksel pita atas", cocok, n * 320 * PITA)

    print("\n%s" % ("PEMBUKA animvm IDENTIK DENGAN GIM" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "introseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
