/* FUN_1000_0082 @ 1000:0082, 4.219 byte — main().
 *
 * ⏳ DRAF — SELURUH fungsi sudah tertulis (tidak ada blok yang belum digarap).
 * Panjang 4.182 vs 4.219 asli. TERJAJAR 2.635/4.219 (62,5%).
 * SUDAH ikut di-link (stub main sudah dicabut). Ukur dengan:
 *     pwsh src_c/build/compile.ps1 -Name main_
 *     python src_c/verify/aligncmp.py main_ 82 4219
 *     python src_c/verify/aligncmp.py main_ 82 4219 --sbs <addr> <n> <geser>
 *
 * ⚠ PAKAI METRIK TERJAJAR, BUKAN POSISI (lihat src_c/README.md).
 *
 * ⭐⭐ AKAR MASALAH GESERAN DITEMUKAN (2026-07-31). SEMUA lokal kita persis
 * 2 byte LEBIH RENDAH dari asli -- terbukti dengan mendaftar tiap slot yang
 * kita rujuk: 0x11E/0x146/0x24E/0x82A/0xBAE/0xD52/0x10A4/0x1C5C/0x62AC/0x6DF0
 * berbanding 0x120/0x148/0x250/0x82C/0xBB0/0xD54/0x10A6/0x1C5E/0x62AE/0x6DF2.
 * Penyebabnya BUKAN deklarasi lokal (semua ukurannya sudah pas dan saling
 * terkunci oleh offset yang terlihat di biner), melainkan TEMP: aslinya
 * memesan 8 byte temp (bp+00..07), kita 6.
 *
 * ⚠ KOREKSI dugaan pertama. Saya sempat menyimpulkan "ada satu ekspresi yang
 * butuh slot temp KEEMPAT". Itu KELIRU. Dihitung langsung: di SELURUH 4.219
 * byte biner asli TIDAK ADA SATU PUN rujukan ke slot temp ([bp], [bp+2],
 * [bp+4], [bp+6]) -- satu-satunya rujukan bp rendah adalah `lea [bp+8]`
 * (alamat e08), dua kali. Punya kita sama persis, hanya `lea [bp+6]`.
 * Jadi kedua versi memesan ruang temp yang TIDAK PERNAH DIPAKAI; aslinya
 * memesan 4 kata, kita 3. Pemicunya bukan pemakaian temp, melainkan
 * kedalaman ekspresi yang DIHITUNG kompiler saat memesan bingkai.
 * Mencarinya harus lewat perbandingan bentuk ekspresi, bukan lewat mencari
 * instruksi yang menyentuh slot temp -- karena tidak ada.
 *
 * ✅ DIATASI 2026-07-31 dengan PERANCAH: `int tpad;` sebagai lokal PERTAMA.
 * Lokal `int` tak terpakai TETAP dialokasikan (beda dari `char x[2]` yang
 * dibuang), jadi ia menggeser semua lokal naik 2 byte TANPA mengubah ukuran
 * atau urutan penyangga mana pun. Hasilnya:
 *     GLOBAL 2.852 -> 3.215 / 4.219 (67,6% -> 76,2%)
 *     geseran 16 -> 4, panjang -25 -> -12
 * ⚠ Ini PERANCAH, bukan kebenaran: pemicu kedalaman ekspresi yang membuat
 * kompiler asli memesan kata temp KEEMPAT masih belum ketemu. Buang `tpad`
 * begitu ketemu. Bedanya dengan percobaan lama: ganjal di DEPAN tidak merusak
 * offset penyangga mana pun, sedangkan membesarkan `lvlbuf` merusaknya.
 *
 * ⚠⚠ KESALAHAN STRUKTUR YANG BELUM DIPERBAIKI, terlokalisasi 2026-07-31 di
 * 0x0C14. Aslinya:
 *     cmp [bp+6F1Eh],1
 *     je  0C19h          <- badan `if`
 *     jmp 0D15h          <- lompat JAUH melewati SELURUH badan
 * Punya kita cuma `jne 0C42h`. Sebabnya bukan bentuk syarat: badan `if` kita
 * BERAKHIR TERLALU CEPAT. Di biner asli seluruh blok 0x0C43..0x0D14 masih DI
 * DALAM `if` itu; di sumber kita blok yang sama berjalan TANPA SYARAT.
 * (Kompiler memakai `je`+`jmp` justru KARENA jaraknya > 127 byte; `jne` pendek
 * kita muat karena badannya kependekan.)
 * Kode di 0x0C43 dan sesudahnya sudah cocok instruksi-per-instruksi.
 * ⚠ SUDAH DICOBA: memindah kurung tutup ke SESUDAH `fillans(...)` (yang jelas
 * benar -- `je 0C1Bh`+`jmp 0D17h` lalu jadi COCOK PERSIS dengan aslinya, dan
 * ujung `if`-nya mendarat tepat). TAPI wilayah 0x0C00..0x0D40 justru MEMBURUK
 * 291 -> 275 byte cocok, dan GLOBAL 3.378 -> 3.276. Sebabnya: memasukkan
 * `fillans(...)` ke dalam `if` mengubah tekanan register SE-BLOK, jadi kode
 * panggilan itu sendiri berubah. Jadi letak kurungnya memang salah, tapi
 * MEMPERBAIKINYA SENDIRIAN merugikan -- ada penyesuaian lain di blok yang
 * sama yang harus dilakukan BERSAMAAN. Dibatalkan sampai itu ketemu.
 *
 * ⚠ JANGAN "memperbaiki"-nya dengan membesarkan salah satu penyangga.
 * Percobaan: menambah 2 byte ke lvlbuf menaikkan TERJAJAR 2.682 -> 3.470 dan
 * membuat SEMUA slot cocok -- tapi itu KOMPENSASI, bukan kebenaran: ia
 * menggeser lvlbuf/recs ke offset yang jelas-jelas salah menurut biner.
 * Angka 3.470 itu berguna sebagai BUKTI DIAGNOSIS (membuktikan selisihnya
 * memang persis 2 byte dan seragam), bukan sebagai hasil.
 *
 * ⚠ Pengganjal `char x[2]` yang TIDAK dirujuk DIBUANG kompiler; `char x[3]`
 * dan `char x[4]` dialokasikan (keduanya jadi 4 byte). Jadi aturan lama
 * "array selalu dialokasikan" tidak berlaku untuk array 2-byte tak terpakai.
 *
 * ⚠ 13 byte DIBLOKIR bug alat, bukan soal sumber: dua instruksi (0x00B9 dan
 * 0x10F1) mengakses kata pertama DGROUP, tapi gendata.py membuang alamat
 * DGROUP 0..3 (penyaring `START <= a` dengan START = 4). Memperbaikinya
 * menyentuh penataan DGROUP yang sekarang 100% cocok -- KEPUTUSAN USER.
 *
 * PETA LABEL (semua terverifikasi dari disassembly):
 *   quit=0x10E8  restart=0x050E  reset=0x0668 (DUA jalur masuk)
 *   redo=0x08A6 (pintas KE DEPAN)  after=0x08C3  done1=0x0A1C
 *   again2=0x0AB2  again3=0x0D15  again1=0x0E0C  redraw1=0x1013
 *   gelung permainan 0x06AB keluar ke 0x0A2E
 *   nilai balik 0FEh = "waktu habis, ulangi" (konvensi sama dgn pickvar)
 *
 * ⭐ TANDA TANGAN YANG SUDAH DITURUNKAN (dipakai ulang belasan kali):
 *   runplay(21) = pickloop(12) diikuti runfill(9), urutan sama.
 *   pickloop: (ytop, nmechc, recB, ids, nmechb, ea8, lvl, ed0, e120, ef8,
 *              buf62ae, buf6df2)
 *   runfill : (nzany, e08, e30, e80, recC, e58, ytop, big, buf0d54)
 *   pickpart: (4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
 *              buf6f22, e08, e80)
 *   fillans dan autofill: tanda tangan IDENTIK, 14 argumen.
 *   animvm  : (state, nmechc, recB, ef8, e120, nzany, recC, e58, e80)
 *
 * BERIKUTNYA: kejar geseran satu per satu dengan --sbs, mulai dari
 * +9 @0x13D (yang +7 @0xD6 diblokir bug gendata di atas).

 */

