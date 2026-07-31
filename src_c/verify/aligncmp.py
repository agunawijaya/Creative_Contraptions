"""Bandingkan .OBJ kita dengan biner asli PAKAI PENJAJARAN, bukan per posisi.

    python src_c/verify/aligncmp.py <nama> [<alamat_hex> <ukuran>]
    python src_c/verify/aligncmp.py <nama> --sbs <alamat_hex> <n> <geseran>

⚠ KENAPA ADA. Menghitung "byte cocok per POSISI" hanya sahih kalau panjang
draf sudah persis sama dengan aslinya. Begitu ada satu sisipan/kekurangan,
SELURUH sisa berkas bergeser dan byte yang sebenarnya benar terhitung salah.
`pickvar` sempat menunjukkan 368 byte cocok per posisi padahal 1.616 byte
benar-benar sejajar. Kesimpulan yang diambil dari angka posisi bisa terbalik:
satu perubahan menurunkan angka posisi 392 -> 386 TAPI menaikkan penjajaran
684 -> 704, dan yang benar adalah yang kedua.

Keluarannya juga mencetak DAFTAR GESERAN: di alamat mana panjang kita mulai
menyimpang dan sebanyak apa. Itu yang menunjuk blok mana yang harus digarap,
jauh lebih berguna daripada satu angka total.
"""
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))
TARGET = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
IMAGE_BASE = 0x200


def aligned(m, slots, orig):
    """(total_byte_sejajar, [(offset, geseran)]) — penjajaran serakah.

    Lari cocok minimal 6 byte dianggap sah; kalau putus, dicari geseran
    -24..+24 yang menyambung lagi dengan lari minimal 12 byte.
    """
    i = j = 0
    tot = 0
    shifts = []
    prev = 0
    while i < len(m) and j < len(orig):
        if m[i] == orig[j] or i in slots:
            k = 0
            while (i + k < len(m) and j + k < len(orig)
                   and (m[i + k] == orig[j + k] or (i + k) in slots)):
                k += 1
            if k >= 6:
                tot += k
                if j - i != prev:
                    shifts.append((j, j - i))
                    prev = j - i
                i += k
                j += k
                continue
        best = None
        for d in range(-24, 25):
            for a in range(1, 64):
                if i + a < len(m) and 0 <= j + a + d < len(orig):
                    k = 0
                    while (i + a + k < len(m) and j + a + d + k < len(orig)
                           and (m[i + a + k] == orig[j + a + d + k]
                                or (i + a + k) in slots)):
                        k += 1
                    if k >= 12 and (best is None or a < best[0]):
                        best = (a, d, k)
            if best:
                break
        if best:
            a, d, _ = best
            i += a
            j += a + d
        else:
            i += 1
            j += 1
    return tot, shifts


def load(name, addr, size):
    from objcode import read_omf, pick_code_segment
    segs = read_omf(os.path.join(ROOT, "src_c", "out", name + ".OBJ"))
    _, (m, slots) = pick_code_segment(segs)
    b = io_read(TARGET)
    return m, slots, b[IMAGE_BASE + addr:IMAGE_BASE + addr + size]


def io_read(p):
    with open(p, "rb") as fh:
        return fh.read()


def manifest_entry(name):
    for ln in open(os.path.join(ROOT, "src_c", "src", "manifest.txt")):
        ln = ln.split("#")[0].split()
        if len(ln) >= 3 and ln[0] == name:
            return int(ln[1], 16), int(ln[2])
    raise SystemExit("tidak ada di manifest: " + name)


def sbs(name, addr, size, a, n, sh):
    """Banding disassembly berdampingan, dengan geseran manual."""
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    m, slots, orig = load(name, addr, size)
    md = Cs(CS_ARCH_X86, CS_MODE_16)
    o = a - addr
    L = ["%04x %s %s" % (i.address, i.mnemonic, i.op_str)
         for i in md.disasm(bytes(orig[o:o + n]), a)]
    R = ["%04x %s %s" % (i.address, i.mnemonic, i.op_str)
         for i in md.disasm(bytes(m[o + sh:o + sh + n]), a + sh)]
    print("%-40s | %s" % ("ASLI", "KITA (geser %+d)" % sh))
    for k in range(max(len(L), len(R))):
        l = L[k] if k < len(L) else ""
        r = R[k] if k < len(R) else ""
        print("%-40s | %s%s" % (l, r, "" if l[5:] == r[5:] else "  <<<"))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    name = sys.argv[1]
    if "--sbs" in sys.argv:
        k = sys.argv.index("--sbs")
        addr, size = ((int(sys.argv[2], 16), int(sys.argv[3])) if k > 3
                      else manifest_entry(name))
        sbs(name, addr, size, int(sys.argv[k + 1], 16),
            int(sys.argv[k + 2]), int(sys.argv[k + 3]))
        return
    addr, size = (manifest_entry(name) if len(sys.argv) < 4
                  else (int(sys.argv[2], 16), int(sys.argv[3])))
    m, slots, orig = load(name, addr, size)
    n = min(len(m), len(orig))
    pos = sum(1 for k in range(n) if m[k] == orig[k] or k in slots)
    tot, sh = aligned(m, slots, orig)
    print("%s @0x%04x  bingkai sub sp=0x%02x" % (name, addr, m[3]))
    print("  panjang   : %d / %d  (%+d)" % (len(m), size, len(m) - size))
    print("  POSISI    : %d   <- MENYESATKAN kalau panjang belum pas" % pos)
    print("  TERJAJAR  : %d / %d  (%.1f%%)" % (tot, size, 100.0 * tot / size))
    print("  geseran   : %s" % ", ".join("0x%04x:%+d" % (addr + o, d)
                                         for o, d in sh))


if __name__ == "__main__":
    main()
