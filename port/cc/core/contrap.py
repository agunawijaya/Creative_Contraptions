"""Berkas CONTRAP + aturan penempatan — satu implementasi bersama.

Format (dari loader `loadcon` @0x5035, sudah cocok byte-per-byte):

    Direktori (216 byte): 36 x { u16 id, u32 offset }
       id 1..6 = enam kontraption; id berulang = varian struktur
       id 7    = sembilan demo mekanisme (mode Review)
       id 128  = layar judul
       id 0    = slot kosong

    Per kontraption @offset:
       u16  goal_id
       u16  countA ; u32[countA]        <- makna BELUM diketahui (panjang pasti)
       u16  countB ; rec6[countB]       <- MEKANISME  { u16 y, u16 x, u16 jenis }
       u16  countC ; rec6[countC]       <- OBJEK ZANY { u16 y, u16 x, u16 jenis }
       u16[countB+countC]

⚠ Urutannya `y` DULU, baru `x` -- konsisten dengan blit(spr, Y, X, H, W).

Aturan posisi layar, dari `pickvar.c` / `place.c`:

    posisi layar = posisi di CONTRAP + (dx, dy) dari record sprite

Slot mekanisme yang BELUM diisi digambar `drawslot.c` sebagai blok penuh:

    fillrect(x + 1, y, x + 0x1e, y + 0x17, 3)      -> 30x24 warna 3

Elemen TETAP di puncak layar: corong bola, MISC record 2 di (136, 0). Muncul di
semua goal dan semua varian; record mana yang dipakai sudah dipastikan lewat
tangkapan VRAM asli (idx 2 cocok 384/384 piksel, idx 3 hanya 140/384).
"""
import struct

CORONG_REC = 2
CORONG_XY = (136, 0)

SLOT_W, SLOT_H = 0x1E, 0x17          # fillrect x+1..x+0x1e, y..y+0x17
SLOT_WARNA = 3


def parse(path):
    """-> {goal: [varian]}; tiap varian {'mech': [(y,x,tipe)], 'zany': [...]}"""
    b = open(path, "rb").read()
    n = struct.unpack_from("<I", b, 2)[0] // 6
    goals = {}
    for i in range(n):
        gid, off = struct.unpack_from("<HI", b, i * 6)
        if gid == 0:
            continue
        p = off
        goal = struct.unpack_from("<H", b, p)[0]
        p += 2
        cA = struct.unpack_from("<H", b, p)[0]
        p += 2
        # `postab` @0x3b6 -- POSISI LABEL HURUF, bukan data tak dikenal.
        # f15d0(): for (i=0;i<cnt;i++) { s = i+'A'; text(&s, tab[i*2+1], tab[i*2], 1,1,3); }
        # jadi tiap entri = (x, y) dan hurufnya 'A'+i, warna 3.
        pos = [struct.unpack_from("<hh", b, p + k * 4) for k in range(cA)]
        p += cA * 4
        cB = struct.unpack_from("<H", b, p)[0]
        p += 2
        mech = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cB)]
        p += cB * 6
        cC = struct.unpack_from("<H", b, p)[0]
        p += 2
        zany = [struct.unpack_from("<hhH", b, p + k * 6) for k in range(cC)]
        p += cC * 6
        # `state` @0x4f2 -- URUTAN RANTAI. Satu entri per part; -1 = mekanisme,
        # selainnya objek zany. Di dalam tiap jenis, part dipakai berurutan
        # sesuai urutannya di CONTRAP.
        #
        # Dipakai `animvm()` opcode 0x03 untuk tahu part MANA yang menerima bola
        # berikutnya: `if (steps[i+1] == -1)` memilih daftar mekanisme, kalau
        # tidak daftar zany. Diperiksa terhadap urutan skrip yang dilaporkan
        # emulator untuk goal 1 -- zany, mech, zany, mech, zany, zany, zany,
        # mech, zany, zany -- yang persis sama dengan [1,-1,1,-1,1,1,1,-1,1,1].
        state = [struct.unpack_from("<h", b, p + k * 2)[0] for k in range(cB + cC)]
        goals.setdefault(goal, []).append(
            dict(mech=mech, zany=zany, pos=pos, state=state))
    return goals


def draw_list(var, graph, mechs, misc=None, pilih=0, isi_mekanisme=False,
              corong=True, pilihan=None):
    """Daftar operasi gambar untuk SATU varian struktur.

    `pilih`    indeks varian part untuk setiap slot, dipakai kalau `pilihan`
               tidak diberikan. Deterministik, supaya keluarannya bisa diulang.
    `pilihan`  {'zany': [indeks record, ...], 'mech': [...]} -- hasil undian
               `pick.pickpart()`. INI yang meniru game asli; `pilih` hanya
               jalur cadangan untuk katalog dan bukti statis.
    `isi_mekanisme=False` = layar AWAL Fill in Mechanisms: slot masih kosong.
    """
    out = []
    if corong and misc is not None:
        r = misc.recs[CORONG_REC]
        out.append(dict(kind="blit", arc=misc, rec=r,
                        x=CORONG_XY[0], y=CORONG_XY[1], w=r["w"], h=r["h"]))
    for kelompok, arc, gambar in (("zany", graph, True),
                                  ("mech", mechs, isi_mekanisme)):
        dipilih = (pilihan or {}).get(kelompok)
        for slot, (y, x, tipe) in enumerate(var[kelompok]):
            if dipilih is not None:
                mulai = dipilih[slot] if slot < len(dipilih) else None
            else:
                vs = arc.variants(tipe)
                mulai = vs[min(pilih, len(vs) - 1)] if vs else None
            if mulai is None:
                continue
            if not gambar:
                out.append(dict(kind="slot", x=x, y=y))
                continue
            for r in arc.chain(mulai):
                out.append(dict(kind="blit", arc=arc, rec=r,
                                x=x + r["dx"], y=y + r["dy"],
                                w=r["w"], h=r["h"]))
    return out


def semua_kemungkinan(var, graph, mechs, misc=None):
    """Semua (x,y,w,h) yang MUNGKIN dihasilkan varian ini, untuk verifikasi.

    Varian part diundi acak saat runtime, jadi tidak bisa ditebak per-jalan.
    Yang diperiksa: tiap blit yang tertangkap emulator HARUS ada di himpunan ini.
    """
    bisa = set()
    if misc is not None:
        r = misc.recs[CORONG_REC]
        bisa.add((CORONG_XY[0], CORONG_XY[1], r["w"], r["h"]))
    for kelompok, arc in (("zany", graph), ("mech", mechs)):
        for (y, x, tipe) in var[kelompok]:
            for v in arc.variants(tipe):
                for r in arc.chain(v):
                    bisa.add((x + r["dx"], y + r["dy"], r["w"], r["h"]))
    return bisa
