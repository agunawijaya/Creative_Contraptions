"""Alat: cetak sebuah string lewat DOS di mode CGA 4, lalu buang VRAM-nya.

Dipakai untuk mengukur hal-hal yang TIDAK ADA di biner gim karena ditentukan
sistem: posisi, warna, dan bentuk glyph teks yang dikeluarkan `printf()`.

Caranya menghindari dua kesulitan sekaligus:
  * tidak perlu tangkapan layar -- programnya sendiri yang menulis 16 KB
    memori layar ke berkas, jadi bisa jalan headless;
  * tidak perlu interaksi -- DOSBox-X dijalankan lewat `[autoexec]` lalu
    `exit`, pola yang sama dengan `src_c/build/buildall.ps1`.

`.COM`-nya dirakit tangan di sini; tiap instruksi berkomentar. Panjangnya
puluhan byte, jadi merakitnya sendiri jauh lebih murah daripada menyeret MASM
ke dalam alur ini.
"""
import os
import subprocess

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSBOX = os.path.join(AKAR, "tools", "dosbox-x", "bin", "x64", "Release",
                      "dosbox-x.exe")
KERJA = os.path.join(AKAR, "work", "dostest")


def ada_dosbox():
    return os.path.exists(DOSBOX)


def buat_com(teks, baris, kolom):
    """-> byte .COM yang mencetak `teks` di (baris, kolom) lalu buang VRAM."""
    # Rangka kode; alamat string diisi belakangan (panjangnya tetap).
    kode = bytearray()
    kode += bytes([0xB8, 0x04, 0x00])          # mov ax,0004h  mode 4
    kode += bytes([0xCD, 0x10])                # int 10h
    kode += bytes([0xB4, 0x02])                # mov ah,02h    set kursor
    kode += bytes([0x30, 0xFF])                # xor bh,bh
    kode += bytes([0xBA, kolom & 0xFF, baris & 0xFF])   # mov dx,(baris<<8)|kolom
    kode += bytes([0xCD, 0x10])                # int 10h
    kode += bytes([0xB4, 0x09])                # mov ah,09h    cetak string '$'
    p_str = len(kode) + 1                      # tempat operan alamat string
    kode += bytes([0xBA, 0x00, 0x00])
    kode += bytes([0xCD, 0x21])                # int 21h
    kode += bytes([0xB4, 0x3C])                # mov ah,3Ch    buat berkas
    kode += bytes([0x31, 0xC9])                # xor cx,cx
    p_nama = len(kode) + 1
    kode += bytes([0xBA, 0x00, 0x00])
    kode += bytes([0xCD, 0x21])                # int 21h
    kode += bytes([0x89, 0xC3])                # mov bx,ax     handle
    kode += bytes([0x1E])                      # push ds
    kode += bytes([0xB8, 0x00, 0xB8])          # mov ax,0B800h
    kode += bytes([0x8E, 0xD8])                # mov ds,ax     DS = VRAM
    kode += bytes([0x31, 0xD2])                # xor dx,dx
    kode += bytes([0xB9, 0x00, 0x40])          # mov cx,4000h  16 KB
    kode += bytes([0xB4, 0x40])                # mov ah,40h    tulis
    kode += bytes([0xCD, 0x21])                # int 21h
    kode += bytes([0x1F])                      # pop ds
    kode += bytes([0xB4, 0x3E])                # mov ah,3Eh    tutup
    kode += bytes([0xCD, 0x21])                # int 21h
    kode += bytes([0xB8, 0x03, 0x00])          # mov ax,0003h  balik mode teks
    kode += bytes([0xCD, 0x10])                # int 10h
    kode += bytes([0xB8, 0x00, 0x4C])          # mov ax,4C00h  keluar
    kode += bytes([0xCD, 0x21])                # int 21h

    data = teks.encode("latin-1") + b"$"
    off_str = 0x100 + len(kode)
    off_nama = off_str + len(data)
    kode[p_str:p_str + 2] = off_str.to_bytes(2, "little")
    kode[p_nama:p_nama + 2] = off_nama.to_bytes(2, "little")
    return bytes(kode) + data + b"OUT.BIN\0"


def jalankan(teks, baris=0, kolom=0, timeout=180):
    """Cetak `teks` di DOS lalu -> 16 KB isi VRAM (atau None kalau gagal)."""
    if not ada_dosbox():
        return None
    os.makedirs(KERJA, exist_ok=True)
    open(os.path.join(KERJA, "PROBE.COM"), "wb").write(
        buat_com(teks, baris, kolom))
    hasil = os.path.join(KERJA, "OUT.BIN")
    if os.path.exists(hasil):
        os.remove(hasil)
    conf = os.path.join(KERJA, "probe.conf")
    open(conf, "w").write(
        "[dosbox]\nmachine=cga\n[cpu]\ncputype=386\ncycles=fixed 30000\n"
        "[autoexec]\nmount x \"%s\"\nx:\nPROBE.COM\nexit\n" % KERJA)
    subprocess.run([DOSBOX, "-conf", conf], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=timeout)
    if not os.path.exists(hasil):
        return None
    return open(hasil, "rb").read()


def px(v, x, y):
    """Piksel CGA mode 4: baris genap di bank 0, ganjil di bank 0x2000."""
    off = (y & 1) * 0x2000 + (y >> 1) * 80 + (x >> 2)
    return (v[off] >> (6 - 2 * (x & 3))) & 3
