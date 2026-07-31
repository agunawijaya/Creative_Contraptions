"""Verifikasi SEMUA fungsi yang sudah direkonstruksi terhadap biner asli.

Membaca src_c/src/manifest.txt berisi baris:  <nama> <alamat_hex> <ukuran>
lalu membandingkan src_c/out/<nama>.OBJ dengan potongan biner yang sesuai.

Kolom KEEMPAT opsional `art=N[,N...]` menandai offset yang berisi ARTEFAK
KOMPILER — byte yang TERBUKTI tidak ditentukan oleh sumber C fungsi itu
(mis. sisa penunjuk internal MS C 1.04). Byte begitu dilaporkan terpisah,
JANGAN dihitung sebagai cocok dan JANGAN disamarkan.

    python src_c/verify/verifyall.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from objcode import read_omf, pick_code_segment, TARGET, IMAGE_BASE   # noqa: E402

MANIFEST = os.path.join(ROOT, "src", "manifest.txt")
OUT = os.path.join(ROOT, "out")


def entries():
    for ln in open(MANIFEST, encoding="utf-8"):
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        p = ln.split()
        art = set()
        for tok in p[3:]:
            if tok.startswith("art="):
                art = {int(v) for v in tok[4:].split(",")}
        yield p[0], int(p[1], 16), int(p[2]), art


def linked_data():
    """Segmen DATA dari src_c/out/CONTRAP.EXE, batasnya dibaca dari CONTRAP.MAP."""
    import struct
    exe = os.path.join(OUT, "CONTRAP.EXE")
    mp = os.path.join(OUT, "CONTRAP.MAP")
    if not (os.path.exists(exe) and os.path.exists(mp)):
        return None
    row = [l.split() for l in open(mp) if " DATA " in l and " STACK " not in l]
    if not row:
        return None
    start, length = int(row[0][0][:-1], 16), int(row[0][2][:-1], 16)
    b = open(exe, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    return b[lb + start:lb + start + length]


def main():
    tgt = open(TARGET, "rb").read()
    rows, ok_bytes, tot_bytes, art_bytes = [], 0, 0, 0
    for name, addr, size, art in entries():
        tot_bytes += size
        obj = os.path.join(OUT, name + ".OBJ")
        if not os.path.exists(obj):
            rows.append((name, addr, size, "TIDAK ADA .OBJ", 0))
            continue
        segs = read_omf(obj)
        if not segs:
            rows.append((name, addr, size, "OBJ kosong", 0))
            continue
        _, (code, slots) = pick_code_segment(segs)
        orig = tgt[IMAGE_BASE + addr: IMAGE_BASE + addr + size]
        if len(code) != len(orig):
            rows.append((name, addr, size, "panjang %d != %d" % (len(code), len(orig)), 0))
            continue
        real = [k for k in range(len(orig)) if code[k] != orig[k] and k not in slots]
        left = [k for k in real if k not in art]
        if left:
            rows.append((name, addr, size, "%d byte beda (mis. +%d)" % (len(left), left[0]), 0))
        elif real:
            art_bytes += len(real)
            rows.append((name, addr, size,
                         "COCOK kecuali %d byte ARTEFAK KOMPILER (+%s)"
                         % (len(real), ",+".join(str(k) for k in real)), size - len(real)))
            ok_bytes += size - len(real)
        else:
            rows.append((name, addr, size, "COCOK", size))
            ok_bytes += size

    w = max(len(r[0]) for r in rows) if rows else 8
    print("%-*s  %-7s %6s  %s" % (w, "fungsi", "alamat", "ukuran", "hasil"))
    print("-" * (w + 30))
    for name, addr, size, res, _ in rows:
        print("%-*s  0x%04x  %6d  %s" % (w, name, addr, size, res))
    n_ok = sum(1 for r in rows if r[3].startswith("COCOK"))
    print()
    print("COCOK %d/%d fungsi   |   %d byte terverifikasi (dari %d byte yang digarap)"
          % (n_ok, len(rows), ok_bytes, tot_bytes))
    if art_bytes:
        print("      %d byte di antaranya ARTEFAK KOMPILER yang TIDAK cocok "
              "(tidak dihitung di atas)" % art_bytes)
    # KODE NYATA = wilayah 0x0082..0x69d7 (26.965 B) DIKURANGI 1.207 byte NOL
    # di 0x5F93..0x6442 yang TERBUKTI bukan kode. Pembagi lama (~26.000)
    # memuat byte nol itu, jadi semua persentase dulu terlalu KECIL.
    CODE_TARGET = 25758
    print("Kode C game   : %d / %d byte  (%.1f%%)"
          % (ok_bytes, CODE_TARGET, ok_bytes * 100.0 / CODE_TARGET))

    # Segmen DATA (DGROUP) diverifikasi dari .EXE HASIL LINK -- itu artefak yang
    # sebenarnya, bukan .OBJ tunggal. Sumbernya: gdata.OBJ (offset 4..akhir) +
    # 4 byte dari C.OBJ (crt0). Kalau .EXE belum ada, mundur ke gdata.OBJ.
    sys.path.insert(0, HERE)
    from dgroup import dgroup as _dg                        # noqa: E402
    orig = _dg()
    dg_tot = len(orig)
    dg_ok = 0
    data = linked_data()
    src = "hasil link"
    if data is None:
        src = "gdata.OBJ"
        gd = os.path.join(OUT, "gdata.OBJ")
        if os.path.exists(gd):
            segs = read_omf(gd)
            order = sorted(segs.items(), key=lambda kv: len(kv[1][0]), reverse=True)
            data = b"\0" * 4 + (order[1] if len(order) > 1 else order[0])[1][0]
    if data:
        n = min(len(data), dg_tot)
        dg_ok = sum(1 for k in range(n) if data[k] == orig[k])
    print("Segmen DATA   : %d / %d byte  (%.1f%%)  [%s]"
          % (dg_ok, dg_tot, dg_ok * 100.0 / dg_tot, src))

    # ⚠ KOREKSI: rumus lama `26000 + 1200 + data` MENGHITUNG GANDA. Modul
    # assembly (blit, blitmsk, keyio, text, prep, snd1, snd2, line, shftl,
    # vbio, fillrec, setup, unrle) SEMUANYA ada di manifest dan sudah ikut
    # `ok_bytes`; menambah +1.200 lagi menghitungnya dua kali. Dan +1.200 itu
    # sendiri keliru — 1.207 byte di 0x5F93 ternyata NOL, bukan assembly.
    total_target = CODE_TARGET + (dg_tot or 9556)       # kode game + data
    total_ok = ok_bytes + dg_ok
    print("-" * 46)
    print("TOTAL         : %d / %d byte  (%.1f%%)"
          % (total_ok, total_target, total_ok * 100.0 / total_target))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
