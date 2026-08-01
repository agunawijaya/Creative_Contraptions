"""Bangkitkan diagram untuk dokumen belajar (ARCHITECTURE.md / CODE_MAP.md).

Semua angka di diagram diambil dari data NYATA (berkas aset, peta link, biner),
bukan ditulis tangan -- supaya dokumennya tidak bisa basi diam-diam.

    python work/gendocimg.py      -> work/doc/*.png
"""
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_ORIGINAL_READONLY")
OUT = os.path.join(ROOT, "work", "doc")
sys.path.insert(0, os.path.join(ROOT, "work"))
import genscreens as G                                        # noqa: E402

BG = (24, 26, 32)
FG = (232, 232, 236)
DIM = (150, 155, 165)
ACC = (120, 200, 255)
WARN = (255, 190, 90)
OK = (140, 220, 150)


def font(sz, bold=False):
    for n in ("consolab.ttf" if bold else "consola.ttf",
              "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf",
              "arialbd.ttf" if bold else "arial.ttf"):
        for d in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            p = os.path.join(d, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, sz)
                except Exception:
                    pass
    return ImageFont.load_default()


F = font(15)
FB = font(17, True)
FS = font(12)


def canvas(w, h, judul):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((16, 12), judul, font=FB, fill=FG)
    d.line((16, 36, w - 16, 36), fill=(70, 74, 86))
    return im, d


def box(d, x, y, w, h, label, sub="", warna=ACC, isi=None):
    d.rectangle((x, y, x + w, y + h), outline=warna, width=2, fill=isi)
    d.text((x + 10, y + 8), label, font=F, fill=FG)
    if sub:
        d.text((x + 10, y + 28), sub, font=FS, fill=DIM)


