"""Layar menu — `setsel()` @0x3769 dan kotak sorotan `runmenu()` @0x34CC.

Tata letak ketiga menu tersimpan sebagai TABEL di DGROUP, bukan disusun kode:

    mtabmn  @0x1D48  11 item   menu utama
    mtablv  @0x1B74   7 item   pemilih level
    menu    @0x1C28  15 item   pemilih goal

Tiap item 12 byte:

    +0   kind   < 0x80 = teks, >= 0x80 = sprite (dan 0x80 = bisa DIPILIH)
    +2   Y
    +4   X
    +6   h / skala tegak
    +7   w / skala datar
    +8   warna (hanya cabang teks)
    +10  penunjuk string, atau alamat penyangga sprite

⚠ Rekonstruksi C menamai kedua field itu `x` dan `y`, tetapi pemakaiannya
terbalik: `text(p->spr, p->y, p->x, ...)` dan `blit(p->spr, p->x, p->y, ...)`.
Karena `text()` menerima (X, Y) dan `blit()` menerima (Y, X), keduanya sepakat
bahwa **+2 adalah Y dan +4 adalah X**. Nama fieldnya yang salah, bukan datanya.

`setsel()` menggambar latarnya sendiri:

    fillrect(0, 0, 0x13f, 7, 3);        pita atas abu-abu
    blit(hdrspr, 0, 0x88, 8, 0x30);     corong
    fillrect(0, 8, 0x13f, 0xc7, 1);     SELURUH sisanya cyan sampai y=199

Perhatikan yang terakhir: layar menu tidak punya pita bawah gelap seperti
layar permainan -- cyan sampai dasar.

Sprite ikonnya penyangga yang diisi saat runtime (`load(miscfh, ...)`):
menu utama memakai MISC record 7..10, pemilih level 11..12, pemilih goal
13..18. Karena itu field +10 pada item sprite berisi 0 di dalam DGROUP.
"""
import struct

from . import dgtab, render as rend

MTABMN = (0x1D48, 11)            # menu utama
MTABLV = (0x1B74, 7)             # pemilih level
MTABGL = (0x1C28, 15)            # pemilih goal

# ── Layar INSTRUKSI, satu per mode isian ────────────────────────────────
#
# `main_.c` menampilkannya HANYA saat pertama kali mode itu dimasuki:
#
#     if (k == 1) { switch (mode) { case 3: menu11(); case 2: menu9(); } }
#     ...
#     k = 0;
#
# Ketiganya berpola sama (`menu9`/`menu11`/`menu12`, masing-masing 37 byte):
# `setsel(tabel, n)` lalu `runmenu()`. Isinya murni teks -- termasuk cara
# bermainnya, yang di port lama tidak pernah muncul sama sekali.
#
# ⚠ Byte 0x80..0x83 di dalam string adalah GLYPH PANAH (kiri/kanan/atas/bawah),
# bukan huruf. Font gim memetakannya; jangan dianggap sampah.
MTAB9 = (0x1634, 9)              # Fill in Mechanisms
MTAB11 = (0x1796, 11)            # Fill in Zany Objects
MTAB12 = (0x18F8, 12)            # Contraption Mix Up

# ── Layar SET UP (askopts) dan CREDITS ──────────────────────────────────
#
# `askopts()` @0x31DA: dua pertanyaan Y/N berurutan -- monitor berwarna, lalu
# suara. Tabel kedua MENIMPA pertanyaan pertama dgn warna 1 lebih dulu (itu
# cara gim menghapusnya), jadi entrinya dua, bukan tiga.
MTAB_SETUP1 = (0x1AD2, 3)
MTAB_SETUP2 = (0x1AF6, 2)

# ── Status pengukuran layar-layar bertabel ──────────────────────────────
#
# `setsel()` @0x3769 adalah SATU penggambar untuk semua layar ini; yang berbeda
# hanya tabelnya. Empat tabel sudah diadu piksel dgn VRAM gim, masing-masing
# 64.000/64.000:
#
#     mtabmn  (menu utama)      mtablv (level)
#     menu    (goal)            credits tahap 0
#
# ⚠ BELUM diadu piksel, walau digambar penggambar yang sama dari tabel DGROUP
# yang sama: `askopts` (MTAB_SETUP1/2) dan ketiga layar instruksi.
#
# JALAN BUNTU, enam percobaan, disudahi 2026-08-02. Untuk memotretnya
# `credits()`/`askopts()` harus benar-benar dijalankan, dan keduanya menunggu
# di `while (keyhit() == 0);`. Tiga penghalang dibuka satu per satu -- stub
# 0x312A/0x31DA dilepas (CC_NOSTARTSTUB), `keyhit()` @0x1791 dipaksa memberi
# ENTER, `getkey()` @0x1814 disambungkan ke antrean CC_OBSKEYS supaya 'Y'
# sampai ke `askopts` -- dan sesudah ketiganya emulator MENGGANTUNG: `credits`
# tergambar (tangkapannya cocok 64.000/64.000) lalu tidak ada tangkapan kedua,
# baik lewat OBSERVE maupun ATTRACT.
#
# GANTI SUMBU, dan hasilnya justru lebih tajam: memotretnya toh tidak akan
# menjawab banyak. Penggambarnya SATU dan sudah terbukti pada empat tabel;
# BYTE tabelnya pasti benar (DATA 9.556/9.556). Yang tersisa sebagai hipotesis
# cuma ALAMAT dan JUMLAH ENTRI tiap tabel -- dan itu bisa diadu langsung dgn
# `src_c/src/*.c`, yang `.EXE`-nya byte-identik dgn biner asli.
# `work/test_tabmenu.py` melakukannya: 12/12 tabel cocok.

