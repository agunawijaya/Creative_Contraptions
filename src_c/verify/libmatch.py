"""Cocokkan modul-modul MC.LIB ke wilayah pustaka di biner asli.

Kenapa penting: kalau sebuah potongan biner asli ternyata BYTE-PER-BYTE sama
dengan modul di MC.LIB, potongan itu TIDAK perlu ditulis ulang -- cukup panggil
nama pustakanya dan linker menaruhnya di sana. Setiap byte yang terbukti berasal
dari pustaka mengecilkan target rekonstruksi dan langsung menghapus satu stub.

Cara: MC.LIB adalah arsip OMF (deretan modul THEADR..MODEND, ukuran halaman
tetap). Tiap modul diambil segmen kodenya, lalu dicari di segmen kode biner
asli. Slot relokasi (dari FIXUPP) diperlakukan wildcard, jadi pencarian
dilakukan dengan menyamakan hanya byte NON-slot.

    python src_c/verify/libmatch.py            # ringkasan semua modul
    python src_c/verify/libmatch.py -v         # + daftar modul yang tak ketemu
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from objcode import TARGET, IMAGE_BASE, parse_fixupp          # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LIB = os.path.join(ROOT, "tools", "msc104", "bin", "MC.LIB")
CODE_END = 0x9070          # awal DGROUP = akhir segmen kode


def modules(path):
    """Pisah arsip OMF jadi modul: [(nama, {seg: (kode, slot)}, set_pubdef)].

    Perpustakaan OMF menaruh tiap modul di batas HALAMAN (di MC.LIB: 512 byte)
    dan mengisi sisa halaman dengan nol. Sesudah MODEND kita WAJIB melompat ke
    batas halaman berikutnya -- kalau tidak, byte nol pengisi dibaca sebagai
    record bertipe 0x00 dan penguraian langsung tersesat (gejalanya: hanya satu
    modul yang terbaca).
    """
    b = open(path, "rb").read()
    page = struct.unpack_from("<H", b, 1)[0] + 3
    out = []
    cur = None
    i = 0
    while i + 3 <= len(b):
        rtype = b[i]
        rlen = struct.unpack_from("<H", b, i + 1)[0]
        body = b[i + 3:i + 3 + rlen - 1]
        if rtype == 0xF0:                       # LIBHDR: ukuran halaman = rlen+3
            i += page
            continue
        if rtype == 0xF1:                       # LIBEND / dictionary -> selesai
            break
        if rtype == 0x80:                       # THEADR = modul baru
            if cur:
                out.append(cur)
            name = body[1:1 + body[0]].decode("ascii", "replace") if body else "?"
            cur = [name, {}, set(), {}, None]   # nama, segs, pub, fix, last
        elif cur is not None:
            if rtype == 0xA0 and len(body) >= 3:            # LEDATA
                seg = body[0]
                off = struct.unpack_from("<H", body, 1)[0]
                cur[1].setdefault(seg, {})[off] = body[3:]
                cur[4] = (seg, off)
            elif rtype == 0x9C and cur[4]:                  # FIXUPP
                seg, off = cur[4]
                cur[3].setdefault(seg, set()).update(parse_fixupp(body, off))
            elif rtype == 0x90 and len(body) >= 3:          # PUBDEF
                j = 2
                while j < len(body):
                    n = body[j]
                    if n == 0 or j + 1 + n > len(body):
                        break
                    nm = body[j + 1:j + 1 + n].decode("ascii", "replace")
                    off = struct.unpack_from("<H", body, j + 1 + n)[0]
                    cur[2].add((nm, off))
                    j += 1 + n + 2 + 1
            elif rtype == 0x8A:                             # MODEND
                out.append(cur)
                cur = None
                i = ((i + 3 + rlen - 1 + 1 + page - 1) // page) * page
                continue
        i += 3 + rlen - 1 + 1
    if cur:
        out.append(cur)

    res = []
    for name, segs, pub, fix, _ in out:
        flat = {}
        for seg, chunks in segs.items():
            size = max(o + len(d) for o, d in chunks.items())
            buf = bytearray(size)
            for o, d in chunks.items():
                buf[o:o + len(d)] = d
            flat[seg] = (bytes(buf), fix.get(seg, set()))
        res.append((name, flat, pub))
    return res


def find(hay, code, slots, lo=0, hi=None):
    """Cari `code` di `hay`, byte di `slots` dianggap wildcard. -> offset / -1."""
    n = len(code)
    if n < 8:
        return -1
    hi = (hi if hi is not None else len(hay)) - n
    # jangkar = byte non-slot pertama yang cukup jarang; pakai 4 byte non-slot awal
    anchor = [k for k in range(n) if k not in slots][:6]
    if len(anchor) < 4:
        return -1
    a0 = anchor[0]
    first = code[a0]
    p = lo
    while True:
        p = hay.find(bytes([first]), p, hi + n)
        if p < 0 or p - a0 > hi:
            return -1
        s = p - a0
        if s >= lo and all(hay[s + k] == code[k] for k in anchor):
            if all(hay[s + k] == code[k] for k in range(n) if k not in slots):
                return s
        p += 1


def main():
    verbose = "-v" in sys.argv
    tgt = open(TARGET, "rb").read()
    code_img = tgt[IMAGE_BASE:IMAGE_BASE + CODE_END]
    mods = modules(LIB)
    hits, misses, total = [], [], 0
    for name, segs, pub in mods:
        if not segs:
            continue
        seg, (code, slots) = max(segs.items(), key=lambda kv: len(kv[1][0]))
        at = find(code_img, code, slots)
        if at >= 0:
            hits.append((at, len(code), name, sorted(pub)))
            total += len(code)
        else:
            misses.append((len(code), name, sorted(pub)))

    print("MC.LIB: %d modul; segmen kode asli 0..0x%04x" % (len(mods), CODE_END))
    print()
    print("%-8s %6s  %-14s %s" % ("alamat", "byte", "modul", "simbol @ alamat"))
    print("-" * 74)
    for at, n, name, pub in sorted(hits):
        # PUBDEF offset di dalam modul + alamat modul = alamat sungguhan simbol
        sym = ", ".join("%s@0x%04x" % (s, at + o) for s, o in
                        sorted(pub, key=lambda p: p[1]))
        print("0x%04x  %6d  %-14s %s" % (at, n, name, sym))
    print()
    print("KETEMU  : %d modul, %d byte terbukti berasal dari MC.LIB" % (len(hits), total))
    print("TAK ADA : %d modul (wajar -- tidak semua rutin pustaka dipakai game)"
          % len(misses))
    if hits:
        print("rentang : 0x%04x .. 0x%04x" % (min(h[0] for h in hits),
                                              max(h[0] + h[1] for h in hits)))
    if verbose:
        print()
        for n, name, pub in sorted(misses, reverse=True)[:30]:
            print("   tak ketemu: %-14s %5d byte  %s" % (name, n, ", ".join(pub[:4])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
