/* FUN_1000_0082 @ 1000:0082, 4.219 byte — main().
 *
 * ⏳ DRAF AWAL. Belum masuk manifest (stubs.c masih menyediakan main kosong),
 * jadi berkas ini TIDAK ikut di-link. Ukur dengan:
 *     pwsh src_c/build/compile.ps1 -Name main_
 *     python src_c/verify/aligncmp.py main_ 0082 4219
 *
 * ⭐ TEMUAN ARSITEKTUR TERPENTING: hampir SEMUA tabel besar game ini hidup di
 * BINGKAI TUMPUKAN main, bukan di DGROUP. Global-global penunjuk yang selama
 * ini kita pakai (recbase, base, objtab, level_, ytop_) diisi di 0x00B5..0x00E4
 * dengan alamat lokal main. Itu sebabnya DGROUP cuma 9.556 byte padahal data
 * kerjanya jauh lebih besar: bingkai main sendiri 0x6F96 = 28.566 byte.
 *
 * PETA BINGKAI (DIUKUR dari seluruh 4.219 byte disassembly, bukan ditebak).
 * Selisih antar-offset memberi ukuran tiap penyangga:
 *
 *   bp+0000..0007  temp (4 slot)
 *   bp+0008        larik 8 entri x 0x28 byte  (08 30 58 80 a8 d0 f8 120)
 *   bp+0148        264 byte   <- level_  (global 0x740)
 *   bp+0250       1500 byte   <- recbase (global 0x73c) = 125 record x 12
 *                              ⭐ cocok dgn batas `k2 > 0x78` (120) di pickvar
 *   bp+082c        900 byte   <- objtab  (global 0x73e)
 *   bp+0bb0        420 byte   <- base    (global 0x73a) = 35 record x 12
 *   bp+0d54        850 byte
 *   bp+10a6       3000 byte   <- ytop_   (global 0x84a)
 *   bp+1c5e      18000 byte   penyangga terbesar (sprite/layar)
 *   bp+62ae       2884 byte
 *   bp+6df2        304 byte
 *   bp+6f22        100 byte
 *   bp+6f86        int i    (pencacah loop, dipakai 9 kali)
 *   bp+6f88        4 byte TAK TERREFERENSI
 *   bp+6f8c        int
 *   bp+6f8e        4 byte TAK TERREFERENSI
 *   bp+6f92        int
 *   bp+6f94        int
 *   ------------------------------------------------ total 0x6f96 = 28.566
 *
 * PANGGILAN yang dilakukan main (22 sasaran berbeda) dan namanya:
 *   131a pickpart  149d fillans   171f ?        1814 getkey   18db ? (VM anim)
 *   312a credits   31da askopts   32bb lvlmenu  341a mainmenu 3f0f drawslot
 *   498c ?         5035 loadcon   531d loadarc  53ff load     5a5b snd1
 *   5a78 sndini    5db8 setfont   5f90 ?        644a bios10   65e0 put
 *   6a48 printf    6b57 ? (MC.LIB)
 * Yang masih '?' belum direkonstruksi; 0x498c adalah fungsi TEPAT SESUDAH
 * pickvar (bingkai 0x74).
 *
 * ⚠ level_ dan ytop_ dideklarasikan `extern int` di berkas lain padahal main
 * mengisinya dengan ALAMAT. Jangan mengubah tipenya di sini dan jangan memberi
 * nama kedua -- gendata.py memanen deklarasi extern dari SEMUA berkas .c dan
 * tipe yang berbeda akan mengubah emisi DGROUP. Pakai cast saja.
 */

extern int  level_;             /* @0x740 */
extern int  ytop_;              /* @0x84a */
extern int  markf[];            /* @0x76a */
extern int  curopt;             /* @0x522 */
extern int  ctx;                /* @0x524 */
extern int  objtab;             /* @0x73e */
extern int  base;               /* @0x73a */
extern int  recbase;            /* @0x73c */
/* Dua alamat ini BELUM pernah dinamai di berkas lain; keduanya juga bukan
   awal simbol yang sudah ada, jadi aman diberi nama (lihat aturan gendata). */
extern int  mark[];             /* @0x742 */
extern int  prevx;              /* @0x266 */
extern int  prevtop;            /* @0x262 */
extern int  page;               /* @0x2e0 */
extern int  page2;              /* @0x2e2 */
/* ⚠ 0x846 sudah bernama `mode_` di berkas lain, tapi di sini jelas ia
   PEGANGAN BERKAS: diisi hasil open() lalu diteruskan ke loadarc sebagai
   argumen pertama. Namanya menyesatkan; JANGAN diganti (aturan: satu alamat
   satu nama), cukup dicatat. */
