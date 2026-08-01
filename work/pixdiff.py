"""Pembanding piksel — alat ukur untuk klaim "tampilannya sama persis".

Tanpa ini, "sama persis" hanya bisa dinilai dengan mata, dan mata sudah beberapa
kali salah di proyek ini (part id 94 terpotong selama berbulan-bulan dan terlihat
masuk akal).

    python work/pixdiff.py <a.png> <b.png> [--out diff.png] [--warna]

Keluaran: jumlah piksel identik, persentase, kotak pembatas wilayah yang beda,
dan (opsional) gambar diff yang menandai bedanya.

--warna  bandingkan nilai RGB apa adanya.
         Tanpa itu, kedua gambar dipetakan dulu ke INDEKS palet CGA sebelum
         dibandingkan; itu yang biasanya diinginkan, karena dua penampil bisa
         menuliskan warna yang sama dengan nilai RGB berbeda.
"""
import os
import sys

from PIL import Image

PALETTE = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]


def ke_indeks(im):
    """RGB -> indeks palet CGA. Warna di luar palet dipetakan ke yang terdekat."""
    px = list(im.convert("RGB").getdata())
    tabel = {}
    out = []
    for p in px:
        if p not in tabel:
            tabel[p] = min(range(4), key=lambda i: sum(
                (a - b) ** 2 for a, b in zip(p, PALETTE[i])))
        out.append(tabel[p])
    return out


def banding(pa, pb, warna=False):
    a, b = Image.open(pa), Image.open(pb)
    if a.size != b.size:
        return dict(sama_ukuran=False, ua=a.size, ub=b.size)
    w, h = a.size
    if warna:
        da, db = list(a.convert("RGB").getdata()), list(b.convert("RGB").getdata())
    else:
        da, db = ke_indeks(a), ke_indeks(b)
    beda = [i for i in range(w * h) if da[i] != db[i]]
    box = None
    if beda:
        xs = [i % w for i in beda]
        ys = [i // w for i in beda]
        box = (min(xs), min(ys), max(xs), max(ys))
    return dict(sama_ukuran=True, w=w, h=h, n=w * h, beda=beda, box=box,
                da=da, db=db)


def tulis_diff(r, path):
    w, h = r["w"], r["h"]
    im = Image.new("RGB", (w, h))
    px = []
    bs = set(r["beda"])
    for i in range(w * h):
        if i in bs:
            px.append((255, 0, 0))
        else:
            c = r["da"][i]
            g = PALETTE[c] if not isinstance(c, tuple) else c
            px.append(tuple(v // 3 for v in g))       # redupkan yang sama
    im.putdata(px)
    im.save(path)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 2:
        sys.exit(__doc__)
    warna = "--warna" in sys.argv
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    r = banding(a[0], a[1], warna)
    if not r["sama_ukuran"]:
        print("UKURAN BEDA: %s vs %s" % (r["ua"], r["ub"]))
        return 2
    n, nb = r["n"], len(r["beda"])
    print("%s  vs  %s" % (os.path.basename(a[0]), os.path.basename(a[1])))
    print("  ukuran     : %dx%d (%d piksel)" % (r["w"], r["h"], n))
    print("  IDENTIK    : %d / %d  (%.3f%%)" % (n - nb, n, 100.0 * (n - nb) / n))
    if nb:
        print("  beda       : %d piksel, kotak %s" % (nb, r["box"]))
        if out:
            tulis_diff(r, out)
            print("  gambar diff: %s  (merah = beda)" % out)
    else:
        print("  -> IDENTIK PIKSEL-PER-PIKSEL")
    return 0 if nb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
