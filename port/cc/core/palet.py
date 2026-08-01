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
# Yang terverifikasi baru ATURANNYA (dari sumber), bukan pikselnya.
