"""Katalog komponen: tiap part digambar PERSIS seperti game menggambarnya.

Ditulis ulang 2026-08-01. Versi lama punya tiga cacat yang membuat katalognya
menyesatkan:

  1. Hanya record PERTAMA tiap tipe yang digambar. Part yang di biner terdiri
     dari DUA record berantai (row dan row+100) jadi tampak terpotong -- gejala
     yang tertangkap saat memeriksa id 94: bagian bawahnya (16x43 di dy=14)
     hilang, sehingga katalog berbeda dengan layar yang dibangkitkan.
  2. Daftar tipe diambil dari tangkapan emulator (`port/cc/draws/*.json`), jadi
     ikut bergantung pada varian mana yang kebetulan terpilih saat capture.
     Sekarang daftarnya dibaca dari CONTRAP -- sumber yang sebenarnya, dan
     mencakup goal 7 (demo) serta goal 128 (layar judul). Hasilnya 70 tipe zany,
     bukan ~59.
  3. Sprite yang isinya SELURUHNYA warna latar tampak seperti sel kosong dan
     terbaca sebagai bug. Contohnya id 83: satu record 4x2, nol piksel berwarna,
     dipakai di layar judul. Sekarang ditandai "(kosong)" secara eksplisit.

Aturan menggambarnya sama dengan work/genscreens.py, yang sudah diverifikasi
menjelaskan 197/197 blit yang ditangkap emulator.

    python work/gen_catalog.py
"""
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "work"))
import genscreens as G                                        # noqa: E402

MECH_NAMES = {100: "Inclined Plane", 101: "Inclined Plane", 110: "Pulley",
              111: "Pulley", 112: "Pulley", 133: "Pulley", 115: "Wheel & Axle",
              120: "Wedge", 130: "Pendulum", 131: "Pendulum", 132: "Magnet",
              135: "Screw", 140: "Lever", 141: "Lever", 150: "Spring"}

HITAM = (0, 0, 0)
MERAH = (140, 0, 0)


def font(sz, bold=False):
    for n in (("consolab.ttf", "arialbd.ttf") if bold else ("consola.ttf", "arial.ttf")):
        p = os.path.join(r"C:\Windows\Fonts", n)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


F = font(12)
FB = font(16, True)


def gambar_rantai(arc, mulai):
    """Susun SATU part utuh dari rantai record-nya -> (Image, kosong?).

    Sama seperti game: tiap record ditempel pada (dx, dy) relatif terhadap titik
    tempel part. Kotak pembatasnya dihitung dari seluruh rantai, bukan dari
    record pertama saja -- itu yang dulu memotong id 94.
    """
    ch = arc.chain(mulai)
    x0 = min(r["dx"] for r in ch)
    y0 = min(r["dy"] for r in ch)
    x1 = max(r["dx"] + r["w"] for r in ch)
    y1 = max(r["dy"] + r["h"] for r in ch)
    im = Image.new("RGB", (max(1, x1 - x0), max(1, y1 - y0)), G.PALETTE[G.BG])
    berwarna = 0
    for r in ch:
        px = arc.pixels(r)
        sub = Image.new("RGB", (r["w"], r["h"]))
        sub.putdata([G.PALETTE[c] for row in px for c in row])
        im.paste(sub, (r["dx"] - x0, r["dy"] - y0))
        berwarna += sum(1 for row in px for c in row if c != G.BG)
    return im, berwarna == 0


