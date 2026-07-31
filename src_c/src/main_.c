/* FUN_1000_0082 @ 1000:0082, 4.219 byte — main().
 *
 * ⏳ DRAF — 2.568 dari 4.219 byte ditulis (61%), TERJAJAR 1.779.
 * SUDAH ikut di-link (stub main sudah dicabut). Ukur dengan:
 *     pwsh src_c/build/compile.ps1 -Name main_
 *     python src_c/verify/aligncmp.py main_ 82 <ukuran_awalan>
 *     python src_c/verify/aligncmp.py main_ 82 <n> --sbs <addr> <n> <geser>
 *
 * ⚠ PAKAI METRIK TERJAJAR, BUKAN POSISI. Angka posisi hanya sahih kalau
 * panjang draf sudah persis; lihat src_c/README.md.
 *
 * BELUM DITULIS: badan case 2 (dari 0x0A4E), case 3 (0x0C03), case 1 (0x0E06),
 * dan blok `quit` (0x10E8..0x10C9 wilayah ekor).
 *
 * PETA LABEL (semua sudah terverifikasi dari disassembly):
 *   quit  = 0x10E8   reset = 0x0668 (DUA jalur masuk)
 *   redo  = 0x08A6 (pintas KE DEPAN)   after = 0x08C3   done1 = 0x0A1C
 *   gelung permainan 0x06AB keluar ke 0x0A2E
 *   nilai balik 0FEh = "waktu habis, ulangi" (konvensi sama dgn pickvar)
 *
 * GESERAN TERSISA (delapan, SEMUANYA sudah terjelaskan -- jangan dikejar):
 *   +7 @0xD6 penghalang gendata DGROUP:0000; sisanya disp8-vs-disp16 karena
 *   temp belum tumbuh ke 8 byte, atau lompatan ke label yang belum jauh.
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
 *   bp+0008        DELAPAN penyangga 40 byte terpisah (08 30 58 80 a8 d0 f8 120),
 *                  dipakai dua kelompok empat -- BUKAN satu larik
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
 *   bp+6f8e        2 byte TAK TERREFERENSI
 *   bp+6f90        int n  (dikira pengganjal, ternyata variabel)
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
extern int  seed;               /* @0x72a  ⚠ juga pegangan berkas di sini */
extern int  fh;                 /* @0x72c */
extern int  objfh;              /* @0x72e */
extern int  mode;               /* @0x792 */
extern int  sub;                /* @0x3b2 */
extern int  goal;               /* @0x718 */
extern int  lvl;                /* @0x734 */
extern int  nmax;               /* @0x3b4 */
extern int  nzany;              /* @0x4b4 */
extern int  nmechc;             /* @0x41c */
extern int  nmechb;             /* @0x41a */
extern int  ids[];              /* @0x3f2 */
extern int  recB[];             /* @0x41e */
extern int  recC[];             /* @0x4b6 */
/* postab bertipe `struct pos` di berkas lain; di sini isinya tidak dipakai,
   cuma alamatnya yang dioper, jadi cukup dideklarasikan sebagai char[]. */
extern char postab[];           /* @0x3b6 */
extern int  tinit;              /* @0x832 */
extern int  ta;                 /* @0x7ec */
extern int  tx;                 /* @0x7ee */
extern int  schi;               /* @0x732 */
extern int  sclo;               /* @0x730 */
extern int  count;              /* @0x82c */
extern int  both;               /* @0x844 */
extern int  hintshown;          /* @0x848 */
extern int  range;              /* @0x830 */
/* Dua alamat ini belum pernah dinamai; keduanya slot 2-byte bebas (0x2e6=curz
   dan 0x7e6=zcnt masing-masing hanya 2 byte). Nama sengaja netral karena
   maknanya belum terbukti -- baru terlihat diset 0 lalu diuji != -1. */
extern int  cursel;             /* @0x2e8 */
extern int  g7e8;               /* @0x7e8 */
extern int  curz;               /* @0x2e6 */
extern int  slot;               /* @0x51a */
extern int  failed;             /* @0x842 */
extern int  pass;               /* @0x71c */
extern int  lvl2;               /* @0x736 */
extern int  lvl3;               /* @0x738 */
extern int  shufflg;            /* @0x794 */
extern int  sndok;              /* @0x71a  hasil sndini(); belum pernah dinamai */
extern int  state[];            /* @0x4f2 */
extern char idtab[];            /* @0x2ea */
extern int  scrmode;            /* @0x3b0 */
extern int  g83a;               /* @0x83a  belum dianalisa maknanya */

