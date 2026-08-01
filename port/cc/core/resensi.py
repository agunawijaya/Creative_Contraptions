"""Tata letak layar *Review Mechanisms*, dibaca dari DGROUP.

Menggantikan `port/cc/anim/review_layout.json` -- hasil MENJALANKAN gim di
emulator. Ternyata tak perlu: seluruh tata letaknya memang tersimpan sebagai
tabel di segmen data program.

    @0x14F6   9 penunjuk u16, satu per mekanisme -> tabel record
    @0x1508   9 pencacah u16, berapa record per mekanisme

Tiap record 12 byte:

    +0  u16  jenis   (1 = teks)
    +2  u16  y
    +4  u16  x
    +6  u8   skala datar     (argumen `w` pada text())
    +7  u8   skala tegak     (argumen `h`)
    +8  u8   warna
    +9  u8   -
    +10 u16  penunjuk string (ber-NUL, di DGROUP)

⚠ Perhatikan `y` datang SEBELUM `x` di record ini, padahal `text()` sendiri
menerima argumen dalam urutan `(X, Y)`. Dua urutan berlawanan di satu program
bukan hal aneh di sini -- `blit()` juga `(Y, X)` sedangkan `text()` `(X, Y)`.
"""
import struct

from . import dgtab

TBL_PTR = 0x14F6                 # 9 penunjuk
TBL_CNT = 0x1508                 # 9 pencacah
N_MEK = 9
REC = 12

# Dua daftar tetap, alamatnya dipakai langsung oleh kode (tidak lewat tabel
# induk seperti kesembilan mekanisme). Ditemukan dengan menelusuri penunjuk
# ke string pertamanya: "MECHANISM REVIEW" @0x0B38 dan "Press SPACE BAR to
# see it work." @0x14B2.
INTRO = (0x0C04, 7)              # judul + pengantar layar Review
TETAP = (0x14D2, 3)              # baris bawah yang muncul di tiap mekanisme


def _string(dg, addr):
    akhir = dg.find(b"\0", addr)
    return dg[addr:akhir if akhir >= 0 else addr].decode("latin-1")


def mekanisme(i):
    """-> daftar record teks untuk mekanisme ke-i (0..8)."""
    dg = dgtab.dgroup()
    tbl = struct.unpack_from("<H", dg, TBL_PTR + 2 * i)[0]
    cnt = struct.unpack_from("<H", dg, TBL_CNT + 2 * i)[0]
    return _daftar(tbl, cnt)


def _daftar(tbl, cnt):
    """Record di sini memakai FORMAT ITEM YANG SAMA dengan tabel menu.

    Bukan kebetulan: `revdet()` memanggil `setsel(ttl[cur], def[cur])` -- fungsi
    penggambar menu yang sama persis. Jadi dekodernya satu, di `menu.tabel()`.
    """
    from . import menu
    dg = dgtab.dgroup()
    out = []
    for it in menu.tabel(tbl, cnt):
        out.append(dict(kind="text" if it["teks"] else "sprite",
                        x=it["x"], y=it["y"], sw=it["w"], sh=it["h"],
                        col=it["warna"], s=_string(dg, it["ptr"]),
                        item=it))
    return out


def intro():
    """Judul + pengantar layar Review."""
    return _daftar(*INTRO)


def tetap():
    """Baris bawah yang muncul di tiap halaman mekanisme."""
    return _daftar(*TETAP)


def semua():
    """-> {'intro': [...], 'fixed': [...], 'mechs': {i: [...]}}."""
    return dict(intro=intro(), fixed=tetap(),
                mechs={i: mekanisme(i) for i in range(N_MEK)})