def build(entri, judul, kolom, sel, path):
    baris = (len(entri) + kolom - 1) // kolom
    W, H = kolom * sel, baris * sel + 40
    canvas = Image.new("RGB", (W, H), G.PALETTE[G.BG])
    d = ImageDraw.Draw(canvas)
    d.text((8, 10), judul, font=FB, fill=HITAM)
    for i, (im, label, kosong) in enumerate(entri):
        cx = (i % kolom) * sel
        cy = (i // kolom) * sel + 36
        muat_w, muat_h = sel - 8, sel - 44
        sc = min(muat_w / max(im.width, 1), muat_h / max(im.height, 1), 2.0)
        if sc < 1:
            w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc))
        else:
            k = max(1, int(sc))
            w, h = im.width * k, im.height * k
        canvas.paste(im.resize((w, h), Image.NEAREST),
                     (cx + (sel - w) // 2, cy + 2))
        for j, ln in enumerate(label.split("\n")):
            d.text((cx + 2, cy + sel - 39 + j * 13), ln, font=F,
                   fill=MERAH if ("kosong" in ln or "tak dipakai" in ln) else HITAM)
    canvas.save(path)
    print("-> %s (%d item)" % (path, len(entri)))


def tipe_terpakai():
    """Tipe yang BENAR-BENAR dirujuk CONTRAP, termasuk goal 7 dan 128.

    Dibaca dari sumbernya, bukan dari tangkapan emulator -- tangkapan hanya
    memuat varian yang kebetulan terpilih saat itu.
    """
    b = open(os.path.join(G.DATA, "CONTRAP"), "rb").read()
    n = struct.unpack_from("<I", b, 2)[0] // 6
    zany, mech = set(), set()
    for i in range(n):
        gid, off = struct.unpack_from("<HI", b, i * 6)
        if gid == 0:
            continue
        p = off + 2
        cA = struct.unpack_from("<H", b, p)[0]
        p += 2 + cA * 4
        cB = struct.unpack_from("<H", b, p)[0]
        p += 2
        for k in range(cB):
            mech.add(struct.unpack_from("<hhH", b, p + k * 6)[2])
        p += cB * 6
        cC = struct.unpack_from("<H", b, p)[0]
        p += 2
        for k in range(cC):
            zany.add(struct.unpack_from("<hhH", b, p + k * 6)[2])
    return sorted(zany), sorted(mech)


def main():
    graph = G.Archive(os.path.join(G.DATA, "GRAPH"))
    mechs = G.Archive(os.path.join(G.DATA, "MECHS"))
    zt, mt = tipe_terpakai()

    # Katalog MECHS menampilkan SEMUA id di arsip, bukan hanya yang dirujuk
    # CONTRAP -- ini katalog isi berkas. Yang tidak pernah dipakai ditandai,
    # karena itu fakta yang menarik: id 131 (Pendulum bentuk kedua) ADA di
    # arsip tapi tak satu pun kontraption memakainya.
    ent = []
    for t in sorted({r["id"] for r in mechs.recs}):
        vs = mechs.variants(t)
        if not vs:
            continue
        im, kosong = gambar_rantai(mechs, vs[0])
        # Penanda di BARIS KETIGA: sel 130 px tidak muat untuk
        # "id=131 (tak dipakai)" dalam satu baris.
        lbl = "%s\nid=%d" % (MECH_NAMES.get(t, "?"), t)
        if kosong:
            lbl += "\n(kosong)"
        elif t not in mt:
            lbl += "\n(tak dipakai)"
        ent.append((im, lbl, kosong or t not in mt))
    build(ent, "MEKANISME (MECHS) — %d tipe, %d dipakai kontraption"
          % (len(ent), len(mt)), 5, 130,
          os.path.join(ROOT, "work", "catalog_mechs.png"))

    ent = []
    for t in zt:
        vs = graph.variants(t)
        if not vs:
            continue
        im, kosong = gambar_rantai(graph, vs[0])
        # Keterangan ditaruh di BARIS KEDUA, bukan disambung ke baris pertama:
        # sel cuma 96 px, dan "id=82  (kosong)" melebar sampai ke sel tetangga.
        lbl = "id=%d" % t
        if kosong:
            lbl += "\n(kosong)"
        elif len(vs) > 1:
            lbl += "\n%d varian" % len(vs)
        ent.append((im, lbl, kosong))
    build(ent, "ZANY OBJECT / PEMANDANGAN (GRAPH) — %d tipe" % len(ent), 8, 96,
          os.path.join(ROOT, "work", "catalog_zany.png"))


if __name__ == "__main__":
    main()