extern int  level_;             /* @0x740 */
extern int  ytop_;              /* @0x84a */
extern int  markf[];            /* @0x76a */
extern int  curopt;             /* @0x522 */
extern int  ctx;                /* @0x524 */
extern int  objtab;             /* @0x73e */
extern int  base;               /* @0x73a */
extern char *recbase;           /* @0x73c -- char* : biner memuatnya LANGSUNG
                                   ke SI, bukan lewat AX (lihat README) */
/* Dua alamat ini BELUM pernah dinamai di berkas lain; keduanya juga bukan
   awal simbol yang sudah ada, jadi aman diberi nama (lihat aturan gendata). */
extern int  mark[];             /* @0x742 */
extern int  prevx;              /* @0x266 */
extern int  prevtop;            /* @0x262 */
extern char pbufA[];            /* buffer halaman @0x26c */
extern char pbufB[];            /* buffer halaman @0x284 */
extern int  page;               /* @0x2e0 */
extern int  page2;              /* @0x2e2 */
/* 0x846 = `miscfh`: diisi hasil open() lalu diteruskan sebagai argumen
   PERTAMA ke loadarc()/load(). Namanya sudah tepat -- catatan lama yang
   menyebutnya "mode permainan" (dan nama lama `mode_`) sudah dikoreksi. */