# `credits()` @0x312A: empat tabel DITUMPUK berurutan dgn `pause(100)` di
# antaranya -- jadi teksnya muncul bertahap, bukan sekaligus:
#
#     setsel(t1, 2); pause(100); show(t2, 2); pause(100);
#     show(t3, 2);   pause(100); show(t4, 1);
#
# Jumlah entri tiap tabel diambil dari argumen kedua itu, bukan ditebak.
# `setsel` menggambar latarnya; `show` hanya menambahkan di atasnya.
MTAB_CREDITS = ((0x1A2A, 2), (0x1A42, 2), (0x1A5A, 2), (0x1A72, 1))
CREDITS_JEDA = 100               # pause(100) -- satuannya BINGKAI, bukan tik

REC_MENU = (7, 8, 9, 10)         # MISC record ikon menu utama
REC_LEVEL = (11, 12)             # MISC record ikon pemilih level
REC_GOAL = (13, 14, 15, 16, 17, 18)   # MISC record ikon keenam goal

_TABEL = {"utama": (MTABMN, REC_MENU),
          "level": (MTABLV, REC_LEVEL),
          "goal": (MTABGL, REC_GOAL),
          "instruksi_mech": (MTAB9, ()),
          "instruksi_zany": (MTAB11, ()),
          "instruksi_mixup": (MTAB12, ()),
          "setup": (MTAB_SETUP1, ())}

# mode gim (2/3/4) -> layar instruksinya
INSTRUKSI = {2: "instruksi_mech", 3: "instruksi_zany", 4: "instruksi_mixup"}

DAPAT_DIPILIH = 0x80             # kind == 0x80 -> entri yang bisa disorot


def _str(addr):
    dg = dgtab.dgroup()
    akhir = dg.find(b"\0", addr)
    return dg[addr:akhir if akhir >= 0 else addr].decode("latin-1")


def tabel(addr, n):
    """-> daftar item menu yang sudah diurai."""
    dg = dgtab.dgroup()
    out = []
    for i in range(n):
        a = addr + i * 12
        kind = dg[a]
        y, x = struct.unpack_from("<hh", dg, a + 2)
        out.append(dict(kind=kind, teks=kind < 0x80, x=x, y=y,
                        h=dg[a + 6], w=dg[a + 7], warna=dg[a + 8],
                        ptr=struct.unpack_from("<H", dg, a + 10)[0]))
    return out


def setsel(k, item, misc, sprites=()):
    """Gambar latar menu + seluruh itemnya.

    `sprites` = record MISC untuk item ber-jenis sprite, berurutan.
    """
    k.fillrect(0, 0, 0x13F, 7, 3)
    r = misc.recs[2]                               # hdrspr = MISC record 2
    k.blit(misc, r, 0x88, 0)
    k.fillrect(0, 8, 0x13F, 0xC7, 1)
    n = 0
    for it in item:
        if it["teks"]:
            k.teks(_str(it["ptr"]), it["x"], it["y"], it["warna"],
                   it["w"], it["h"])
        else:
            if n < len(sprites):
                k.blit(misc, misc.recs[sprites[n]], it["x"], it["y"])
            n += 1


def dipilih(item):
    """Indeks item yang bisa disorot, berurutan (`kind == 0x80`)."""
    return [i for i, it in enumerate(item) if it["kind"] == DAPAT_DIPILIH]


def kotak(k, it, nyala=True):
    """Kotak sorotan `runmenu()`, digambar dengan XOR sehingga BERKEDIP.

        drawrect(y, x, h, w, 1);
        line(x + 1,     y + 1, x + 1,     y + h - 2, 1);
        line(x + w - 2, y + 1, x + w - 2, y + h - 2, 1);
        line(x,     y - 1, x + w - 1, y - 1, 2);
        line(x,     y + h, x + w - 1, y + h, 2);

    Digambar dua kali per putaran gelung: sekali menyalakan, sekali memadamkan.
    `nyala` hanya untuk memilih fase; XOR-nya sendiri simetris.
    """
    if not nyala:
        return
    x, y, h, w = it["x"], it["y"], it["h"], it["w"]
    k.xor(x, y, x + w - 1, y, 1)
    k.xor(x, y + h - 1, x + w - 1, y + h - 1, 1)
    k.xor(x + 1, y + 1, x + 1, y + h - 2, 1)
    k.xor(x + w - 2, y + 1, x + w - 2, y + h - 2, 1)
    k.xor(x, y - 1, x + w - 1, y - 1, 2)
    k.xor(x, y + h, x + w - 1, y + h, 2)


def tumpuk(misc, tabel_urut, sampai=None):
    """Gambar beberapa tabel BERTINDIH di satu layar -> framebuffer.

    Dipakai `credits()`: `setsel()` yang pertama (menggambar latar), lalu
    `show()` untuk sisanya. `sampai` membatasi berapa tabel yang sudah tampil,
    supaya pemanggil bisa memunculkannya bertahap seperti `pause(100)` di gim.
    """
    fb = rend.new_fb()
    k = rend.KanvasFB(fb)
    for i, (addr, n) in enumerate(tabel_urut):
        if sampai is not None and i > sampai:
            break
        it = tabel(addr, n)
        if i == 0:
            setsel(k, it, misc, ())
        else:
            for x in it:
                if x["teks"]:
                    k.teks(_str(x["ptr"]), x["x"], x["y"], x["warna"],
                           x["w"], x["h"])
    return fb


def layar(misc, mana="utama"):
    """-> framebuffer indeks berisi layar menu lengkap (tanpa kotak sorotan)."""
    (addr, n), spr = _TABEL[mana]
    it = tabel(addr, n)
    fb = rend.new_fb()
    setsel(rend.KanvasFB(fb), it, misc, spr)
    return fb, it
