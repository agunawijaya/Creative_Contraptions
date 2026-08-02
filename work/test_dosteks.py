"""REGRESI: baris DAN warna teks DOS, diukur di DOS SUNGGUHAN.

Pesan dalam permainan ("Mechanism %c does not work.") keluar lewat `printf()`
MC.LIB, yang di jalur akhirnya memanggil `INT 21h AH=02h` satu kali per
karakter — terukur 36 panggilan untuk 36 karakter. Artinya ATRIBUT WARNANYA
dipilih driver konsol DOS, **bukan oleh gim**: tidak ada apa pun di biner gim
yang bisa dibaca untuk menjawabnya.

Karena itu satu-satunya cara mengukurnya adalah menjalankan DOS sungguhan.
Uji ini merakit program 69 byte (`PROBE.COM`) yang:

    mode 4  ->  set kursor (baris 22, kolom 0)  ->  INT 21h AH=02h cetak 'A'
            ->  tulis SELURUH VRAM (16 KB) ke berkas  ->  keluar

lalu menjalankannya di DOSBox-X lewat `[autoexec]` dan MEMBACA berkasnya.
Tidak perlu tangkapan layar, tidak perlu interaksi — jadi bisa jalan headless.

Hasil yang diharapkan, dan ketiganya sudah terukur:
    posisi  x = 0, y = 176   (= baris teks 22, kolom 0)
    warna   3
Posisi itu KONFIRMASI INDEPENDEN atas angka yang dihitung dari panggilan
kursor gim sendiri (`f66fd(0x16, 0)`, terekam 11 kali lewat INT 10h AH=02h).

⚠ Bentuk glyph-nya berbeda dari yang digambar port: DOS memakai font ROM BIOS,
port memakai font gim. Font ROM bukan bagian dari gim dan tidak ikut
didistribusikan.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from cc.core import hud                                        # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSBOX = os.path.join(AKAR, "tools", "dosbox-x", "bin", "x64", "Release",
                      "dosbox-x.exe")
KERJA = os.path.join(AKAR, "work", "dostest")

# PROBE.COM dirakit tangan; tiap baris satu instruksi.
KODE = bytes([
    0xB8, 0x04, 0x00,        # mov ax,0004h   mode 4 = CGA 320x200 4 warna
    0xCD, 0x10,              # int 10h
    0xB4, 0x02,              # mov ah,02h     set posisi kursor
    0x30, 0xFF,              # xor bh,bh      halaman 0
    0xBA, 0x00, 0x16,        # mov dx,1600h   DH=22 baris, DL=0 kolom
    0xCD, 0x10,              # int 10h
    0xB4, 0x02,              # mov ah,02h     DOS: cetak satu karakter
    0xB2, 0x41,              # mov dl,'A'
    0xCD, 0x21,              # int 21h        <- jalur yang SAMA dgn printf gim
    0xB4, 0x3C,              # mov ah,3Ch     buat berkas
    0x31, 0xC9,              # xor cx,cx
    0xBA, 0x3D, 0x01,        # mov dx,offset nama
    0xCD, 0x21,              # int 21h
    0x89, 0xC3,              # mov bx,ax      handle
    0x1E,                    # push ds
    0xB8, 0x00, 0xB8,        # mov ax,0B800h
    0x8E, 0xD8,              # mov ds,ax      DS = VRAM
    0x31, 0xD2,              # xor dx,dx
    0xB9, 0x00, 0x40,        # mov cx,4000h   16 KB
    0xB4, 0x40,              # mov ah,40h     tulis ke handle
    0xCD, 0x21,              # int 21h
    0x1F,                    # pop ds
    0xB4, 0x3E,              # mov ah,3Eh     tutup
    0xCD, 0x21,              # int 21h
    0xB8, 0x03, 0x00,        # mov ax,0003h   balik ke mode teks
    0xCD, 0x10,              # int 10h
    0xB8, 0x00, 0x4C,        # mov ax,4C00h   keluar
    0xCD, 0x21,              # int 21h
]) + b"OUT.BIN\0"

gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-38s %-12s %s" % (nama, dapat if ok else "%s != %s" % (dapat, harap),
                                "OK" if ok else "GAGAL"))


def px(v, x, y):
    """Piksel CGA mode 4: baris genap di bank 0, ganjil di bank 0x2000."""
    off = (y & 1) * 0x2000 + (y >> 1) * 80 + (x >> 2)
    return (v[off] >> (6 - 2 * (x & 3))) & 3


def main():
    if not os.path.exists(DOSBOX):
        print("  DOSBox-X tidak ada di tools/ -- uji dilewati (bukan kegagalan)")
        return 0
    os.makedirs(KERJA, exist_ok=True)
    # offset nama berkas harus jatuh tepat di 0x13d
    assert len(KODE) - 8 + 0x100 == 0x13D, hex(len(KODE) - 8 + 0x100)
    open(os.path.join(KERJA, "PROBE.COM"), "wb").write(KODE)
    hasil = os.path.join(KERJA, "OUT.BIN")
    if os.path.exists(hasil):
        os.remove(hasil)
    conf = os.path.join(KERJA, "probe.conf")
    open(conf, "w").write(
        "[dosbox]\nmachine=cga\n[cpu]\ncputype=386\ncycles=fixed 30000\n"
        "[autoexec]\nmount x \"%s\"\nx:\nPROBE.COM\nexit\n" % KERJA)
    subprocess.run([DOSBOX, "-conf", conf], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=180)
    if not os.path.exists(hasil):
        print("  PROBE.COM tidak menghasilkan OUT.BIN")
        return 1
    v = open(hasil, "rb").read()
    hit = [(x, y) for y in range(200) for x in range(320) if px(v, x, y) != 0]
    if not hit:
        print("  tidak ada piksel tergambar -- DOS tidak mencetak apa pun")
        return 1
    warna = {px(v, x, y) for x, y in hit}
    cek("baris teks glyph", min(y for _x, y in hit) // 8, 22)
    cek("kolom teks glyph", min(x for x, _y in hit) // 8, 0)
    cek("y piksel == hud.PESAN_Y", min(y for _x, y in hit), hud.PESAN_Y)
    cek("x piksel == hud.PESAN_X", min(x for x, _y in hit), hud.PESAN_X)
    cek("warna teks DOS", sorted(warna), [hud.PESAN_WARNA])
    print("\n%s" % ("BARIS DAN WARNA TEKS DOS COCOK" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


sys.exit(main())
