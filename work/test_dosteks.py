"""REGRESI TEKS DOS: baris, kolom, warna, DAN bentuk glyph — diukur di DOS.

Pesan dalam permainan ("Mechanism A does not work.") keluar lewat `printf()`
MC.LIB, yang di ujungnya memanggil `INT 21h AH=02h` satu kali per karakter
(terukur 36 panggilan untuk 36 karakter). Artinya SEMUA sifat tampilannya —
posisi, warna, dan bentuk huruf — ditentukan DOS + ROM BIOS, **bukan oleh
gim**. Tidak ada apa pun di biner gim yang bisa dibaca untuk menjawabnya;
membaca lebih teliti tidak akan menolong.

Jadi diukur di DOS sungguhan. `work/dosprobe.py` merakit program DOS puluhan
byte yang menyetel mode CGA 4, menaruh kursor, mencetak lewat jalur yang sama,
lalu MENULIS SENDIRI 16 KB memori layar ke berkas — tanpa tangkapan layar dan
tanpa interaksi, jadi bisa jalan headless di DOSBox-X.

Tiga hal diuji, makin ketat:

  1. satu huruf 'A' di (22, 0)  -> posisi dan warna
  2. font ROM hasil ekstraksi   -> dipakai port untuk pesan bergaya printf
  3. PESAN GIM yang sebenarnya  -> diadu piksel per piksel dgn render port

⚠ `port/cc/data/romfont.bin` TIDAK ikut ke git (font ROM bukan bagian dari
gim). Uji ini menjalankan `port/import_romfont.py` sendiri kalau belum ada.
"""
import os
import subprocess
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "work"))
sys.path.insert(0, os.path.join(AKAR, "port"))

import dosprobe as dp                                          # noqa: E402

from cc.core import hud, dosfont, render as rend               # noqa: E402

PESAN = "       Mechanism A does not work."
gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-40s %-12s %s" % (nama, dapat if ok else "%s != %s" % (dapat, harap),
                                "OK" if ok else "GAGAL"))


def uji_posisi_warna():
    print("  satu huruf lewat INT 21h AH=02h -- posisi dan warna")
    v = dp.jalankan("A", 22, 0)
    if v is None:
        gagal.append("PROBE tidak menghasilkan keluaran")
        return
    hit = [(x, y) for y in range(200) for x in range(320) if dp.px(v, x, y)]
    if not hit:
        gagal.append("DOS tidak mencetak apa pun")
        return
    cek("baris teks", min(y for _x, y in hit) // 8, 22)
    cek("kolom teks", min(x for x, _y in hit) // 8, 0)
    cek("y piksel == hud.PESAN_Y", min(y for _x, y in hit), hud.PESAN_Y)
    cek("x piksel == hud.PESAN_X", min(x for x, _y in hit), hud.PESAN_X)
    cek("warna teks DOS", sorted({dp.px(v, x, y) for x, y in hit}),
        [hud.PESAN_WARNA])


def uji_font():
    print("  font ROM BIOS")
    if not dosfont.tersedia():
        print("    belum diekstrak -- menjalankan port/import_romfont.py")
        subprocess.run([sys.executable,
                        os.path.join(AKAR, "port", "import_romfont.py")],
                       cwd=AKAR, stdout=subprocess.DEVNULL, timeout=300)
        dosfont._FONT[0] = None
    cek("bundel font tersedia", dosfont.tersedia(), True)
    if dosfont.tersedia():
        cek("glyph 'A' tidak kosong", any(dosfont.glyph("A")), True)
        cek("glyph ' ' kosong", any(dosfont.glyph(" ")), False)


def uji_pesan():
    print("  PESAN GIM sungguhan, diadu piksel dgn DOS")
    v = dp.jalankan(PESAN, 22, 0)
    if v is None:
        gagal.append("PROBE pesan tidak menghasilkan keluaran")
        return
    fb = rend.new_fb(0)                    # latar 0 = layar DOS kosong
    hud.gambar_pesan(rend.KanvasFB(fb), PESAN)
    beda = sum(1 for y in range(200) for x in range(320)
               if fb[y][x] != dp.px(v, x, y))
    cek("SELURUH LAYAR", 64000 - beda, 64000)


def main():
    if not dp.ada_dosbox():
        print("  DOSBox-X tidak ada di tools/ -- uji dilewati (bukan kegagalan)")
        return 0
    uji_posisi_warna()
    uji_font()
    uji_pesan()
    print("\n%s" % ("TEKS DOS COCOK: posisi, warna, DAN glyph" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


sys.exit(main())
