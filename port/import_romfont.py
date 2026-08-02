"""Ekstrak font teks 8x8 milik ROM BIOS ke bundel port (port/cc/data/romfont.bin).

Kenapa ada skrip ini
--------------------
Pesan DALAM permainan ("Mechanism A does not work.") keluar lewat `printf()`,
yaitu teks DOS -- dan DOS menggambarnya dengan **font ROM BIOS**, bukan dengan
font gim yang ada di DGROUP. Jadi untuk setia sampai piksel, port butuh font
itu juga.

Font ROM BUKAN bagian dari gim, dan repo ini tidak mendistribusikan berkas
pihak ketiga. Polanya sama dengan `import_assets.py`: yang ikut ke git adalah
PENGEKSTRAKNYA, bukan hasilnya. `port/cc/data/` sudah di-.gitignore.

Cara mengukurnya
----------------
Sebuah program DOS puluhan byte dirakit di tempat (`work/dosprobe.py`), lalu
dijalankan headless di DOSBox-X: ia menyetel mode CGA 4, mencetak karakter
ASCII 32..126 lewat DOS, dan MENULIS SENDIRI 16 KB memori layar ke berkas.
Tidak perlu tangkapan layar dan tidak perlu interaksi.

Mode 4 punya 40 kolom x 25 baris sel 8x8, jadi 95 karakter membungkus ke tiga
baris pertama. Tiap sel didekode jadi 8 byte bitmap (satu bit per piksel).

⚠ Karakter '$' tidak ikut: ia penanda akhir string untuk `INT 21h AH=09h`.
Tak satu pun teks gim memakainya, jadi ia sengaja dikosongkan.

Jalankan:  python port/import_romfont.py
"""
import os
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "work"))

import dosprobe as dp                                          # noqa: E402

AWAL, AKHIR = 32, 126
KOLOM = 40                       # mode 4: 40 kolom teks
TUJUAN = os.path.join(AKAR, "port", "cc", "data", "romfont.bin")


def ekstrak():
    teks = "".join(chr(c) if c != ord("$") else " "
                   for c in range(AWAL, AKHIR + 1))
    v = dp.jalankan(teks, 0, 0)
    if v is None:
        return None
    font = bytearray()
    for i in range(AKHIR - AWAL + 1):
        cx, cy = (i % KOLOM) * 8, (i // KOLOM) * 8
        for row in range(8):
            b = 0
            for col in range(8):
                if dp.px(v, cx + col, cy + row):
                    b |= 0x80 >> col
            font.append(b)
    return bytes(font)


def main():
    if not dp.ada_dosbox():
        print("DOSBox-X tidak ada di tools/ -- tidak bisa mengekstrak.")
        return 1
    font = ekstrak()
    if font is None:
        print("PROBE.COM tidak menghasilkan keluaran.")
        return 1
    kosong = sum(1 for i in range(0, len(font), 8)
                 if not any(font[i:i + 8]))
    os.makedirs(os.path.dirname(TUJUAN), exist_ok=True)
    open(TUJUAN, "wb").write(font)
    print("%s: %d karakter x 8 byte = %d byte (%d sel kosong: spasi dan '$')"
          % (os.path.relpath(TUJUAN, AKAR), (AKHIR - AWAL + 1), len(font), kosong))
    return 0


if __name__ == "__main__":
    sys.exit(main())
