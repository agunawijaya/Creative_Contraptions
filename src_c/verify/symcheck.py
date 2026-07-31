"""Verifikasi IDENTITAS SIMBOL — menutup lubang terbesar di objcode.py.

objcode.py memperlakukan slot relokasi sebagai WILDCARD: target `call` dan
alamat global tidak ikut dibandingkan. Akibatnya sebuah fungsi bisa dilaporkan
"COCOK BYTE-PER-BYTE" padahal memanggil fungsi yang SALAH, asalkan jumlah dan
urutan argumennya kebetulan sama. Itu bukan kekhawatiran teoretis: bug `put()`
(0x6524 vs 0x65e0) lolos persis lewat lubang ini.

Cara kerja alat ini:
  1. Panen peta nama->alamat dari manifest.txt (fungsi yang sudah
     direkonstruksi) dan dari komentar `nama()=ADDR` / `@0xNNN` di src/*.c.
  2. Untuk tiap .OBJ, baca EXTDEF (daftar nama eksternal) dan FIXUPP.
  3. Untuk tiap fixup, baca BINER ASLI di posisi yang sama dan hitung alamat
     yang SEBENARNYA dituju:
        - self-relative (bit M=0, dipakai `call`): addr + off + 2 + disp
        - segment-relative (M=1, referensi DGROUP): nilai kata apa adanya
  4. Bandingkan dengan alamat yang kita KLAIM untuk simbol itu.

Keluaran: tiap ketidakcocokan = fungsi kita memanggil/membaca simbol yang
berbeda dari biner asli, walaupun objcode.py bilang cocok.

    python src_c/verify/symcheck.py
"""
import glob
import io
import os
import re
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "src_c", "src")
OUT = os.path.join(ROOT, "src_c", "out")
TARGET = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
IMAGE_BASE = 0x200


def manifest():
    """nama_berkas -> (alamat, ukuran) untuk fungsi yang sudah direkonstruksi."""
    out = {}
    for ln in io.open(os.path.join(SRC, "manifest.txt"), encoding="utf-8"):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        p = ln.split()
        if len(p) >= 3:
            out[p[0]] = (int(p[1], 16), int(p[2]))
    return out


def symbol_map(man):
    """nama_simbol -> alamat yang KITA klaim.

    Sumber: (a) manifest — nama berkas = nama fungsi untuk yang direkonstruksi;
    (b) komentar `nama()=ADDR` atau `nama() = FUN_1000_ADDR` di src/*.c;
    (c) komentar `@0xNNN` pada deklarasi extern (variabel DGROUP).
    """
    sym = {}
    for name, (addr, _) in man.items():
        sym[name] = ("code", addr)
    # ⚠ Nama BERKAS != nama SIMBOL. Satu modul assembly bisa memuat beberapa
    # fungsi, dan yang bernama sama dengan berkasnya belum tentu ada di offset
    # 0 (mis. modul `text` mulai 0x644a tapi simbol `text` ada di 0x6453 --
    # 0x644a itu pembungkus INT 10h yang lain). Kalau ini dilewatkan, symcheck
    # melaporkan 18 BEDA palsu. Alamat sebenarnya diambil dari PUBDEF .OBJ.
    for name, (addr, _) in man.items():
        p = os.path.join(OUT, name + ".OBJ")
        if not os.path.exists(p):
            continue
        for pub, off in read_pubdefs(p):
            # MASM 1.27 memancarkan nama publik dalam HURUF BESAR; berkas .c
            # memakai huruf kecil. LINK memadankannya tanpa peduli besar-kecil,
            # jadi symcheck harus begitu juga -- kalau tidak, entri manifest
            # yang salah tetap menang dan BEDA palsunya bertahan.
            sym[pub] = ("code", addr + off)
            sym[pub.lower()] = ("code", addr + off)
    pat_fn = re.compile(r"(\w+)\(\)\s*=\s*(?:FUN_1000_)?0?x?([0-9a-fA-F]{4})\b")
    pat_var = re.compile(
        r"extern\s+[\w\s*]*?(\w+)\s*(?:\[\s*\])?\s*;[^\n]*?@0x([0-9a-fA-F]{2,4})")
    for f in sorted(glob.glob(os.path.join(SRC, "*.c"))):
        s = io.open(f, encoding="utf-8", errors="replace").read()
        for m in pat_fn.finditer(s):
            sym.setdefault(m.group(1), ("code", int(m.group(2), 16)))
        for m in pat_var.finditer(s):
            sym.setdefault(m.group(1), ("data", int(m.group(2), 16)))
    return sym


def read_pubdefs(path):
    """[(nama_publik, offset_dalam_segmen)] dari rekaman PUBDEF (0x90)."""
    b = io.open(path, "rb").read()
    out, i = [], 0
    while i + 3 <= len(b):
        rlen = struct.unpack_from("<H", b, i + 1)[0]
        if b[i] == 0x90:
            body = b[i + 3:i + 3 + rlen - 1]
            j, gi = _idx(body, 0)
            j, si = _idx(body, j)
            if gi == 0 and si == 0:         # BASE FRAME hadir hanya bila keduanya 0
                j += 2
            while j + 3 <= len(body):
                n = body[j]
                nm = body[j + 1:j + 1 + n].decode("ascii", "replace")
                j += 1 + n
                if j + 2 > len(body):
                    break
                out.append((nm, struct.unpack_from("<H", body, j)[0]))
                j += 2
                j, _ = _idx(body, j)
        i += 3 + rlen
    return out