extern int  miscfh;              /* @0x846 */
extern int  mechfh;             /* @0x72a  arsip "mechs" */
extern int  fh;                 /* @0x72c  arsip "graph" */
extern int  objfh;              /* @0x72e  arsip "animate" */
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
/* ⚠ `sclo` dipakai di sini sebagai satu `long` 32-bit, bukan `int`. Aslinya
   menolkan skor dengan DUA simpanan-immediate (`mov [732h],0` lalu
   `mov [730h],0`) -- itu pola penugasan nol pada `long`, bukan dua `int`
   yang akan memakai ulang AX=0 dan cuma 3 byte masing-masing. Tanpa komentar
   @ supaya gendata tidak memanennya ulang; gdata.c tetap memancarkan int. */
extern long sclo;
extern int  count;              /* @0x82c */
extern int  both;               /* @0x844 */
extern int  hintshown;          /* @0x848 */
extern int  range;              /* @0x830 */
/* Dua alamat ini belum pernah dinamai; keduanya slot 2-byte bebas (0x2e6=curz
   dan 0x7e6=zcnt masing-masing hanya 2 byte). Nama sengaja netral karena
   maknanya belum terbukti -- baru terlihat diset 0 lalu diuji != -1. */
extern int  cursel;             /* @0x2e8 */
extern int  g7e8;               /* @0x7e8 */
extern int  nmech;              /* @0x3ac */
extern int  cur;                /* @0x51c */
extern int  curz;               /* @0x2e6 */
extern int  slot;               /* @0x51a */
extern int  failed;             /* @0x842 */
extern int  pass;               /* @0x71c */
extern int  lvl2;               /* @0x736 */
extern int  lvl3;               /* @0x738 */
extern int  shufflg;            /* @0x794 */
extern int  sndok;              /* @0x71a  hasil sndini(); belum pernah dinamai */
extern int  state[];            /* @0x4f2 */
/* Tabel byte 9 entri, dipakai mengisi recB[i*3+2] di case 1. Ada di dalam
   blok pengisi (simbol bernama terdekat: ytop_ @0x84a, hintstr @0xa26),
   jadi aman dinamai. Maknanya belum dianalisa lebih jauh. */
extern char rowtab[];           /* @0x870 */
extern char idtab[];            /* @0x2ea */
extern int  scrmode;            /* @0x3b0 */
extern int  g83a;               /* @0x83a  salinan _TOP selama permainan */
/* _TOP dan _BASE ada di DUA kata pertama DGROUP dan disumbang C.OBJ (crt0),
   BUKAN gdata.c -- makanya tidak boleh diberi komentar alamat di sini.
   `main` MENYIMPAN _TOP di awal dan MENGEMBALIKANNYA saat keluar, karena
   bingkai tumpukannya sendiri 28.566 byte. */
extern int  _TOP;

