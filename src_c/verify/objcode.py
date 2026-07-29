"""Ambil byte KODE dari .OBJ (OMF) hasil MS C 1.04, lalu banding dgn biner game asli.

Kenapa perlu: hasil kompilasi kita masih .OBJ yang belum di-relokasi — alamat variabel
global & target call masih nol, baru diisi linker. Biner game sudah ter-link, jadi slot
itu berisi alamat sungguhan. Pembandingan harus memperlakukan slot relokasi sebagai
wildcard, kalau tidak setiap fungsi terlihat "beda" padahal kodenya identik.

PENTING — dua pelajaran yang sudah menggigit sekali:
  1. Satu .OBJ berisi BEBERAPA segmen LEDATA (kode DAN data). Kalau digabung berdasar
     offset saja, data akan MENIMPA awal kode. Di sini tiap segmen dipisah.
  2. Slot relokasi dibaca dari record FIXUPP yang sebenarnya, BUKAN ditebak dari
     "byte kita nol". Tebakan itu menyamarkan perbedaan sungguhan jadi 'cocok'.

Pakai:
    python src_c/verify/objcode.py <file.obj>                 # daftar segmen + dump
    python src_c/verify/objcode.py <file.obj> <addr> <size>   # banding vs biner asli
"""
import sys
import os
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
IMAGE_BASE = 0x200          # awal segmen kode di dalam EXE ter-unpack

# Ukuran byte yang ditempati tiap jenis lokasi fixup (field LOCAT bit 5..2).
LOC_SIZE = {0: 1, 1: 2, 2: 2, 3: 4, 4: 1, 5: 2, 9: 2, 11: 4, 13: 4}


def _index(body, j):
    """Indeks OMF: 1 byte kalau <0x80, kalau tidak 2 byte."""
    return (j + 2) if (body[j] & 0x80) else (j + 1)


def parse_fixupp(body, base):
    """Kembalikan set offset (relatif segmen) yang ditempati slot relokasi."""
    slots = set()
    j = 0
    while j < len(body):
        b0 = body[j]
        if not (b0 & 0x80):                 # THREAD subrecord
            j += 1
            j = _index(body, j) if (b0 & 0x08) == 0 else j
            continue
        if j + 2 >= len(body):
            break
        locat = (b0 << 8) | body[j + 1]     # big-endian
        off = locat & 0x03FF
        loc = (locat >> 10) & 0x0F
        j += 2
        fixdat = body[j]
        j += 1
        F = (fixdat >> 7) & 1
        T = (fixdat >> 3) & 1
        P = (fixdat >> 2) & 1
        if F == 0:
            j = _index(body, j)             # frame datum
        if T == 0:
            j = _index(body, j)             # target datum
        if P == 0:
            j += 2                          # target displacement
        for k in range(LOC_SIZE.get(loc, 2)):
            slots.add(base + off + k)
    return slots


def read_omf(path):
    """Kembalikan {segidx: (bytes_kode, set_slot_relokasi)}."""
    b = open(path, "rb").read()
    segs = {}          # segidx -> {offset: data}
    fixups = {}        # segidx -> set
    last = None        # (segidx, offset)
    i = 0
    while i + 3 <= len(b):
        rtype = b[i]
        rlen = struct.unpack_from("<H", b, i + 1)[0]
        body = b[i + 3:i + 3 + rlen - 1]           # -1: buang checksum
        if rtype == 0xA0 and len(body) >= 3:       # LEDATA
            seg = body[0]
            off = struct.unpack_from("<H", body, 1)[0]
            segs.setdefault(seg, {})[off] = body[3:]
            last = (seg, off)
        elif rtype == 0x9C and last is not None:   # FIXUPP
            seg, off = last
            fixups.setdefault(seg, set()).update(parse_fixupp(body, off))
        i += 3 + rlen - 1 + 1

    out = {}
    for seg, chunks in segs.items():
        size = max(o + len(d) for o, d in chunks.items())
        buf = bytearray(size)
        for o, d in chunks.items():
            buf[o:o + len(d)] = d
        out[seg] = (bytes(buf), fixups.get(seg, set()))
    return out


def pick_code_segment(segs):
    """Segmen kode = yang paling besar (modul MS C: PROG jauh lebih besar dari DATA)."""
    return max(segs.items(), key=lambda kv: len(kv[1][0]))


def compare(code, slots, addr, size):
    tgt = open(TARGET, "rb").read()[IMAGE_BASE + addr: IMAGE_BASE + addr + size]
    n = min(len(code), len(tgt))
    diff = [k for k in range(n) if code[k] != tgt[k]]
    reloc = [k for k in diff if k in slots]
    real = [k for k in diff if k not in slots]

    def fmt(buf):
        return " ".join(("__" if k in slots else "%02x" % buf[k]) for k in range(len(buf)))

    print("panjang : kita=%d  asli=%d %s" % (len(code), len(tgt),
                                             "" if len(code) == len(tgt) else "  <-- BEDA PANJANG"))
    print("slot relokasi (dari FIXUPP): %s" % (sorted(slots) if slots else "tidak ada"))
    print("beda    : %d byte  (%d di slot relokasi = wajar, %d BEDA SUNGGUHAN)"
          % (len(diff), len(reloc), len(real)))
    if real:
        print("posisi beda sungguhan:", real[:24])
        for k in real[:10]:
            print("   +%3d : kita=%02x  asli=%02x" % (k, code[k], tgt[k]))
    print()
    print("kita : " + fmt(code))
    print("asli : " + fmt(tgt))
    return not real and len(code) == len(tgt)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    segs = read_omf(sys.argv[1])
    print("segmen dalam .OBJ: " + ", ".join(
        "seg%d=%dB" % (s, len(d)) for s, (d, _) in sorted(segs.items())))
    seg, (code, slots) = pick_code_segment(segs)
    print("dipakai sebagai kode: seg%d (%d byte)" % (seg, len(code)))
    print()
    if len(sys.argv) >= 4:
        ok = compare(code, slots, int(sys.argv[2], 16), int(sys.argv[3], 0))
        print()
        print("HASIL: " + ("COCOK BYTE-PER-BYTE" if ok else "BELUM cocok"))
        sys.exit(0 if ok else 1)
    print(" ".join("%02x" % c for c in code))
