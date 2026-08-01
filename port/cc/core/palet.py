"""Strip pemilih part di dasar layar — `drawpal()` @0x5xxx.

Bukan sekadar deretan ikon. Tiga hal yang mudah salah, dan port lama salah
di ketiganya:

⭐ 1. URUTANNYA DIBALIK. `blit(addr, 0xa8, 0x110 - i * 0x20, ...)` -- indeks
      logis `lo + i` yang MAKIN BESAR digambar makin ke KIRI. Item pertama
      jendela muncul di ujung KANAN layar.

⭐ 2. JENDELA GESER, BUKAN SELURUH DAFTAR. Hanya sembilan sel yang tampak,
      berpusat di pilihan sekarang: `lo = sel - 4`, `hi = sel + 4`. Kalau
      `sel == -1`, pusatnya `nmech / 2`. Sel yang jatuh di luar daftar TIDAK
      dikosongkan begitu saja -- ia diisi HITAM (`fillrect(..., 0)`), jadi
      tepi jendela terlihat sebagai lubang gelap, bukan latar.

⭐ 3. UKURAN DAN TEMPATNYA TETAP. Sembilan sel 32x24 di `y = 0xa8` (168),
      pada `x = 0x110 - i*0x20` -> 272, 240, 208, 176, 144, 112, 80, 48, 16.
      Tidak ada penskalaan mengikuti banyaknya pilihan.

Penunjuknya berkedip dengan menukar dua sprite MISC di tempat yang sama:

    blit(0x364, 0xc0, 0x90, 8, 0x20);   <- MISC record 1
    blit(0x31c, 0xc0, 0x90, 8, 0x20);   <- MISC record 0

yaitu 32x8 di (x=0x90, y=0xc0) = (144, 192), berselang ~12 tik.

⚠ `review.c` -- yang memanggil `drawpal()` -- BUKAN hanya layar Review
Mechanisms. Ia gelung pemilih part yang dipakai saat BERMAIN juga: di dalamnya
ada `hintmark()`, `timebar()`, dan pemeriksaan `mode == 4 && tx <= 0` untuk
waktu habis. Namanya di rekonstruksi menyesatkan.
"""
ROWTAB = 0x870                   # 9 id mekanisme, urutan layar Review
N_MEK = 9


def rowtab():
    """Sembilan id mekanisme untuk strip Review, dari DGROUP @0x870.

    ⚠ Isinya `[100, 110, 115, 120, 130, 132, 135, 141, 150]` -- perhatikan
    **141**, bukan 140, untuk Lever. Daftar kategori yang ditulis tangan di
    port memakai 140 sebagai wakil kategori itu, dan thumbnail-nya berbeda.
    """
    from . import dgtab
    return list(dgtab.blok(ROWTAB, N_MEK))


SEL_W, SEL_H = 0x20, 0x18        # 32 x 24
SEL_Y = 0xA8                     # 168
SEL_X0 = 0x110                   # sel i berada di SEL_X0 - i*SEL_W
N_SEL = 9

PENUNJUK_XY = (0x90, 0xC0)       # 144, 192
PENUNJUK_REC = (1, 0)            # MISC record 1 dan 0, bergantian
PENUNJUK_TIK = 12                # ~12 tik per fase, dari gelung `for (i = 0; i < 0xc; ...)`