main()
{
    /* Deklarasi ditulis supaya OFFSET-nya jatuh persis seperti peta di atas.
       Urutan alokasi lokal MS C 1.04 masih harus diverifikasi lewat `sub sp`:
       kalau bukan 0x6f96, urutannya dibalik dulu sebelum menulis kode. */
    /* ⭐ KOREKSI peta: ini BUKAN larik 8x0x28, melainkan DELAPAN penyangga
       40-byte terpisah, dipakai dalam DUA KELOMPOK EMPAT: (08,30,58,80)
       dioper ke pickpart, (a8,d0,f8,120) ke panggilan berikutnya. */
    /* ⏳ PERANCAH, bukan klaim tentang sumber asli. Aslinya memesan 4 kata
       temp, kita 3 -- selisih 2 byte yang menggeser SEMUA lokal ke bawah dan
       menutupi divergensi lain di hilirnya. Ganjal di DEPAN ini menggeser
       semuanya kembali TANPA mengubah ukuran atau urutan penyangga mana pun
       (beda dari percobaan lama yang membesarkan `lvlbuf` dan justru merusak
       offset lvlbuf/recs). BUANG kalau pemicu kedalaman ekspresi ketemu. */
    int  tpad;                  /* 0006..0007 */
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
    int  i2;                    /* 6f88  pencacah kedua */
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
    /* ⚠ Urutan DIBACA dari urutan MUATAN REGISTER di biner, bukan dari urutan
       simpanannya: aslinya memuat ax=&ytop, bx=_TOP, cx=&basebuf, dx=&recs
       lebih dulu, baru memakai ulang ax untuk &objs dan &lvlbuf. */
    ytop_ = (int)ytop;
    g83a = _TOP;
    base = (int)basebuf;
    recbase = (char *)recs;
    objtab = (int)objs;
    level_ = (int)lvlbuf;
    for (i = 0; i < 0x14; i++)
        markf[i] = 1;
    for (i = 0; i < 0x14; i++)
        mark[i] = 1;
    /* Empat penugasan konstanta ini dipancarkan dalam urutan TERBALIK
       (aturan MS C 1.04 yang sudah dikenal), jadi urutan sumbernya
       page, page2, prevtop, prevx -- bukan sebaliknya. */
    /* Urutan dibaca dari MUATAN: ax=140h, bx=26Ch, cx=284h, dx=8004h. */
    prevx = 0x140;
    prevtop = 0x140;
    /* ⭐⭐ ALAMAT SIMBOL, bukan literal. 0x26c dan 0x284 ternyata `pbufA`/
       `pbufB` (dideklarasikan di drawball.c). `&larik` memancarkan
       `mov reg,offset` + simpanan yang DITUNDA — persis bentuk asli
       (`mov bx,26ch / mov cx,284h` lalu kedua simpanan sesudah `push`).
       Bentuk literal memancarkan simpanan-immediate 6 byte dan menggeser
       seluruh fungsi; bentuk `page + 0x18` kebetulan panjangnya benar tapi
       kodenya salah. GLOBAL 4.205 -> 4.215.
       ⭐ PELAJARAN: sebelum menerima sebuah literal alamat sebagai literal,
       CEK apakah ia simbol DGROUP yang sudah dikenal. Satu grep. */
    page = (int)pbufA;
    page2 = (int)pbufB;
    miscfh = open(0x952, 0x8004);
    if (miscfh == -1) {
        printf(0x957);
        return;
    }
    loadarc(miscfh, level_, 1);
    /* Enam muatan awal dari arsip yang sama. Argumen ke-3 = nomor record,
       ke-4 = alamat tujuan di DGROUP. */
    load(miscfh, level_, 0, 0x31c);
    load(miscfh, level_, 1, 0x364);
    load(miscfh, level_, 2, 0x526);
    load(miscfh, level_, 3, 0x586);
    load(miscfh, level_, 4, 0x5e6);
    load(miscfh, level_, 0x13, 0x646);
    /* Tiga arsip lagi dibuka, masing-masing dengan penanganan galat yang
       SAMA PERSIS (34 byte tiap blok). */
    mechfh = open(0x963, 0x8004);
    if (mechfh == -1) {
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
    /* ⭐ `goal`/`lvl` (keduanya = 1) DI DEPAN `sub`: nilai 1 dipakai DUA kali
       sehingga masuk register dan dimaterialisasi di PUNCAK blok — asli
       memancarkan `mov ax,1` SEBELUM `mov [sub],80h`. Simpanannya sendiri
       tetap ditata ulang ([0x734] lalu [0x718] = kebalikan urutan sumber). */
    goal = 1;
    lvl = 1;
    sub = 0x80;
    if (loadcon(-1) < 0) {
        printf(0x957);
        return;
    }
    f171f(2, 0x8ca, 0, nmax, postab);
    /* Pakai NAMA array, bukan alamat harfiah: yang benar memancarkan referensi
       ter-relokasi (slot wildcard), sedangkan angka harfiah memancarkan
       konstanta biasa -- kebetulan bytenya sama, tapi itu bukan rekonstruksi. */
    loadarc(fh, recbase, 0, recC, nzany, mark);
    loadarc(mechfh, base, 0, recB, nmechc, markf);
    j = loadarc(objfh, objtab, 0, recC, nzany, mark);
    loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
    pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
             buf6f22, e08, e80);
    fillans(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0, ef8, recB,
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
           memancarkan `si = mode - 1` lalu `if (si >= 4) default` lalu `shl si,1`
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
            /* ⭐ Sama seperti situs 0x0256: nilai 1 dipakai dua kali, jadi
               dimaterialisasi sebelum simpanan `sub`. */
            lvl3 = 1;
            lvl2 = 1;
            sub = 7;
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
        /* ⭐ URUTAN LABEL: `case 3:` DULU. Rantai perbandingan `switch`
           dipancarkan KEBALIKAN urutan `case` di sumber (probeB), jadi
           sumber (3,2) memberi rantai `cmp 2` lalu `cmp 3` seperti asli.
           Karena kedua label BERBAGI badan, menukarnya tidak mengubah
           tata letak apa pun. GLOBAL 4.201 -> 4.203. */
        case 3:
        case 2:
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
            loadarc(mechfh, base, n, recB, nmechc, markf);
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
            /* ⚠ SUDAH DICOBA & GAGAL (3 pendekatan, 9 bentuk): membuat
               schi/sclo dipancarkan sebagai KONSTANTA LANGSUNG seperti asli
               (`mov [mem],0`, 6 byte) alih-alih lewat AX (3 byte). Diuji:
               (a) 5 urutan pernyataan berbeda, (b) `schi = sclo = 0`,
               (c) rantai enam nol `a = b = ... = 0` dua arah, (d) menulis 0x0.
               SEMUANYA memberi byte IDENTIK. MS C 1.04 rupanya memakai AX
               untuk SEMUA penugasan nol dalam satu kelompok begitu AX=0
               dimaterialisasi, dan rantai dikompilasi sama persis dengan
               pernyataan terpisah. Selisihnya 6 byte; pemicunya kemungkinan
               di luar bentuk penugasan itu sendiri. */
            /* ⚠ TERTUTUP TOTAL: memindah nol ke DEPAN `sclo = 0` menurunkan
               GLOBAL 3.378 -> 3.270 (walau geseran 4 -> 2, TERJAJAR naik).
               Diuji ulang 2026-07-31 dengan MEMINDAH SATU penugasan saja,
               keenam-enamnya bergantian: semua menghasilkan .OBJ BYTE-IDENTIK
               (SHA1 af9b4ad4637d0cf8). Jadi urutan sumber di deretan simpanan
               bernilai sama TIDAK memberi sinyal; biayanya murni karena nol
               menjadi HIDUP lebih awal sehingga 0x140 terusir dari BX ke AX.
               Pengungkitnya harus di luar penataan ulang sumber. */
            /* ⭐ SATU nol dipindah KE DEPAN `sclo = 0` supaya nolnya HIDUP
               lebih awal: asli memancarkan `xor ax,ax` di 0x0668 lalu
               memakai AX untuk ENAM simpanan, sehingga 0x140 terusir ke BX.
               Keenam nol memberi hasil BYTE-IDENTIK (SHA1 af9b4ad4637d0cf8),
               jadi mana yang dipindah tidak penting.
               ⚠ Perubahan ini dulu MENURUNKAN (3.378 -> 3.270) dan tercatat
               sebagai gagal. Yang berubah: sesudah `page2` diperbaiki,
               panjangnya tidak lagi bergeser -- dan bentuk yang sama kini
               memberi 3.707 -> 3.910. Contoh paling jelas bahwa daftar
               "dicoba & gagal" KEDALUWARSA. */
            hintshown = 0;
            sclo = 0;
            /* Urutan DIBACA dari muatan: `mov bx,140h` DULU (jadi `tx`
               pernyataan pertama), lalu simpanan-immediate `ta`, lalu
               `sub bx,14h` yang menempel pada `range`, baru `count`. */
            tx = 0x140;
            ta = 5;
            range = tx - 0x14;
            count = 4;
            g7e8 = 0;
            cursel = 0;
            failed = 0;
            sub = 0;
            both = 0;
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
                /* ⭐ `slot = 0` DIPINDAH KE DEPAN `p1 = 1`: nolnya juga jadi
                   ARGUMEN panggilan berikutnya, dan asli memancarkan
                   `xor ax,ax` di PUNCAK blok. GLOBAL 4.173 -> 4.175. */
                slot = 0;
                p1 = 1;
                /* Tiga nol di-hoist dari satu `xor ax,ax` yang juga jadi
                   argumen; pancarannya kebalikan urutan sumber. */
                curz = 0;
                pass = 0;
                j = loadarc(fh, recbase, 0, recC, nzany, mark);
                if (lvl3 == 1)
                    n = 0;
                else
                    n = 1;
                /* Hasilnya ditampung j juga -- ada `mov [bp+6f8c],ax` yang
                   ditunda sampai sebelum panggilan berikutnya. */
                j = loadarc(mechfh, base, n, recB, nmechc, markf);
                j = loadarc(objfh, objtab, 0, recC, nzany, mark);
                loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
                pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
                         buf6f22, e08, e80);
                fillans(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0, ef8,
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
                    autofill(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0,
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
            /* ⭐ Arah `!=` dengan badan DITUKAR — sama seperti kedua ekor
               `endcase` di bawah. Asli memancarkan `jne` lebih dulu. */
            if (cursel != -1)
                goto reset;
            continue;
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
                /* ⭐ `tail2`, BUKAN `endcase2`. Keduanya SETARA (endcase2 =
                   `break` yang akhirnya sampai ke `restart` juga), tapi
                   `goto endcase2` diruntuhkan jadi lompatan LANGSUNG ke
                   `restart`; asli melompat ke uji ekor di 0x0BF6.
                   Dipetakan lewat PENANDA, bukan ditebak. GLOBAL 4.203 -> 4.205. */
                goto tail2;
            failed = animvm(state, nmechc, recB, ef8, e120, nzany, recC, e58,
                            e80);
            cursel = waitkey();
            /* Switch RANTAI atas hasil waitkey (0x0BE6). */
            /* Urutan case mengikuti urutan ALAMAT badannya: badan `case -1`
               (jmp 0x450) ada di 0x0B7A, SEBELUM badan `case 0` di 0x0B7D. */
            switch (cursel) {
            case -1:
                continue;
            case 0:
                if (lvl == 1)
                    autofill(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0,
                             ef8, recB, idtab, ea8, e120, ytop, lvl);
                f171f(2, 0x922, sub, nmax, postab);
                break;
            default:
                goto restart;
            }
            /* 0x0BF6 -- ekor case 2: kalau belum dibatalkan, ulangi dari
               0x0AB2; kalau dibatalkan, ulangi dari `restart`. */
            /* ⭐ Syaratnya `== -1` dengan badan DITUKAR: asli memancarkan
               `je` lebih dulu lalu jatuh-tembus ke `goto again2`. Bentuk
               `!= -1` memberi `jne` dan menukar kedua `jmp` sesudahnya —
               semantiknya sama, byte-nya beda. */
        tail2:
            if (cursel == -1)
                goto restart;
            goto again2;
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
            i = nzany - 1;
            /* 0x4BA itu recC + 2 kata, jadi recC[i*3+2] -- BUKAN simbol baru
               (aturan: satu alamat satu nama). */
            cnt2 = nvar(recC[i * 3 + 2], buf6f22);
            for (j = 0; j < cnt2; j++) {
                if ((buf6f22[j] * 0xc + recbase)[1] == sub)
                    break;
            }
            e08[i] = j;
            e30[i] = buf6f22[j];
            e80[i] = recC[i * 3 + 2];
            e58[i] = -1;
            fillans(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0, ef8,
                    recB, idtab, ea8, e120, ytop, lvl);
            /* ⭐ KURUNG TUTUP DI SINI, bukan sebelum `i = nzany - 1`.
               fillans() ADA DI DALAM blok. Ini DITOLAK DUA KALI sebelumnya
               (3.378 -> 3.276 lewat GLOBAL, dan 291 -> 275 lewat metrik
               wilayah) -- kedua pengukuran itu dilakukan saat panjang fungsi
               masih bergeser, sehingga bentuk yang BENAR justru terukur buruk.
               Pada dasar yang panjangnya sudah lurus: 3.910 -> 4.169. */
            }
        again3:
            drawslot(ytop, nmechc, recB, ed0, ef8);
            f498c(ytop, nzany, recC, e08, e58);
            while (failed != 0) {
                failed = 0;
                /* 9 argumen ini persis EKOR daftar argumen runplay. */
                cursel = runfill(nzany, e08, e30, e80, recC, e58, ytop, big,
                                 buf0d54);
            }
            if (cursel == -1)
                goto endcase3;
            failed = animvm(state, nmechc, recB, ef8, e120, nzany, recC, e58,
                            e80);
            cursel = waitkey();
            /* Struktur ekor SAMA PERSIS dengan case 2, hanya argumen pertama
               f171f yang beda (3, bukan 2). */
            /* Sama seperti case 2: badan `case -1` (0x0DC8) SEBELUM `case 0`. */
            switch (cursel) {
            case -1:
                continue;
            case 0:
                f171f(3, 0x922, sub, nmax, postab);
                break;
            default:
                goto restart;
            }
        endcase3:
            /* ⭐ Syaratnya `== -1` dengan badan DITUKAR: asli memancarkan
               `je` lebih dulu lalu jatuh-tembus ke `goto again3`. Bentuk
               `!= -1` memberi `jne` dan menukar kedua `jmp` sesudahnya —
               semantiknya sama, byte-nya beda. */
            if (cursel == -1)
                goto restart;
            goto again3;
        case 1:
            cur = -1;
        again1:
            /* ⭐ `goal = 0` DULU: nolnya dipakai EMPAT kali (goal, pass, dan
               dua argumen f171f), dan asli memancarkan `xor ax,ax` di PUNCAK
               blok — sebelum `p1 = 1`. GLOBAL 4.169 -> 4.173. */
            goal = 0;
            p1 = 1;
            mode = 2;
            pass = 0;
            f171f(mode, 0x922, 0, 0, postab);
            mode = 1;
            goal = 1;
            f2fde();
            j = loadarc(mechfh, base, 1);
            for (i2 = 0; i2 < 9; i2++)
                recB[i2 * 3 + 2] = rowtab[i2];
            nmech = mkpal(mechfh, ytop, recB, i2, 1);
            cursel = review(ytop, 0, 0, 0, 0, cur);
            if (cursel == -1)
                continue;
            cursel = revdet(cur);
            if (cursel == -1)
                continue;
            if (cursel == 0xd)
                goto again1;
            if (loadcon(cur) < 0) {
                printf(0x957);
                return;
            }
            f171f(mode, 0x8ca, cur + 1, nmax, postab);
            p1 = 1;
            pass = 0;
            loadarc(fh, recbase, 0, recC, nzany, mark);
            loadarc(mechfh, base, 0, recB, nmechc, markf);
            j = loadarc(objfh, objtab, 0, recC, nzany, mark);
            loadarc(objfh, objtab + j * 0xc, 0, recB, nmechc, markf);
            pickpart(4, recbase, fh, big, buf0d54, nzany, e30, e58, recC,
                     buf6f22, e08, e80);
            fillans(0x1a8, base, mechfh, buf62ae, buf6df2, nmechc, ed0, ef8,
                    recB, idtab, ea8, e120, ytop, lvl);
        redraw1:
            f498c(ytop, nzany, recC, e08, e58);
            drawslot(ytop, nmechc, recB, ed0, ef8);
            animvm(state, nmechc, recB, ef8, e120, nzany, recC, e58, e80);
            /* 0x1075 -- tunggu tombol; ESC keluar ke menu, Enter ulangi case,
               SPASI maju ke mekanisme berikutnya lalu gambar ulang. */
            for (;;) {
                while (keyhit() == 0)
                    ;
                m = getkey();
                if (m == 0x1b)
                    break;
                if (m == 0xd)
                    goto again1;
                if (m == 0x20) {
                    goal = 1;
                    /* ⭐ literal 2, BUKAN `mode`: asli `mov bx,2 / push bx`,
                       kita `push [mode]`. GLOBAL 4.199 -> 4.201. */
                    f171f(2, 0x8ca, cur + 1, nmax, postab);
                    goto redraw1;
                }
            }
            break;
        }
    }
quit:
    /* 0x10E8 -- blok keluar. */
    bios10(scrmode);
    _TOP = g83a;
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
