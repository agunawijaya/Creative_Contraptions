"""Verifikasi IDENTITAS SIMBOL untuk fungsi yang BELUM cocok byte-per-byte.

⚠ KENAPA ADA. Dua alat lain punya lubang yang saling melengkapi:

  - `aligncmp.py` memperlakukan slot relokasi sebagai WILDCARD (harus begitu,
    alamatnya belum final di `.OBJ`). Akibatnya penyimpanan ke simbol yang
    SALAH tidak terdeteksi: `mov [a],ax` dan `mov [b],ax` bytenya identik.
  - `symcheck.py` bisa memeriksa identitas simbol, TAPI ia MELEWATI fungsi yang
    belum cocok byte-per-byte, karena offsetnya tak sejajar dengan biner asli
    sehingga pembacaannya menghasilkan sampah.

Jadi untuk `main`, `pickvar`, `place`, `nvar`, `loadcon` identitas simbol
tidak terverifikasi oleh alat mana pun. Berkas ini menutup celah itu: ia
memakai PETA LARI SEJAJAR dari aligncmp untuk memetakan tiap offset FIXUPP
kita ke offset yang benar di biner asli, lalu membandingkan alamat yang kita
klaim dengan yang sebenarnya dituju.

    python src_c/verify/fixorder.py <nama> <alamat_hex> <ukuran>
    python src_c/verify/fixorder.py main_ 82 4219
"""
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(__file__))
TARGET = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
IMAGE_BASE = 0x200


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        raise SystemExit(2)
    name = sys.argv[1]
    addr = int(sys.argv[2], 16)
    size = int(sys.argv[3])

    from objcode import read_omf, pick_code_segment
    from aligncmp import align_runs
    from symcheck import read_obj, manifest, symbol_map

    obj = os.path.join(ROOT, "src_c", "out", name + ".OBJ")
    _, (m, slots) = pick_code_segment(read_omf(obj))
    with open(TARGET, "rb") as fh:
        b = fh.read()
    orig = b[IMAGE_BASE + addr:IMAGE_BASE + addr + size]

    runs = align_runs(m, slots, orig)
    sym = symbol_map(manifest())
    _, fixups = read_obj(obj)

    def map_off(o):
        for oi, oj, n in runs:
            if oi <= o < oi + n:
                return oj + (o - oi)
        return None

    ok = beda = luar = takdikenal = idx = 0
    for off, mbit, nm in sorted(fixups):
        if nm is None:
            continue
        t = sym.get(nm)
        if t is None:
            takdikenal += 1
            continue
        oo = map_off(off)
        if oo is None or oo + 2 > len(orig):
            luar += 1
            continue
        raw = struct.unpack_from("<H", bytes(orig), oo)[0]
        # self-relative (call) vs segment-relative (data)
        actual = raw if mbit else (addr + oo + 2 + struct.unpack_from(
            "<h", bytes(orig), oo)[0]) & 0xFFFF
        if actual == t[1]:
            ok += 1
        elif 0 < actual - t[1] <= 0x40 and not [
                n2 for n2, v in sym.items() if v[1] == actual]:
            # Akses ber-INDEKS: `recC[i*3+2]` memancarkan fixup ke recC dengan
            # +4 ikut di displacement yang sama. Bukan kesalahan simbol.
            idx += 1
        else:
            other = [n2 for n2, v in sym.items() if v[1] == actual]
            beda += 1
            print("BEDA  +%-5d %-12s kita=%s(0x%04x)  asli=0x%04x%s"
                  % (off, nm, nm, t[1], actual,
                     "=" + other[0] if other else ""))
    print()
    print("%s @0x%04x -- cocok: %d, BEDA: %d, ber-indeks (bukan salah): %d, "
          "di luar lari sejajar: %d, nama tanpa alamat: %d"
          % (name, addr, ok, beda, idx, luar, takdikenal))
    print("(slot 'di luar lari sejajar' tidak bisa diperiksa -- wilayah yang "
          "memang belum sejajar)")


if __name__ == "__main__":
    main()