def jendela(sel, n):
    """-> daftar 9 indeks logis (None kalau sel itu di luar daftar).

        if (sel == -1) { cur = nmech/2; lo = nmech/2 - 4; }
        else           { cur = sel;     lo = sel - 4;     }
    """
    lo = (n // 2 - 4) if sel == -1 else (sel - 4)
    return [(lo + i if 0 <= lo + i < n else None) for i in range(N_SEL)]


def drawpal(k, sel, isi, n=None):
    """Gambar strip. `isi(indeks) -> (arsip, record)` atau None.

    `isi` sengaja sebuah fungsi: di gim asli sel diambil dari penyangga
    thumbnail `base + spr[lo+i] * 0xc0`, yaitu urutan yang SUDAH dikocok.
    Pemanggil yang tahu urutannya, bukan modul ini.
    """
    n = n if n is not None else 0
    for i, idx in enumerate(jendela(sel, n)):
        x = SEL_X0 - i * SEL_W
        pasangan = isi(idx) if idx is not None else None
        if pasangan is None:
            k.fillrect(x, SEL_Y, x + SEL_W - 1, SEL_Y + SEL_H - 1, 0)
            continue
        arc, rec = pasangan
        k.blit(arc, rec, x, SEL_Y)


def penunjuk(k, misc, fase=0):
    """Penunjuk berkedip di bawah strip: dua sprite MISC ditukar di tempat."""
    rec = misc.recs[PENUNJUK_REC[fase & 1]]
    k.blit(misc, rec, PENUNJUK_XY[0], PENUNJUK_XY[1])


# ── Catatan verifikasi, supaya tidak diulang ─────────────────────────────
#
# `drawpal()` dipakai DUA layar, dan `runplay()` memanggil keduanya:
#     baris 72  review(...)   -> cabang MEKANISME: strip sembilan thumbnail
#     baris 95  pickvar(...)  -> cabang ZANY: kandidat berputar DI DALAM kotak
# Jadi model port (strip untuk Fill in Mechanisms, in-box untuk Fill in Zany)
# memang benar.
#
# HASIL NEGATIF: strip ini BELUM pernah diadu piksel dengan gim asli.
# Empat percobaan menangkapnya lewat emulator gagal, masing-masing dengan
# sebab berbeda:
#   1. OBSERVE=fillmech berhenti sesudah goal dipilih -> ditambah CC_OBSKEYS;
#   2. anggaran instruksi habis -> ditambah CC_MAXINSN;
#   3. dengan 250 juta instruksi, `672f` terpanggil 207.069 kali dan
#      `drawpal` NOL kali -- emulator berputar di gelung gambar ulang;
#   4. di jalur Review yang berhasil dijangkau, `nmech` bernilai 0 sehingga
#      kesembilan sel mengambil cabang HITAM. Artefak emulator, bukan gim.
# TERPECAHKAN. Penyebabnya sepele dan bukan pada gimnya: tangkapan diambil di
# ALAMAT MASUK `drawpal`, sehingga yang terlihat selalu keadaan SEBELUM ia
# menggambar -- dan di antara dua panggilan, strip itu memang dibersihkan
# hitam. Ditangkap di alamat RET (0x3C4E) isinya langsung muncul.
#
# Diukur: strip `drawpal(sel=-1)` dengan urutan `rowtab` @0x870
# = 7.680/7.680 piksel vs tangkapan VRAM emulator.
#
# ── Strip di mode ISIAN, dan kenapa ia sempat "tak terjangkau" ───────────
#
# Menangkapnya di mode Fill in Mechanisms berkali-kali gagal, dan sebabnya
# BUKAN pada gimnya: `work/emu.py` sengaja mem-bypass gelung penempatan part
# (`hook_2e90`), dan `drawpal()` hidup DI DALAM gelung itu. Ditambahkan
# saklar `CC_NOSKIP=1` untuk mematikan bypass-nya; sesudah itu tangkapannya
# langsung ada. "Terhalang emulator" ternyata untuk KEDUA kalinya berarti
# "terhalang oleh harness kita sendiri".
#
# Terukur di mode ISIAN (OBSERVE=fillmech CC_NOSKIP=1, tangkap di RET 0x3C4E):
#   sel = 1, n = 3 -> jendela [None,None,None,0,1,2,None,None,None]
#   dan tangkapannya memang HITAM PENUH di i = 0,1,2,6,7,8 dan berisi di
#   i = 3,4,5 (x = 176, 144, 112). Aturan jendela-geser + urutan-dibalik +
#   isian hitam berlaku sama di mode ISIAN, pada posisi piksel yang sama.
#
# ⭐ TEMUAN yang lebih besar: BERAPA pilihan yang ditawarkan tergantung MODE.
# `nmech` @0x3ac terukur 3, 4, 3 untuk goal 1, 2, 4 -- yaitu jumlah JENIS
# mekanisme yang dibutuhkan kontraption itu ([100,150,110], [101,132,140,133],
# [141,130,111]), bukan sembilan kategori. Sebabnya di `mkpal()` @0x3909:
#
#     if (lvl3 != 1 || base[i*0xc] == tab[j*3+2]) { ...masuk palet }
#
# `lvl3 == 1` di mode 1/2/3 dan `lvl3 == 3` di mode 4. Jadi Fill in Mechanisms
# hanya menawarkan part yang memang dipakai (soalnya "taruh di kotak yang
# benar"), sedangkan Contraption Mix Up menawarkan seluruh daftar. Port lama
# selalu memberi kesembilan kategori di semua mode.
#
# @0x7fa = `spr[]`, permutasi hasil kocokan. Terukur: goal 2 -> 01 03 02 00,
# goal 4 -> 01 00 02.
#
# ⭐ SISI MIX UP KINI TERUKUR JUGA. Yang menghalanginya bukan `pickvar`
# melainkan urutan tombol OBSERVE bawaan, yang diakhiri ESC (0x1B): ESC
# membuat `runplay()` mengembalikan -1 sebelum strip sempat digambar. Dgn
# urutan tanpa ESC, drawpal langsung tertangkap.
#
#   Contraption Mix Up  lvl3 = 3, shufflg = 1, nmech = 13
#   dan 13 itu memang 15 id record berbeda di MECHS sesudah tiga id >= 0x8c
#   (140, 141, 150) diciutkan jadi satu oleh dedup mkpal.
#
# ⭐ `idtab[]` @0x2ea MENGINDEKS `base`, bukan direktori arsip -- dan `base`
# berbeda menurut mode: `loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`.
# Terukur `CC_VSPTR=73a:`: mode isian 6 record (disaring+dipadatkan), Mix Up
# 30 record (direktori penuh). Salah memilihnya memberi CACAH yang benar tapi
# THUMBNAIL yang meleset -- gejala yang sempat terlihat sebagai 23.292/27.648.
#
# Diukur, kedua mode: **48.384/48.384 piksel** (`python work/test_palet.py`).
#
# Alat yang dipakai untuk mendiagnosisnya, semuanya di work/emu.py:
#   CC_VSWORD=3ac,51c   catat word DGROUP tiap frame (nmech, cur, lo, hi)
#   CC_VSMEM=7fa:12     buang byte mentah dari alamat tetap (urutan palet)
#   CC_VSPTR=84a:24     baca sebuah word sebagai ALAMAT lalu buang isinya
