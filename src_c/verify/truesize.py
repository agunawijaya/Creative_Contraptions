"""Hitung UKURAN SEBENARNYA tiap fungsi — jangan percaya size= di functions.txt.

Ghidra hanya menghitung potongan pertama yang bersambung. Fungsi yang badannya
terpecah oleh lompatan (mis. yang punya `switch`) tercatat jauh lebih kecil dari
kenyataan: FUN_1000_18db tercatat 1.229 byte, sebenarnya 3.040.

Cara di sini: baca N dari prolog `push bp; sub sp,N; mov bp,sp`, lalu cari
kemunculan TERAKHIR epilog `add sp,N; pop bp; ret` sebelum fungsi berikutnya.

    python src_c/verify/truesize.py            # yang ukurannya beda saja
    python src_c/verify/truesize.py --all      # semua
"""
import os
import re
import sys
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXE = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
FNS = os.path.join(ROOT, "work", "ghidra_out", "functions.txt")


def load():
    b = open(EXE, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    fns = []
    for ln in open(FNS):
        m = re.match(r"(\w+):(\w+)\s+(\S+)\s+size=(\d+)", ln.strip())
        if m:
            fns.append((int(m.group(2), 16), m.group(3), int(m.group(4))))
    fns.sort()
    return b, lb, fns


def true_end(img, start, limit):
    """Kembalikan (ukuran, N_bingkai) atau (None, None) kalau prolognya bukan pola C."""
    if img[start] != 0x55 or img[start + 1] not in (0x81, 0x83) or img[start + 2] != 0xEC:
        return None, None
    if img[start + 1] == 0x83:
        n = img[start + 3]
        epi = bytes([0x83, 0xC4, n, 0x5D, 0xC3])
    else:
        n = struct.unpack_from("<H", img, start + 3)[0]
        epi = bytes([0x81, 0xC4]) + struct.pack("<H", n) + bytes([0x5D, 0xC3])
    last = -1
    i = start
    while True:
        j = img.find(epi, i, limit)
        if j < 0:
            break
        last = j
        i = j + 1
    if last < 0:
        return None, n
    return last + len(epi) - start, n


def main():
    b, lb, fns = load()
    img = b[lb:]
    show_all = "--all" in sys.argv
    rows = []
    for k, (a, name, ghidra_sz) in enumerate(fns):
        nxt = fns[k + 1][0] if k + 1 < len(fns) else len(img)
        # batas pencarian: fungsi berikutnya yang prolognya sah (biar celah ikut terbaca)
        limit = nxt
        for a2, _, _ in fns[k + 1:]:
            if img[a2] == 0x55 and img[a2 + 1] in (0x81, 0x83) and img[a2 + 2] == 0xEC:
                limit = a2
                break
        sz, n = true_end(img, a, limit)
        if sz is None:
            continue
        if show_all or sz != ghidra_sz:
            rows.append((a, name, ghidra_sz, sz, n))
    print("%-8s %-18s %8s %8s %7s" % ("alamat", "fungsi", "ghidra", "asli", "bingkai"))
    print("-" * 55)
    tot_g = tot_t = 0
    for a, name, g, t, n in sorted(rows, key=lambda r: -(r[3] - r[2])):
        print("0x%04x  %-18s %8d %8d %7d %s" % (a, name, g, t, n,
                                                "  <-- +%d" % (t - g) if t > g else ""))
        tot_g += g
        tot_t += t
    print()
    print("%d fungsi ditampilkan | ghidra total %d byte, sebenarnya %d byte (+%d)"
          % (len(rows), tot_g, tot_t, tot_t - tot_g))


if __name__ == "__main__":
    main()