main()
{
    /* Deklarasi ditulis supaya OFFSET-nya jatuh persis seperti peta di atas.
       Urutan alokasi lokal MS C 1.04 masih harus diverifikasi lewat `sub sp`:
       kalau bukan 0x6f96, urutannya dibalik dulu sebelum menulis kode. */
    /* ⭐ KOREKSI peta: ini BUKAN larik 8x0x28, melainkan DELAPAN penyangga
       40-byte terpisah, dipakai dalam DUA KELOMPOK EMPAT: (08,30,58,80)
       dioper ke pickpart, (a8,d0,f8,120) ke panggilan berikutnya. */
    int  e08[20];              /* 0008  larik INT */
    int  e30[20];              /* 0030  larik INT */
    int  e58[20];              /* 0058  larik INT */
    int  e80[20];              /* 0080  larik INT */
    int  ea8[20];              /* 00a8  larik INT (ditulis per kata) */
    int  ed0[20];              /* 00d0  larik INT (ditulis per kata) */
    int  ef8[20];              /* 00f8  larik INT (ditulis per kata) */
    int  e120[20];              /* 0120  larik INT (ditulis per kata) */
    char lvlbuf[264];           /* 0148 */
    char recs[1500];            /* 0250 */
    char objs[900];             /* 082c */
    char basebuf[420];          /* 0bb0 */
    char buf0d54[850];          /* 0d54 */
    char ytop[3000];            /* 10a6 */
    char big[18000];            /* 1c5e */
    char buf62ae[2884];         /* 62ae */
    char buf6df2[300];          /* 6df2 */
    int  p1;                    /* 6f1e  dikira bagian penyangga, ternyata int */
    char g3[2];                 /* 6f20 */
    int  buf6f22[50];           /* 6f22  larik INT (dibaca per kata) */
    int  i;                     /* 6f86  pencacah loop, dipakai 9 kali */
    char g1[2];                 /* 6f88  tak terreferensi */
    int  cnt2;                  /* 6f8a */
    int  j;                     /* 6f8c */
    char g2[2];                 /* 6f8e  tak terreferensi */
    int  n;                     /* 6f90 */
    int  k;                     /* 6f92 */
    char m;                     /* 6f94  ⚠ CHAR, bukan int -- biner memakai
                                   `mov byte ptr [bp+6f94],al` lalu
                                   `xor ah,ah` tiap kali dibaca */

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
    /* Tiga arsip lagi dibuka, masing-masing dengan penanganan galat yang
       SAMA PERSIS (34 byte tiap blok). ⚠ 0x72a bernama `seed` di berkas lain
       padahal di sini jelas pegangan berkas -- nama menyesatkan, tidak
       diganti (aturan satu alamat satu nama). */
    seed = open(0x963, 0x8004);
    if (seed == -1) {
        printf(0x957);
        return;
    }
    fh = open(0x969, 0x8004);
    if (fh == -1) {
        printf(0x957);
        return;
    }
    objfh = open(0x96f, 0x8004);
    if (objfh == -1) {
        printf(0x957);
        return;
    }
    setfont();
    mode = 0;
    sub = 0x80;
    /* `mov ax,1` di-hoist lalu disimpan ke DUA tempat sesudah push argumen;
       urutan pancarannya [0x734] lalu [0x718] = KEBALIKAN urutan sumber. */
    goal = 1;
    lvl = 1;
    if (loadcon(-1) < 0) {
        printf(0x957);
        return;
    }
    f171f(2, 0x8ca, 0, nmax, postab);
    /* Pakai NAMA array, bukan alamat harfiah: yang benar memancarkan referensi
       ter-relokasi (slot wildcard), sedangkan angka harfiah memancarkan
       konstanta biasa -- kebetulan bytenya sama, tapi itu bukan rekonstruksi. */
    loadarc(fh, recbase, 0, recC, nzany, mark);
    loadarc(seed, base, 0, recB, nmechc, markf);
    j = loadarc(objfh, objtab, 0, recC, nzany, mark);
    loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
    pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
             buf6f22, e08, e80);
    fillans(0x1a8, base, seed, buf62ae, buf6df2, nmechc, ed0, ef8, recB,
            idtab, ea8, e120, ytop, lvl);
    f498c(ytop, nzany, recC, e08, e58);
    drawslot(ytop, nmechc, recB, ed0, ef8);
    animvm(state, nmechc, recB, ef8, e120, nzany, recC, e58, e80);
    do {
        m = getkey();
    } while (m != 0xd && m != 0x1b);
    /* ⚠ Ketiga lompatan ini menuju 0x10E8, jauh di ujung fungsi. Selama
       badan sesudahnya belum ditulis, labelnya dekat sehingga kompiler
       memancarkan JMP PENDEK (2 byte) padahal aslinya JMP NEAR (3 byte).
       Selisih 1 byte x3 itu HILANG SENDIRI begitu sisa fungsi ditulis --
       jangan dikejar. */
    if (m == 0x1b)
        goto quit;
    if (credits() == -1)
        goto quit;
    if (askopts() == -1)
        goto quit;
    sndok = sndini();
    /* ⚠ 0x5a5b itu `rnd` (generator acak), BUKAN rutin suara -- modulnya
       kebetulan bernama snd1.asm. Jadi ini MEMANASKAN generator acak
       20 kali, bukan membunyikan apa pun. */
    for (i = 0; i < 0x14; i++)
        rnd(1);
    /* 0x0450 -- gelung utama program. */
    for (;;) {
        k = 1;
        mode = mainmenu();
        if (mode == -1)
            goto quit;
        /* ⭐ SWITCH PADAT (beda dengan bentuk JARANG di pickvar): kompiler
           memancarkan `si = mode - 1; if (si >= 4) default; shl si,1;
           jmp cs:[si+tabel]` dengan tabel 4 entri di 0x0480. Bentuk ini
           dipilih kalau nilai case-nya rapat; yang jarang memakai tabel
           pasangan nilai/label yang dipindai mundur.
           Urutan case di sumber = urutan ALAMAT badannya, sama seperti
           bentuk jarang: badan 0x0467 (case 2,3,4) sebelum 0x0478 (case 1). */
        switch (mode) {
        case 2:
        case 3:
        case 4:
            shufflg = 1;
            lvl = lvlmenu();
            if (lvl == -1)
                continue;
            break;
        case 1:
            shufflg = 0;
            break;
        }
        /* Switch PADAT kedua, tabel di 0x04F3. Urutan case lagi-lagi mengikuti
           urutan ALAMAT badannya: 0x4A0(case 2), 0x4BA(3), 0x4D4(4), 0x4E2(1). */
        switch (mode) {
        case 2:
            lvl2 = 1;
            if (lvl == 1)
                lvl3 = 1;
            else
                lvl3 = 2;
            break;
        case 3:
            lvl3 = 1;
            if (lvl == 1)
                lvl2 = 1;
            else
                lvl2 = 2;
            break;
        case 4:
            lvl3 = 3;
            lvl2 = 2;
            break;
        case 1:
            sub = 7;
            lvl3 = 1;
            lvl2 = 1;
            break;
        }
    restart:
        goal = 1;
        /* ⭐ BENTUK SWITCH KETIGA: RANTAI PERBANDINGAN (0x05F1). Kalau nilai
           case-nya cuma sedikit, MS C 1.04 tidak membuat tabel sama sekali --
           ia memancarkan `cmp ax,2 / jne .. / jmp badan` berurutan. Tetap
           dikenali sebagai switch karena blok ujinya diletakkan SESUDAH badan
           dan dicapai lewat `jmp` ke depan, persis seperti dua bentuk lain. */
        switch (mode) {
        case 2:
        case 3:
            sub = goalmenu();
            if (sub == -1)
                continue;
            if (loadcon(-1) < 0)
                goto quit;
            if (mode == 3)
                setzany(nzany + nmechc, state, lvl2, markf, mark);
            if (k == 1) {
                /* Badan 0x566 (case 3) sebelum 0x56F (case 2) -> case 3 dulu. */
                switch (mode) {
                case 3:
                    if (menu11() == -1)
                        continue;
                    break;
                case 2:
                    if (menu9() == -1)
                        continue;
                    break;
                }
            }
            k = 0;
            f171f(mode, 0x922, sub, nmax, postab);
            loadarc(fh, recbase, 0, recC, nzany, mark);
            if (lvl3 == 1)
                n = 0;
            else
                n = 1;
            loadarc(seed, base, n, recB, nmechc, markf);
            break;
        }
        /* Lima penugasan nol di-hoist dari satu `xor ax,ax` yang juga jadi
           argumen; urutan pancarannya KEBALIKAN urutan sumber. */
        pass = 0;
        p1 = 0;
        failed = 0;
        slot = 0;
        curz = 0;
        j = loadarc(objfh, objtab, 0, recC, nzany, mark);
        loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
        p1++;
        /* Switch PADAT ketiga (tabel 0x10CA, 4 entri) -- ini yang memuat
           BADAN UTAMA fungsi, 0x065F..0x10C9 (~2.660 byte). Urutan case
           mengikuti alamat badan: 0x065F(4), 0x0A3B(2), 0x0C03(3), 0x0E06(1).
           default melompat ke 0x450 = `continue`.
           ⏳ Badan case 2, 3, 1 BELUM ditulis; dibiarkan kosong dulu supaya
           bentuk tabel padat 4-entri tetap terbangkitkan. */
        switch (mode) {
        case 4:
            if (menu12() == -1)
                continue;
        reset:
            /* 0x0668 -- juga sasaran `goto` dari hasil runplay == 0FEh. */
            schi = 0;
            sclo = 0;
            ta = 5;
            tx = 0x140;
            count = 4;
            hintshown = 0;
            g7e8 = 0;
            cursel = 0;
            failed = 0;
            sub = 0;
            both = 0;
            /* Aslinya BERBAGI register: `mov bx,140h` dipakai untuk tx lalu
               `sub bx,14h` untuk range. Menulis 0x140-0x14 sebagai konstanta
               memberi simpan-langsung, bukan pengurangan. */
            range = tx - 0x14;
            pickmax();
            goal = 6;
            /* 0x06AB -- gelung permainan. Keluar ke 0x0A2E. */
            while (goal > 0) {
                if (cursel == -1)
                    break;
                if (hintshown != 0)
                    break;
                if (lvl == 1)
                    goal = 1;
                if (failed != 0)
                    goto redo;
                tinit = 1;
                /* Kosongkan kolom pertama tiap record. Batasnya (0x78=120 dan
                   0x23=35) COCOK dengan ukuran penyangga di peta bingkai:
                   recs 1.500/12 = 125 dan basebuf 420/12 = 35. Dua temuan
                   yang saling menguatkan. */
                for (i = 0; i < 0x78; i++)
                    recs[i * 0xc] = 0;
                for (i = 0; i < 0x23; i++)
                    basebuf[i * 0xc] = 0;
                sub++;
                if (loadcon(-1) < 0) {
                    printf(0x957);
                    return;
                }
                setmark(nzany + nmechc, state, lvl, markf, mark);
                f171f(2, 0x922, sub, nmax, postab);
                p1 = 1;
                /* Tiga nol di-hoist dari satu `xor ax,ax` yang juga jadi
                   argumen; pancarannya kebalikan urutan sumber. */
                slot = 0;
                curz = 0;
                pass = 0;
                j = loadarc(fh, recbase, 0, recC, nzany, mark);
                if (lvl3 == 1)
                    n = 0;
                else
                    n = 1;
                /* Hasilnya ditampung j juga -- ada `mov [bp+6f8c],ax` yang
                   ditunda sampai sebelum panggilan berikutnya. */
                j = loadarc(seed, base, n, recB, nmechc, markf);
                j = loadarc(objfh, objtab, 0, recC, nzany, mark);
                loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
                pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
                         buf6f22, e08, e80);
                fillans(0x1a8, base, seed, buf62ae, buf6df2, nmechc, ed0, ef8,
                        recB, idtab, ea8, e120, ytop, lvl);
                goto after;
            redo:
                /* 0x08A6 -- jalur pintas kalau `failed` sudah diset: lewati
                   seluruh pemuatan ulang, cukup gambar ulang papannya. */
                p1++;
                f171f(2, 0x922, sub, nmax, postab);
            after:
                f498c(ytop, nzany, recC, e08, e58);
                drawslot(ytop, nmechc, recB, ed0, ef8);
                redraw();
                /* 21 argumen -- panggilan terbesar di seluruh biner. */
                cursel = runplay(ytop, nmechc, recB, ids, nmechb, ea8, lvl,
                                 ed0, e120, ef8, buf62ae, buf6df2, nzany,
                                 e08, e30, e80, recC, e58, ytop, big,
                                 buf0d54);
                if (cursel == 0xfe)
                    goto reset;
                if (cursel == -1)
                    goto done1;
                failed = animvm(state, nmechc, recB, ef8, e120, nzany, recC,
                                e58, e80);
                do {
                    m = getkey();
                } while (m != 0x20 && m != 0x1b);
                if (m == 0x1b) {
                    cursel = -1;
                    goto done1;
                }
                if (lvl == 1)
                    autofill(0x1a8, base, seed, buf62ae, buf6df2, nmechc, ed0,
                             ef8, recB, idtab, ea8, e120, ytop, lvl);
            done1:
                /* Tanda-tangan autofill PERSIS sama dengan fillans (14 arg,
                   urutan identik) -- keduanya mengisi papan, bedanya sumber
                   jawabannya. */
                if (lvl == 1)
                    goal++;
                goal--;
            }
            /* 0x0A2E -- ekor case 4. Tidak pernah jatuh ke bawah: kalau
               dibatalkan kembali ke menu, kalau tidak ulangi dari `reset`. */
            if (cursel == -1)
                continue;
            goto reset;
        case 2:
            failed = 1;
            cursel = 0;
            if (p1 == 1) {
                /* Ditulis per KATA ke ea8 (`mov [bp+si+a8h],bx`), jadi
                   penyangga 40-byte itu sebenarnya larik 20 int. */
                for (i = 0; i < nmechc; i++) {
                    ea8[i] = -1;
                    ed0[i] = -1;
                    e120[i] = -1;
                    ef8[i] = -1;
                }
                pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
                         buf6f22, e08, e80);
            }
        again2:
            f498c(ytop, nzany, recC, e08, e58);
            drawslot(ytop, nmechc, recB, ed0, ef8);
            while (failed != 0) {
                failed = 0;
                redraw();
                cursel = pickloop(ytop, nmechc, recB, ids, nmechb, ea8, lvl,
                                  ed0, e120, ef8, buf62ae, buf6df2);
            }
            if (cursel == -1)
                goto endcase2;
            failed = animvm(state, nmechc, recB, ef8, e120, nzany, recC, e58,
                            e80);
            cursel = waitkey();
            /* Switch RANTAI atas hasil waitkey (0x0BE6). */
            switch (cursel) {
            case 0:
                if (lvl == 1)
                    autofill(0x1a8, base, seed, buf62ae, buf6df2, nmechc, ed0,
                             ef8, recB, idtab, ea8, e120, ytop, lvl);
                f171f(2, 0x922, sub, nmax, postab);
                break;
            case -1:
                continue;
            default:
                goto restart;
            }
            /* 0x0BF6 -- ekor case 2: kalau belum dibatalkan, ulangi dari
               0x0AB2; kalau dibatalkan, ulangi dari `restart`. */
            if (cursel != -1)
                goto again2;
            goto restart;
        endcase2:
            break;
        case 3:
            failed = 1;
            cursel = 0;
            if (p1 == 1) {
                /* Empat penyangga SISANYA (08, 30, 58, 80) juga larik int --
                   ditulis per kata, sama seperti A8/D0/F8/120. */
                for (i = 0; i < nzany - 1; i++) {
                    e08[i] = -1;
                    e30[i] = -1;
                    e80[i] = -1;
                    e58[i] = -1;
                }
            }
            i = nzany - 1;
            /* 0x4BA itu recC + 2 kata, jadi recC[i*3+2] -- BUKAN simbol baru
               (aturan: satu alamat satu nama). */
            cnt2 = nvar(recC[i * 3 + 2], buf6f22);
            for (j = 0; j < cnt2; j++) {
                /* recbase di berkas ini bertipe int (main mengisinya dengan alamat),
                   jadi butuh cast; urutan operan tetap bentuk PENUNJUK. */
                if ((buf6f22[j] * 0xc + (char *)recbase)[1] == sub)
                    break;
            }
            e08[i] = j;
            e30[i] = buf6f22[j];
            e80[i] = recC[i * 3 + 2];
            e58[i] = -1;
            fillans(0x1a8, base, seed, buf62ae, buf6df2, nmechc, ed0, ef8,
                    recB, idtab, ea8, e120, ytop, lvl);
            drawslot(ytop, nmechc, recB, ed0, ef8);
            break;
        case 1:
            break;
        }
    }
quit:
    ;
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