extern int  mode_;              /* @0x846 */
extern int  scrmode;            /* @0x3b0 */
extern int  g83a;               /* @0x83a  belum dianalisa maknanya */

main()
{
    /* Deklarasi ditulis supaya OFFSET-nya jatuh persis seperti peta di atas.
       Urutan alokasi lokal MS C 1.04 masih harus diverifikasi lewat `sub sp`:
       kalau bukan 0x6f96, urutannya dibalik dulu sebelum menulis kode. */
    char ent[8][0x28];          /* 0008 */
    char lvlbuf[264];           /* 0148 */
    char recs[1500];            /* 0250 */
    char objs[900];             /* 082c */
    char basebuf[420];          /* 0bb0 */
    char buf0d54[850];          /* 0d54 */
    char ytop[3000];            /* 10a6 */
    char big[18000];            /* 1c5e */
    char buf62ae[2884];         /* 62ae */
    char buf6df2[304];          /* 6df2 */
    char buf6f22[100];          /* 6f22 */
    int  i;                     /* 6f86  pencacah loop, dipakai 9 kali */
    char g1[4];                 /* 6f88  tak terreferensi */
    int  j;                     /* 6f8c */
    char g2[4];                 /* 6f8e  tak terreferensi */
    int  k;                     /* 6f92 */
    int  m;                     /* 6f94 */

    bios10(scrmode);
    put(curopt, ctx);
    if (setup() != 0) {
        printf(0x930);
        return;
    }
    ytop_ = (int)ytop;
    objtab = (int)objs;
    level_ = (int)lvlbuf;
    base = (int)basebuf;
    recbase = (int)recs;
    /* ⚠ TERTUNDA: 0x00B9 `mov bx,[0]` = baca kata pertama DGROUP (offset 0).
       Butuh simbol bernama di DGROUP:0000, TAPI gendata.py menyaring
       `START <= a` dengan START=4 -- alamat DGROUP 0..3 DIBUANG diam-diam,
       jadi namanya tidak pernah terbit dan LINK gagal (unresolved dg0).
       Memperbaikinya menyentuh penataan DGROUP yang saat ini 100% cocok,
       jadi TIDAK dikerjakan tanpa pengawasan. Biayanya 7 byte di sini. */
    for (i = 0; i < 0x14; i++)
        markf[i] = 1;
    for (i = 0; i < 0x14; i++)
        mark[i] = 1;
    /* Empat penugasan konstanta ini dipancarkan dalam urutan TERBALIK
       (aturan MS C 1.04 yang sudah dikenal), jadi urutan sumbernya
       page, page2, prevtop, prevx -- bukan sebaliknya. */
    page = 0x26c;
    page2 = 0x284;
    prevtop = 0x140;
    prevx = 0x140;
    mode_ = open(0x952, 0x8004);
    if (mode_ == -1) {
        printf(0x957);
        return;
    }
    loadarc(mode_, level_, 1);
    /* Enam muatan awal dari arsip yang sama. Argumen ke-3 = nomor record,
       ke-4 = alamat tujuan di DGROUP. */
    load(mode_, level_, 0, 0x31c);
    load(mode_, level_, 1, 0x364);
    load(mode_, level_, 2, 0x526);
    load(mode_, level_, 3, 0x586);
    load(mode_, level_, 4, 0x5e6);
    load(mode_, level_, 0x13, 0x646);
}

/* ⏳ BELUM DITULIS: 0x0101 ke atas (4.100 byte).
 *
 * LANGKAH BERIKUTNYA, berurutan:
 * 1. Verifikasi `sub sp` == 0x6f96 dengan deklarasi di atas. Kalau meleset,
 *    balik urutan deklarasi -- JANGAN menambah pengganjal sebelum tahu arah
 *    alokasinya (pelajaran dari pickvar: pengganjal yang salah menggeser
 *    SEMUA slot dan menyesatkan berjam-jam).
 * 2. Namai 0x5f90 (dipanggil sekali, hasilnya != 0 -> pesan galat 0x930)
 *    dan 0x6b57 (4 pemanggilan, kemungkinan rutin MC.LIB).
 * 3. Baru menulis blok demi blok, ukur dengan aligncmp.py tiap blok.
 */
