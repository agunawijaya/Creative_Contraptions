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
import difflib
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))
TARGET = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
IMAGE_BASE = 0x200


def align_runs(m, slots, orig):
    """[(offset_kita, offset_asli, panjang)] untuk tiap lari yang sejajar.

    Dipakai fixorder.py untuk memetakan offset FIXUPP kita ke offset biner asli
    walau fungsinya BELUM cocok byte-per-byte.
    """
    runs = []
    i = j = 0
    while i < len(m) and j < len(orig):
        if m[i] == orig[j] or i in slots:
            k = 0
            while (i + k < len(m) and j + k < len(orig)
                   and (m[i + k] == orig[j + k] or (i + k) in slots)):
                k += 1
            if k >= 6:
                runs.append((i, j, k))
                i += k
                j += k
                continue
        best = None
        for d in sorted(range(-24, 25), key=lambda v: (abs(v), v)):
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
    return runs


def global_aligned(m, slots, orig):
    """Byte cocok di bawah penjajaran GLOBAL (difflib), bukan pemindaian serakah.

    ⚠ KENAPA ADA. `aligned()` di bawah memakai jendela geseran ±24 dan lari
    minimal 6/12 byte. Kalau pola divergensinya BERUBAH, ia bisa gagal
    menyambung dan MELAPORKAN TURUN padahal kodenya membaik. Terjadi nyata di
    `pickvar` (2026-07-31): satu perubahan menurunkan angka serakah 1.616 ->
    1.583 TAPI menaikkan penjajaran global 1.631 -> 1.654 dan POSISI 368 ->
    1.333. Yang benar yang global.

    Pakai angka GLOBAL untuk memutuskan; angka serakah cuma untuk daftar
    geserannya, yang tetap berguna menunjuk LETAK masalah.
    """
    mm = bytearray(m)
    for k in slots:                     # slot relokasi = wildcard
        if k < len(mm) and k < len(orig):
            mm[k] = orig[k]
    sm = difflib.SequenceMatcher(None, bytes(mm), orig, autojunk=False)
    return sum(n for _, _, n in sm.get_matching_blocks())


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
        # ⚠ Urutan pencarian HARUS dari |d| terkecil. Versi pertama memakai
        # range(-24, 25) sehingga d = -24 dicoba DULUAN; pada kode berulang
        # (mis. enam panggilan load() beruntun di main) geseran besar tetap
        # memberi lari cocok panjang, jadi alat memilihnya dan melaporkan
        # penjajaran jauh lebih buruk dari yang sebenarnya.
        for d in sorted(range(-24, 25), key=lambda v: (abs(v), v)):
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
    gtot = global_aligned(m, slots, orig)
    print("  TERJAJAR  : %d / %d  (%.1f%%)   <- serakah, untuk daftar geseran"
          % (tot, size, 100.0 * tot / size))
    print("  GLOBAL    : %d / %d  (%.1f%%)   <- INI yang dipakai memutuskan"
          % (gtot, size, 100.0 * gtot / size))
    print("  geseran   : %s" % ", ".join("0x%04x:%+d" % (addr + o, d)
                                         for o, d in sh))


if __name__ == "__main__":
    main()