def _idx(body, j):
    return (j + 2, ((body[j] & 0x7F) << 8) | body[j + 1]) if (body[j] & 0x80) \
        else (j + 1, body[j])


def read_obj(path):
    """Kembalikan (extdefs, fixups) — fixups: (offset_dlm_segmen, M, nama)."""
    b = io.open(path, "rb").read()
    ext, fixups, last = [], [], 0
    i = 0
    while i + 3 <= len(b):
        rtype = b[i]
        rlen = struct.unpack_from("<H", b, i + 1)[0]
        body = b[i + 3:i + 3 + rlen - 1]
        if rtype == 0x8C:                                   # EXTDEF
            j = 0
            while j < len(body):
                n = body[j]
                ext.append(body[j + 1:j + 1 + n].decode("ascii", "replace"))
                j += 1 + n
                j, _ = _idx(body, j)
        elif rtype == 0xA0 and len(body) >= 3:              # LEDATA
            last = struct.unpack_from("<H", body, 1)[0]
        elif rtype == 0x9C:                                 # FIXUPP
            j = 0
            while j < len(body):
                b0 = body[j]
                if not (b0 & 0x80):                         # THREAD
                    j += 1
                    if (b0 & 0x08) == 0:
                        j, _ = _idx(body, j)
                    continue
                if j + 2 >= len(body):
                    break
                locat = (b0 << 8) | body[j + 1]
                off = locat & 0x03FF
                mbit = (locat >> 14) & 1
                j += 2
                fixdat = body[j]
                j += 1
                F = (fixdat >> 7) & 1
                T = (fixdat >> 3) & 1
                P = (fixdat >> 2) & 1
                targt = fixdat & 3
                if F == 0:
                    j, _ = _idx(body, j)
                name = None
                if T == 0:
                    j, datum = _idx(body, j)
                    if targt == 2 and 1 <= datum <= len(ext):
                        name = ext[datum - 1]
                if P == 0:
                    j += 2
                fixups.append((last + off, mbit, name))
        i += 3 + rlen - 1 + 1
    return ext, fixups


def matches(name, addr, size, tgt):
    """True kalau kode kita cocok byte-per-byte (di luar slot relokasi).

    WAJIB disaring: untuk fungsi yang BELUM cocok, offset kita tidak sejajar
    dengan biner asli sehingga pembacaan di alamat yang sama menghasilkan
    sampah -- dan sampah itu akan dilaporkan sebagai 'beda simbol' palsu.
    """
    sys.path.insert(0, os.path.dirname(__file__))
    from objcode import read_omf, pick_code_segment
    obj = os.path.join(OUT, name + ".OBJ")
    segs = read_omf(obj)
    _, (code, slots) = pick_code_segment(segs)
    if len(code) != size:
        return False
    for k in range(size):
        if k in slots:
            continue
        if code[k] != tgt[IMAGE_BASE + addr + k]:
            return False
    return True


def main():
    man = manifest()
    sym = symbol_map(man)
    tgt = io.open(TARGET, "rb").read()
    bad = unknown = checked = indexed = 0
    skipped = []
    byaddr = {}
    for n2, (k2, a2) in sym.items():
        byaddr.setdefault(a2, n2)
    addr_set = set(byaddr)
    for name in sorted(man):
        addr, size = man[name]
        obj = os.path.join(OUT, name + ".OBJ")
        if not os.path.exists(obj):
            continue
        if not matches(name, addr, size, tgt):
            skipped.append(name)
            continue
        _, fixups = read_obj(obj)
        for off, mbit, sname in fixups:
            if sname is None or off + 2 > size:
                continue
            raw = struct.unpack_from("<H", tgt, IMAGE_BASE + addr + off)[0]
            if sname not in sym:
                unknown += 1
                continue
            kind, claim = sym[sname]
            actual = ((addr + off + 2 + raw) & 0xFFFF) if mbit == 0 else raw
            checked += 1
            if actual == claim:
                continue
            # Bedakan KESALAHAN dari akses ber-INDEKS. `tab[2].y` menghasilkan
            # fixup atas simbol `tab` tapi nilainya basis+offset. Kalau nilai
            # sebenarnya TIDAK sama dengan alamat simbol lain mana pun, itu
            # hampir pasti indeks -- bukan simbol yang salah.
            if mbit == 1 and actual not in addr_set and actual > claim                     and actual - claim < 0x400:
                indexed += 1
                continue
            bad += 1
            other = byaddr.get(actual, "?")
            print("BEDA  %-9s +%-4d %-10s kita=%s(0x%04x)  asli=0x%04x=%s  (%s)"
                  % (name, off, sname, sname, claim, actual, other,
                     "call" if mbit == 0 else "data"))
    print()
    print("slot dicek : %d" % checked)
    print("TIDAK cocok: %d" % bad)
    print("akses ber-INDEKS (basis+offset, bukan kesalahan): %d" % indexed)
    print("nama tanpa alamat terdokumentasi (dilewati): %d" % unknown)
    if skipped:
        print("fungsi DILEWATI (byte-nya belum cocok, offset tak sejajar): %s"
              % ", ".join(skipped))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