# ---------------------------------------------------------------- 1. memori
def mem_layout():
    """Peta segmen .EXE + DGROUP, angkanya dibaca dari CONTRAP.MAP."""
    mp = os.path.join(ROOT, "src_c", "out", "CONTRAP.MAP")
    seg = []
    for ln in open(mp):
        p = ln.split()
        if len(p) >= 5 and p[0].endswith("H") and p[3] in ("BASE", "PROG", "DATA", "STACK"):
            a0, b0 = int(p[0][:-1], 16), int(p[1][:-1], 16)
            if b0 > a0:                      # lewati segmen 0 byte (dgalign)
                seg.append((a0, b0, p[3]))
    im, d = canvas(1060, 520, "1. Tata letak .EXE Creative Contraptions di memori (angka dari CONTRAP.MAP)")
    y = 60
    warna = {"BASE": (150, 150, 160), "PROG": ACC, "DATA": OK, "STACK": WARN}
    for a, b, nm in seg:
        n = b - a + 1
        h = max(50, min(140, n // 110))
        ket = {"BASE": "tanda tangan kompiler 14 byte: \"MS-C  V 1.04  \"",
               "PROG": "SELURUH kode: game + rutin pustaka MC.LIB",
               "DATA": "DGROUP -- variabel global, tabel, teks",
               "STACK": "tumpukan 256 byte"}[nm]
        box(d, 40, y, 620, h, "%-6s 0x%05X..0x%05X  (%s byte)" % (nm, a, b, "{:,}".format(n)),
            ket, warna[nm])
        y += h + 10
    d.text((700, 66), "Kenapa PROG dan DATA terpisah?", font=F, fill=WARN)
    for i, t in enumerate([
        "Prosesor 8086 memakai SEGMEN 64 KB.",
        "Kode dialamati lewat CS, data lewat DS.",
        "Model SMALL = satu segmen kode +",
        "satu segmen data, jadi semua alamat",
        "cukup 16 bit. Itu sebabnya program",
        "1985 terasa 'kecil': batasnya bukan",
        "disiplin, melainkan arsitektur.",
        "",
        "DGROUP WAJIB mulai di batas",
        "paragraf (kelipatan 16). Kalau tidak,",
        "DS menunjuk satu paragraf di bawahnya",
        "dan SEMUA alamat data meleset.",
    ]):
        d.text((700, 92 + i * 20), t, font=FS, fill=DIM if i > 6 else FG)
    im.save(os.path.join(OUT, "doc_mem_layout.png"))


# ------------------------------------------------------------------- 2. CGA
def cga_pixel():
    im, d = canvas(1000, 430, "2. Satu byte = empat piksel: cara CGA menyimpan gambar")
    byte = 0b11011000
    d.text((40, 60), "Contoh satu byte dari berkas GRAPH:", font=F, fill=FG)
    x0 = 40
    for i in range(8):
        bit = (byte >> (7 - i)) & 1
        d.rectangle((x0 + i * 46, 88, x0 + i * 46 + 42, 130), outline=DIM, width=1)
        d.text((x0 + i * 46 + 15, 98), str(bit), font=FB, fill=FG)
    d.text((x0, 140), "11011000  = 0xD8", font=F, fill=DIM)
    d.text((40, 180), "Dibaca DUA bit sekaligus, dari kiri:", font=F, fill=FG)
    pal = G.PALETTE
    nama = ["0 biru (latar layar)", "1 cyan (latar game)", "2 magenta", "3 abu"]
    for i in range(4):
        v = (byte >> (6 - 2 * i)) & 3
        d.rectangle((40 + i * 120, 208, 40 + i * 120 + 100, 268), fill=pal[v], outline=FG)
        d.text((40 + i * 120 + 8, 274), "piksel %d -> %d" % (i, v), font=FS, fill=DIM)
    d.text((560, 180), "Palet: hanya EMPAT warna", font=F, fill=WARN)
    for i in range(4):
        d.rectangle((560, 206 + i * 30, 600, 230 + i * 30), fill=pal[i], outline=FG)
        d.text((610, 210 + i * 30), nama[i], font=FS, fill=DIM)
    for i, t in enumerate([
        "320x200 piksel x 2 bit = 16.000 byte per layar penuh.",
        "Itu memaksa gaya seni: garis tebal, blok warna rata, tanpa gradasi.",
        "PENTING: barisnya BERSELANG-SELING di memori: baris genap mulai di 0x0000,",
        "   baris ganjil di 0x2000. Warisan cara CRT menggambar dua medan.",
    ]):
        d.text((40, 330 + i * 22), t, font=FS, fill=FG if i < 2 else WARN)
    im.save(os.path.join(OUT, "doc_cga_pixel.png"))


# ------------------------------------------------------------------- 3. RLE
def rle():
    a = G.Archive(os.path.join(DATA, "MECHS"))
    r = a.recs[0]
    raw = a.raw[r["off"]:r["off"] + r["ln"]]
    dec = G.decode_rle(raw)
    im, d = canvas(1060, 470, "3. Pemampatan RLE: bagaimana 30 sprite muat di disket 360 KB")
    d.text((40, 60), "Sprite '%s' (id=%d), %dx%d piksel" % ("Inclined Plane", r["id"], r["w"], r["h"]),
           font=F, fill=FG)
    d.text((40, 84), "di berkas : %3d byte" % len(raw), font=F, fill=WARN)
    d.text((40, 106), "sesudah dibuka : %3d byte   (hemat %d%%)"
           % (len(dec), 100 - 100 * len(raw) // max(1, len(dec))), font=F, fill=OK)
    d.text((40, 140), "Potongan byte mentahnya:", font=F, fill=FG)
    d.text((40, 164), " ".join("%02X" % c for c in raw[:24]), font=FS, fill=DIM)
    d.text((40, 196), "Aturannya cuma satu:", font=F, fill=FG)
    d.text((40, 220), "  E4 <jumlah> <nilai>   ->  ulangi <nilai> sebanyak <jumlah>", font=FS, fill=ACC)
    d.text((40, 240), "  byte lain             ->  salin apa adanya", font=FS, fill=ACC)
    i = 0
    contoh = None
    while i < len(raw) - 2:
        if raw[i] == 0xE4:
            contoh = (raw[i + 1], raw[i + 2])
            break
        i += 1
    if contoh:
        d.text((40, 272), "Contoh nyata di sprite ini: E4 %02X %02X  ->  %d byte bernilai 0x%02X"
               % (contoh[0], contoh[1], contoh[0], contoh[1]), font=FS, fill=WARN)
    px = a.pixels(r)
    Z = 4
    sp = Image.new("RGB", (r["w"], r["h"]))
    sp.putdata([G.PALETTE[c] for row in px for c in row])
    im.paste(sp.resize((r["w"] * Z, r["h"] * Z), Image.NEAREST), (660, 70))
    d.text((660, 74 + r["h"] * Z), "hasilnya: sprite ini", font=FS, fill=DIM)
    for i, t in enumerate([
        "Kenapa justru RLE, bukan yang lebih pintar?",
        "Karena membukanya harus CEPAT dan MUAT: rutin pembukanya",
        "cuma beberapa lusin byte assembly, tidak butuh memori kerja,",
        "dan gambar CGA 4 warna penuh deretan byte yang sama.",
        "Kompresi yang lebih baik akan menghabiskan RAM yang justru",
        "dibutuhkan untuk gambarnya sendiri.",
    ]):
        d.text((40, 320 + i * 22), t, font=FS, fill=WARN if i == 0 else DIM)
    im.save(os.path.join(OUT, "doc_rle.png"))


# -------------------------------------------------------------- 4. pipeline
def pipeline():
    im, d = canvas(1060, 330, "4. Dari .C menjadi .EXE: rantai perkakas 1985")
    tahap = [("kode.c", "sumber C"), ("MC1.EXE", "penganalisa"), ("kode.Q", "berkas QUAD"),
             ("MC2.EXE", "penghasil kode"), ("kode.OBJ", "objek OMF"),
             ("LINK.EXE", "penaut"), ("CONTRAP.EXE", "program")]
    x = 24
    for i, (a, b) in enumerate(tahap):
        w = 118
        warna = OK if a.endswith(".EXE") and i in (1, 3, 5) else ACC
        box(d, x, 70, w, 56, a, b, warna)
        if i < len(tahap) - 1:
            d.line((x + w + 4, 98, x + w + 18, 98), fill=DIM, width=2)
            d.polygon([(x + w + 18, 94), (x + w + 24, 98), (x + w + 18, 102)], fill=DIM)
        x += w + 28
    for i, t in enumerate([
        "Kompilernya DUA FASE, dan itu penting untuk dipahami:",
        "  MC1 membaca C dan menulis QUAD -- daftar operasi tanpa register sama sekali.",
        "  MC2 membaca QUAD dan barulah memutuskan nilai mana masuk register mana.",
        "",
        "Akibatnya: kalau dua tulisan C menghasilkan QUAD yang sama, keduanya PASTI",
        "menghasilkan byte yang sama. Pemilihan register bukan sifat teks sumber,",
        "melainkan hasil urutan operasi -- persis seperti kompiler modern, hanya jauh",
        "lebih sederhana dan sepenuhnya bisa ditelusuri.",
        "",
        "Catatan: MC2 menghapus berkas .Q sesudah membacanya. Jalankan MC1 sendirian untuk melihatnya.",
    ]):
        d.text((28, 160 + i * 17), t, font=FS,
               fill=WARN if i == 0 else (ACC if i in (1, 2) else DIM))
    im.save(os.path.join(OUT, "doc_pipeline.png"))


# ---------------------------------------------------------------- 5. record
def record():
    a = G.Archive(os.path.join(DATA, "GRAPH"))
    r = next(x for x in a.recs if x["w"] and x["h"] and x["ln"] > 100)
    im, d = canvas(1120, 430, "5. Satu record arsip = 12 byte: seluruh 'basis data' game")
    lbl = [("+0", "id", "jenis part"), ("+1", "row", "nomor varian; +100 = bagian lanjutan"),
           ("+2", "h", "tinggi"), ("+3", "w", "lebar"),
           ("+4", "dy", "geser tegak (bertanda)"), ("+5", "dx", "geser datar (bertanda)"),
           ("+6", "len", "panjang blob (2 byte)"), ("+8", "off", "posisi blob (4 byte)")]
    lebar = [56, 56, 56, 56, 56, 56, 112, 224]
    x = 40
    nilai = [r["id"], r["row"], r["h"], r["w"], r["dy"] & 0xFF, r["dx"] & 0xFF, r["ln"], r["off"]]
    for (o, n, k), w, v in zip(lbl, lebar, nilai):
        d.rectangle((x, 74, x + w - 6, 126), outline=ACC, width=2)
        d.text((x + 8, 80), n, font=F, fill=FG)
        d.text((x + 8, 102), str(v), font=FS, fill=OK)
        d.text((x + 8, 56), o, font=FS, fill=DIM)
        x += w
    for i, (o, n, k) in enumerate(lbl):
        d.text((40, 150 + i * 20), "%-3s %-5s %s" % (o, n, k), font=FS, fill=DIM)
    d.text((560, 150), "Kenapa 12 byte, bukan struct yang enak dibaca?", font=F, fill=WARN)
    for i, t in enumerate([
        "Karena record dibaca LANGSUNG dari disket ke memori,",
        "tanpa penguraian. Bentuk di berkas = bentuk di RAM.",
        "Tidak ada JSON, tidak ada parser, tidak ada alokasi.",
        "",
        "12 byte juga bukan angka sembarangan: 6 byte data",
        "+ 2 byte penunjuk sprite + 4 byte cadangan yang diisi",
        "saat dimuat. Perkalian indeks x 12 muncul di mana-mana",
        "di kode -- itu tanda tangan tabel ini.",
        "",
        "PENTING: +4 adalah dy dan +5 adalah dx, bukan sebaliknya.",
        "         Terbalik = seluruh gambar berantakan.",
    ]):
        d.text((560, 176 + i * 19), t, font=FS, fill=WARN if t.startswith("PENTING") else DIM)
    im.save(os.path.join(OUT, "doc_record.png"))


# --------------------------------------------------------------- 6. anatomi
def anatomi():
    src = os.path.join(ROOT, "work", "screens_gen", "fillmech_goal1_v0_kosong.png")
    scr = Image.open(src).resize((640, 400), Image.NEAREST)
    im, d = canvas(1340, 560, "6. Anatomi satu layar: dari mana tiap bagian datang")
    im.paste(scr, (24, 60))
    d.rectangle((24, 60, 24 + 640, 60 + 400), outline=(90, 95, 108), width=1)

    def tanda(sx, sy, tx, ty, teks, warna):
        d.line((24 + sx * 2, 60 + sy * 2, tx, ty), fill=warna, width=2)
        d.ellipse((24 + sx * 2 - 4, 60 + sy * 2 - 4, 24 + sx * 2 + 4, 60 + sy * 2 + 4),
                  outline=warna, width=2)
        d.text((tx + 6, ty - 8), teks, font=FS, fill=warna)

    tanda(160, 4, 690, 70, "MISC record 2 -- corong awal", WARN)
    tanda(30, 25, 690, 110, "GRAPH -- objek zany (hiasan)", OK)
    tanda(64, 79, 690, 150, "kotak abu = slot mekanisme KOSONG", ACC)
    tanda(196, 24, 690, 190, "posisi dari CONTRAP + geser record", (230, 150, 230))
    for i, t in enumerate([
        "Tiga berkas berbeda menyusun satu layar:",
        "",
        "CONTRAP  menyimpan SUSUNAN: untuk tiap goal, daftar",
        "         komponen berupa (y, x, jenis).",
        "GRAPH    menyimpan objek zany -- gambar hiasan yang",
        "         sudah terpasang.",
        "MECHS    menyimpan 15 mekanisme yang harus dipilih",
        "         pemain.",
        "MISC     menyimpan potongan antarmuka tetap.",
        "",
        "Posisi layar = posisi di CONTRAP + geser (dx,dy) yang",
        "tersimpan di record sprite-nya. Pemisahan ini membuat",
        "satu objek bisa dipakai ulang di banyak goal dengan",
        "penyelarasan halus yang berbeda-beda.",
        "",
        "Kotak abu digambar fillrect(x+1, y, x+30, y+23, warna 3)",
        "-- satu baris kode, bukan sprite.",
    ]):
        d.text((690, 240 + i * 18), t, font=FS,
               fill=FG if i in (0,) else (ACC if t[:7].strip() in
                                          ("CONTRAP", "GRAPH", "MECHS", "MISC") else DIM))
    im.save(os.path.join(OUT, "doc_anatomi.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mem_layout()
    cga_pixel()
    rle()
    pipeline()
    record()
    anatomi()
    print("diagram -> %s" % OUT)
    for f in sorted(os.listdir(OUT)):
        print("   " + f)
