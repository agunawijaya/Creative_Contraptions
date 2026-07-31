/* FUN_1000_18db @ 1000:18db (3.040 byte) — VM ANIMASI, penafsir skrip ANIMATE.
 *
 * Fungsi TERBESAR di game dan stub TERAKHIR yang tersisa. Dikerjakan BERTAHAP:
 * tahap ini baru PROLOG + kerangka; badan 18 case menyusul.
 *
 * ⚠ ADA TABEL DATA 72 byte DI TENGAH fungsi (0x23d4..0x241b) — 18 pasang
 * (nilai_case, alamat_badan) untuk switch bentuk PEMINDAIAN. Capstone berhenti
 * di situ tanpa bilang apa-apa; kode berlanjut lagi di 0x241c. Peta lengkapnya
 * ada di src_c/JOURNAL.md §Pengintaian animvm.
 *
 * ⚠ SEMBILAN argumen (bp+6E..7E). Bingkai 0x6a: temp 0x00..0x0d,
 * lokal 0x0e..0x69 (92 byte).
 *
 * Semantik opcode-nya TIDAK diturunkan ulang dari disassembly — jalur port
 * sudah memparsi ke-17 opcode dan memvalidasinya vs emulator, lihat
 * `port/cc/animvm.py`. Itu yang membuat f2823 selesai sekali kompilasi.
 *
 *   keyhit()=1791  showhint()=24bb  delay()=2692  f2714()=2714  f278e()=278e
 *   f2823()=2823  setball()=2a53  showsc()=2a86  waitn()=2b11  prompts()=2b77
 *   kbflush()=36ef  timedrw()=4c04  sndoff()=5a74  sndon()=5a76  sndsave()=5a7f
 *   bounce()=2504  shftr()=6600  f66fd()=66fd (modul keyio.asm; PUBDEF-nya F66FD, bukan `keyio`)  blit()=672f  fillrect()=6869
 *   printf()=6a48  text()=6453  putmsk()=6524 (modul blitmsk.asm; PUBDEF-nya
 *   PUTMSK, bukan `blitmsk` -- nama BERKAS != nama SIMBOL)
 *
 * ⏳ TAHAP 1: baru prolog. Angka penjajaran ada di JOURNAL.
 */

/* ⚠ `scrptr` sengaja `char *` (bukan `int` + cor) — lihat README §CAST
   PENUNJUK. Alamatnya sudah terdaftar di f2714.c, jadi tanpa komentar @ di
   sini supaya gendata tidak memanennya dua kali. */
extern char *scrptr;

extern int  prevtop;            /* @0x262 */
extern int  prevx;              /* @0x266 */
extern int  page2;              /* @0x2e2 */
extern int  ticks;              /* @0x2e4 */
extern int  goal;               /* @0x718 */
extern int *sndptr;             /* @0x720 */
extern int  sndmode;            /* @0x722 */
extern int  mode;               /* @0x792 */
extern int  failed;             /* @0x842 */
extern int  both;               /* @0x844 */
extern char hdrspr[];           /* @0x526 -- 3 sprite 96 byte: +0, +96, +192 */
extern char sndbuf[];           /* @0x670e */
extern int  curz;               /* @0x2e6 */
extern int  sub;                /* @0x3b2 */
extern int  slot;               /* @0x51a */
extern int  lvl;                /* @0x734 */
extern int  zflag[];            /* @0x796 */
extern int  fail[];             /* @0x7be */
extern int  zcnt;               /* @0x7e6 */
extern int  g7e8;               /* @0x7e8 */
extern char msgmech[];          /* @0x9dd */
extern char msgzany[];          /* @0xa01 */
extern char buf9c5[];           /* @0x9c5 -- penyangga; dioper ke bounce()
                                   dan blitmsk(). Perannya belum diturunkan,
                                   tapi HARUS bernama: literal alamat tidak
                                   memancarkan slot relokasi. */
extern int  ballx;              /* @0x260 */
extern int  bally;              /* @0x25e */
extern int  mflag;              /* @0x834 */
extern int  cur2;               /* @0x7f8 */
extern int  tx;                 /* @0x7ee */

/* ⚠ `sclo` di gdata.c bertipe `int` (@0x730) dan `schi` menyusul (@0x732).
   Di SINI ia dipakai sebagai satu `long` 32-bit: biner memakai
   `add [730h],imm / adc [732h],0`, dan `showsc` dipanggil dengan SATU argumen
   long yang mendarat sebagai dua parameter word (lo,hi) di sisi penerima.
   LINK memadankan NAMA, bukan tipe, jadi ini sah. Tanpa komentar @ supaya
   gendata tidak memanennya ulang. */
extern long sclo;

/* Record 12 byte. Yang dipakai di sini field pada offset 2 = penunjuk skrip
   ANIMATE. drawslot.c memakai tabel yang sama lewat field offset 0 (`w`).
   DUA tabel BERBEDA, dan namanya tidak boleh tertukar -- lihat README
   §SATU NAMA untuk DUA ALAMAT. */
struct part {
    int   w;
    char *scr;
    char  pad[8];
};
extern struct part sprtab[];    /* @0x0a  -- dipakai cabang ZANY */
extern struct part parttab[];   /* @0x1ae -- dipakai cabang MEKANISME */

/* ⭐ PANDANGAN KEDUA atas DUA tabel yang SAMA, digeser 6 byte ke bawah.
   `anmech` = parttab - 6 dan `anzany` = sprtab - 6. Jadi field `scr` di
   offset +8 di sini menunjuk memori yang sama dengan `parttab[k].scr`
   (offset +2 dari basis yang 6 byte lebih tinggi). Itu yang menjelaskan
   konstanta 0x1a8 dan 0x4 yang sempat tidak terpecahkan: keduanya PERSIS
   6 byte sebelum basis tabelnya. `f278e` menerima basis versi ini dan
   membaca `spr` di offset +6, yang sama dengan `parttab[k].w`. */
struct anrec {
    char  pad[8];
    char *scr;
    char  pad2[2];
};
extern struct anrec anzany[];   /* @0x004 = sprtab  - 6 -- ⚠ WAJIB tiga digit:
                                   pola gendata menuntut 2-4 digit hex, jadi
                                   `@0x4` TIDAK akan terpanen. */
extern struct anrec anmech[];   /* @0x1a8 = parttab - 6 */

animvm(steps, n2, rec1, sel1, ord1, n1, rec2, sel2, ord2)
int *steps;                     /* 0x6e — -1 = langkah MEKANISME, else ZANY */
int  n2;                        /* 0x70 */
int *rec1, *sel1, *ord1;        /* 0x72, 0x74, 0x76 */
int  n1;                        /* 0x78 */
int *rec2, *sel2, *ord2;        /* 0x7a, 0x7c, 0x7e */
{
    /* ⚠ TATA LETAK BINGKAI, bukan daftar variabel yang sudah dipahami.
       Offsetnya TERUKUR dari biner; nama `uNN` berarti slot itu memang
       dirujuk tapi perannya belum diturunkan. Urutan deklarasi menentukan
       offset (README aturan 9), jadi JANGAN diurutkan ulang. */
    /* ⏳ PENGGANJAL SEMENTARA. Aslinya 14 byte temp (bingkai 0x6a - 92 lokal);
       draf ini baru menuntut 8 karena badan case belum ditulis. Tanpa ganjal
       ini SEMUA offset lokal bergeser 10 byte dan prolog yang sudah benar pun
       terhitung salah. BUANG begitu ekspresi asli menuntut temp-nya sendiri. */
    char tpad[6];               /* 0x08..0x0d */
    int  i;                     /* 0x0e — indeks langkah skrip */
    int  c1;                    /* 0x10 — pencacah cabang-1 */
    int  c2;                    /* 0x12 — pencacah cabang-2 */
    int  u14, u16;              /* 0x14, 0x16 */
    char ch18[4];               /* 0x18 — diakses per-BYTE */
    int  u1c, u1e, u20, u22, u24, u26, u28, u2a;
    int  snd[3];                /* 0x2c — penyangga BUNYI (lea -> sndptr) */
    int  u32, u34, u36, u38, u3a, u3c, u3e, u40;
    int  u42, u44, u46;
    struct anrec *u48;          /* 0x48 — record part yang sedang dimainkan */
    struct anrec *u4a;          /* 0x4a — basis tabel record (anmech/anzany) */
    int  u4c, u4e;
    int  u50, u52;
    char *u54;                  /* 0x54 — kursor tulis skrip sintetis */
    int  u56;
    char *u58;                  /* 0x58 — awal badan gelung skrip (op 0x0d) */
    int  u5a, u5c, u5e;
    char ch60[2];               /* 0x60/0x61 — pasangan (dx,dy) hasil pilihan */
    char ch62[8];               /* 0x62 — skrip SINTETIS {00, dx, dy, FF} */

    u42 = 0;
    u56 = 0;
    /* mode 0 dan 1 tidak membersihkan separuh bawah layar. */
    if (mode != 0 && mode != 1)
        fillrect(0, 0xa8, 0x13f, 0xc7, 0);
    sndsave(sndbuf);
    if (keyhit() == 0x1b) {
        failed = -1;
        goto quit;
    }
    both = 0;
    /* Pola yang sama: `mov ax,140h` dimuat SEBELUM simpanan-immediate `ticks`. */
    prevtop = 0x140;
    prevx = 0x140;
    ticks = 0x27;
    sndoff();
    /* ⚠ `sndptr` DULU walau simpanannya belakangan: aslinya memuat
       `mov ax,<tune>` SEBELUM simpanan-immediate `sndmode`, lalu menunda
       simpanan `sndptr`-nya. Muatan register mengikuti urutan SUMBER;
       simpanannya yang ditata ulang kompiler. */
    sndptr = 0x978;
    sndmode = 2;
    sndon();
    /* Gelung "jam pasir": dua bingkai bergantian sampai `ticks` habis. */
    for (;;) {
        waitn(0x10);
        blit(&hdrspr[96], 0, 0x88, 8, 0x30);
        waitn(0x10);
        blit(hdrspr, 0, 0x88, 8, 0x30);
        if (ticks == 0x7c0)
            ticks = 0;
        if (ticks <= 0)
            break;
        keyhit();
    }
    u56 = goal * 10;
    sndoff();
    snd[0] = 0x1f4;
    snd[1] = 0x5b4;
    snd[2] = 0x10;
    sndptr = snd;
    sndmode = 1;
    sndon();
    c1 = 0;
    /* Bilah turun dari 0x78 sampai posisi goal. */
    for (i = 0x78; i >= u56; i -= 2) {
        waitn(2);
        if (i != 0x78)
            fillrect(i + 0x10, 0, i + 0x11, 7, 3);
        blit(&hdrspr[192], 0, i, 8, 0x10);
        keyhit();
    }
    for (i = 0; i < 2; i++) {
        waitn(2);
        shftr(0, 4, 8, 0x64, -1);
    }
    fillrect(u56 - 8, 0, u56 + 0x10, 7, 3);
    sndoff();
    sndptr = snd;
    sndmode = 0;
    sndon();
    delay(9);
    /* ⚠ Urutan TERBALIK dari urutan simpanan di biner: untuk beberapa
       penugasan nol berturut yang berbagi satu register, kompiler memancarkan
       simpanannya dalam urutan KEBALIKAN sumber. */
    c1 = 0;
    c2 = 0;
    failed = 0;
    prevx = 0x140;
    prevtop = 0x140;
    kbflush();

    for (i = 0; i < n1 + n2; i++) {
        if (failed != 0)
            break;
        f66fd(0x16, 0);
        if (steps[i] == -1) {
            /* CABANG MEKANISME: jawaban slot c1 harus cocok dengan urutannya. */
            if (ord1[c1] != rec1[3 * c1 + 2]) {
                failed = -1;
                both = i;
                curz = c1;
                slot = c2;
                ch18[0] = i + 0x41;
                fail[c1]++;
                zcnt++;
                g7e8++;
                /* ⚠ slot/curz disimpan SEBELUM printf. Aslinya memuat c2, c1,
                   dan i ke bx/cx/dx sekaligus di awal blok lalu menyimpannya
                   mendahului `call`; menaruhnya SESUDAH printf memaksa
                   kompiler memuat ulang keduanya (4 byte). */
                printf(msgmech, ch18[0]);
                break;
            }
            u5e = fail[c1];
            fail[c1] = 0x8ad0;
            u4a = anmech;
            u20 = sel1[c1];
            scrptr = parttab[u20].scr;
            u22 = rec1[c1 * 3];
            u24 = rec1[c1 * 3 + 1];
        }
        else {
            /* CABANG ZANY OBJECT: sama, tapi atas pencacah dan tabel kedua. */
            if (ord2[c2] != rec2[3 * c2 + 2]) {
                failed = 1;
                slot = c2;
                curz = c1;
                /* ⚠ `both`/`ch18` di SINI, sebelum pencacah — kebalikan dari
                   cabang MEKANISME yang menaruhnya sesudah `curz`/`slot` lalu
                   pencacah. Memindahkannya ke belakang pencacah sudah dicoba
                   DUA kali (tahap 14: 2.913 -> 2.905; tahap 16: 2.941 -> 2.924)
                   dan selalu lebih buruk. */
                both = i;
                zflag[c2]++;
                zcnt++;
                g7e8++;
                ch18[0] = i + 0x41;
                printf(msgzany, ch18[0]);
            }
            else {
                u5e = zflag[c2];
                zflag[c2] = 0x8ad0;
            }
            u4a = anzany;
            u20 = sel2[c2];
            scrptr = sprtab[u20].scr;
            u22 = rec2[c2 * 3];
            u24 = rec2[c2 * 3 + 1];
        }
        /* Bonus: hanya mode 4, hanya kalau lolos, dan BUKAN di langkah
           i == n1+n2-1 (lihat catatan di bawah — dulu dibaca terbalik). */
        /* ⚠ SYARATNYA `!=`, BUKAN `==` — dikoreksi 2026-07-31 dari BINER.
           Di 0x1c72 asli memancarkan `je 0x1cd2` (lompat KELUAR saat sama),
           kita dulu `jne`. Dugaan lama "bonus hanya di langkah TERAKHIR" itu
           TEBAKAN dari nama, bukan dari kode. Membalikkannya menaikkan GLOBAL
           2.900 -> 2.901 dan membuat opcode-nya cocok. Dua syarat berikutnya
           memancarkan `jne` di KEDUA bacaan, jadi hanya yang pertama yang
           membedakan. */
        if (i != n1 + n2 - 1 && mode == 4 && failed == 0) {
            if (u5e >= 0) {
                switch (zcnt) {
                case 0:
                    sclo += 1000;
                    break;
                case 1:
                    sclo += 500;
                    break;
                default:
                    sclo += 250;
                    break;
                }
            }
            showsc(sclo, 1);
        }
        /* Jalankan skrip ANIMATE part ini sampai 0xFF. */
        for (;;) {
            /* SATU ekspresi `||`, bukan dua `if` terpisah: aslinya menguji
               `test si,si` (2 byte) dengan MEMAKAI ULANG SI yang baru dipakai
               untuk membaca `*scrptr`. Dua pernyataan terpisah memaksa
               kompiler memuat ulang penunjuknya (`cmp [3AEh],0`, 5 byte). */
            if (*scrptr == 0xff || scrptr == 0)
                break;
            if (keyhit() == 0x1b) {
                failed = -1;
                goto quit;
            }
            switch (*scrptr++) {
            /* ⚠ URUTAN CASE = urutan ALAMAT BADAN di biner, bukan urutan nilai
               (README aturan 13). Peta lengkap di JOURNAL §Pengintaian animvm. */

            case 0x10:          /* 0x1d09 — akhir goal: bonus + skor + hint */
                if (mode == 4 && lvl == 2 && mflag == 1) {
                    for (u40 = 0; u40 < goal; u40++) {
                        prevx = 0x140;
                        prevtop = 0x140;
                        setball(0, u40 * 10 + 2);
                    }
                    goal++;
                }
                prompts();
                u42 = 1;
                if (mode != 4)
                    break;
                switch (zcnt) {
                case 0:
                    sclo += 10000;
                    break;
                case 1:
                    sclo += 5000;
                    break;
                default:
                    sclo += 2500;
                    break;
                }
                showsc(sclo, 2);
                if (lvl == 2) {
                    sclo += cur2 * 1000;
                    showsc(sclo, 2);
                }
                if (sub == 6) {
                    sclo += (goal - 1) * 2500;
                    fillrect(0, 0, 0x46, 7, 3);
                    goal = 1;
                    showsc(sclo, 3);
                    if (lvl == 2) {
                        sclo += tx * 100;
                        tx = 0;
                        timedrw();
                        showsc(sclo, 3);
                    }
                }
                if ((lvl == 2 && goal <= 1) || (sub == 6 && failed == 0))
                    showhint();
                break;

            case 0x11:          /* 0x1e85 — tulis teks berparameter dari skrip */
                bounce(buf9c5);
                u32 = *(int *)scrptr;
                scrptr += 2;
                u34 = *(int *)scrptr;
                scrptr += 2;
                u36 = *scrptr++;
                u38 = *scrptr++;
                u3a = *scrptr++;
                u3c = *scrptr++;
                u3e = (int)scrptr;
                scrptr += u3c;
                text(u3e, u34, u32, u38, u36, u3a);
                break;

            case 0x00:          /* 0x1f11 — aliran titik jalur bola sampai 0xFF */
                while (*scrptr != 0xff)
                    f2714(u22, u24);
                scrptr++;
                break;

            /* ⚠ 0x0a JATUH TEMBUS ke 0x08 (dan 0x07 ke 0x09): di biner badan
               0x0a berakhir tepat di awal badan 0x08 tanpa lompatan. */
            case 0x0a:          /* 0x1f32 */
                prevx = 0x140;
                prevtop = 0x140;
            case 0x08:          /* 0x1f3b */
                f2714(u22, u24);
                break;

            case 0x01:          /* 0x1f49 — aliran bingkai sprite sampai 0xFF */
                while (*scrptr != 0xff)
                    f278e(u22, u24, u20, u4a);
                scrptr++;
                break;

            case 0x07:          /* 0x1f70 */
                prevx = 0x140;
                prevtop = 0x140;
            case 0x09:          /* 0x1f79 */
                f278e(u22, u24, u20, u4a);
                break;

            case 0x02:          /* 0x1f8d — jeda */
                /* Penugasan DI DALAM syarat: aslinya `push ax` (1 byte),
                   nilainya masih di register sesudah uji tanda. Bentuk dua
                   pernyataan membuat kompiler MEMUAT ULANG dari bingkai. */
                if ((u2a = *scrptr++) >= 0)
                    delay(u2a);
                break;

            case 0x03:          /* 0x1fac — lempar bola ke part BERIKUTNYA */
                ticks = 0;
                u44 = *scrptr++;
                /* ⚠ DI SINI hasilnya DISIMPAN BALIK -- kebalikan dari case 0x0c
                   yang membuangnya. Sudah diuji: membuangnya di sini menurunkan
                   penjajaran 2.748 -> 2.722 dan memunculkan geseran baru di
                   0x1ff1. Dua case, dua perilaku; jangan diseragamkan. */
                u44 = (u44 >= 0xc8) ? u44 - 0x100 : u44;
                u46 = *scrptr++;
                if (steps[i + 1] == -1) {
                    /* ⚠ if/else, BUKAN ternary. Aslinya MENYIMPAN di kedua
                       cabang lalu MEMUAT ULANG; ternary menghitung ke AX,
                       menyimpan sekali, dan memakai ulang AX (4 byte lebih
                       pendek). Bandingkan dengan pemulihan tanda 0xC8 di
                       bawah, yang justru ternary — bentuknya per-TEMPAT. */
                    if (steps[i] == -1)
                        u14 = c1 + 1;
                    else
                        u14 = c1;
                    u48 = anmech + sel1[u14];
                    u26 = rec1[u14 * 3];
                    u28 = rec1[u14 * 3 + 1];
                    if (ord1[u14] != rec1[u14 * 3 + 2]) {
                        /* Part tujuan SALAH: karang skrip {00, dx, dy, FF}
                           supaya bolanya tetap bergerak ke arah yang masuk
                           akal, lalu tunjuk record itu ke skrip karangan. */
                        u48->scr = ch62;
                        u54 = ch62;
                        *u54++ = 0;
                        if (ballx > u26 + 0x18) {
                            ch60[0] = 0x18;
                            ch60[1] = 0x0a;
                        }
                        else if (bally < u28) {
                            ch60[0] = 0xf8;
                            ch60[1] = 0xfc;
                        }
                        else if (ballx < u26) {
                            ch60[0] = 0xf8;
                            ch60[1] = 0x12;
                        }
                        else {
                            ch60[0] = 0xf8;
                            ch60[1] = 0x12;
                        }
                        *u54++ = ch60[0];
                        *u54++ = ch60[1];
                        *u54++ = 0xff;
                    }
                }
                else {
                    if (steps[i] == -1)
                        u16 = c2;
                    else
                        u16 = c2 + 1;
                    u48 = anzany + sel2[u16];
                    u26 = rec2[u16 * 3];
                    u28 = rec2[u16 * 3 + 1];
                }
                u54 = u48->scr;
                /* Switch BERSARANG dengan tabelnya sendiri di 0x21ba (16 byte).
                   Keempat nilai memakai badan yang SAMA; urutan label = urutan
                   pindai tabel. */
                switch (*u54++) {
                case 0x00:
                case 0x0a:
                case 0x08:
                case 0x0b:
                    u4c = *u54++;
                    u4c = ((u4c >= 0xc8) ? u4c - 0x100 : u4c) + u26;
                    u50 = *u54++;
                    u50 = ((u50 >= 0xc8) ? u50 - 0x100 : u50) + u28;
                    u4e = ballx;
                    u52 = bally;
                    f2823(u44, u4e, u52, u4c, u50, u46, 1);
                    break;
                }
                break;

            case 0x0c:          /* 0x21e1 — lempar bola ke koordinat RELATIF */
                u44 = *scrptr++;
                /* ⚠ HASILNYA SENGAJA DIBUANG, bukan salah tulis. Di biner, AX
                   yang memuat nilai terpulihkan langsung ditimpa `mov ax,si`
                   tanpa pernah disimpan balik ke [bp+44h], dan f2823 menerima
                   nilai MENTAH-nya. Kelihatannya bug di gim aslinya; kita
                   merekonstruksi apa adanya. */
                (u44 >= 0xc8) ? u44 - 0x100 : u44;
                u46 = *scrptr++;
                u54 = scrptr;
                u54++;
                u4c = *u54++;
                u4c = ((u4c >= 0xc8) ? u4c - 0x100 : u4c) + u22;
                u50 = *u54++;
                u50 = ((u50 >= 0xc8) ? u50 - 0x100 : u50) + u24;
                u4e = ballx;
                u52 = bally;
                f2823(u44, u4e, u52, u4c, u50, u46, 1);
                break;

            case 0x04:          /* 0x2280 — ganti sumber BUNYI */
                sndoff();
                sndmode = *scrptr++;
                switch (sndmode) {
                case 1:         /* tiga kata tetap, disalin ke penyangga lokal */
                    for (u1c = 0; u1c < 3; u1c++) {
                        snd[u1c] = *(int *)scrptr;
                        scrptr += 2;
                    }
                    sndptr = snd;
                    break;
                case 2:
                case 3:         /* aliran mentah sampai penanda GANDA 0xFF 0xFF */
                    sndptr = scrptr;
                    /* ⚠ SISA 1 BYTE DI SINI, dan itu memblokir ~40 byte lain:
                       geseran +1 memecah lari sejajar di SELURUH sisa fungsi,
                       jadi celah di 0x2313/0x23b7/0x1ce0 dst. sebagian besar
                       ARTEFAK geseran ini, bukan beda isi sungguhan.

                       Yang dibutuhkan SEKALIGUS: (a) keluar gelung lewat
                       FALL-THROUGH (bukan `break` yang memancarkan `jmp`
                       mubazir ke instruksi berikutnya), dan (b) operan kedua
                       MEMUAT ULANG `mov ax,[3AEh]` alih-alih memakai ulang SI.
                       EMPAT bentuk sudah dicoba, tak satu pun memberi keduanya:
                         - `do/while` + `*++scrptr`            -> 2.908 (fall-through OK, SI dipakai ulang)
                         - `do/while` + `(scrptr++, *scrptr)`  -> 2.909
                         - `do/while` + `*(scrptr += 1)`       -> 2.909
                         - `for(;;)` + `&&` satu-ekspresi      -> 2.731
                       Yang di bawah (`for`/`continue`) = 2.929, TERBAIK sejauh
                       ini: muat-ulangnya benar, `jmp` mubazirnya yang tersisa.

                       ⚠ SUDAH DICOBA & GAGAL: bentuk `&&` satu-ekspresi
                       (`if (*scrptr == 0xff && *++scrptr == 0xff) break;`)
                       menurunkan penjajaran 2.753 -> 2.731.
                       Bentuk `continue` di bawah MEMANG memaksa muat-ulang
                       `mov ax,[3AEh]` seperti aslinya (itu yang dicari), TAPI
                       masih menyisakan `jmp` mubazir ke instruksi berikutnya
                       karena `break`-nya bukan jalur jatuh-tembus. Aslinya
                       keluar lewat FALL-THROUGH dari `jne` yang kedua — bentuk
                       do/while `||` memberi itu tapi memakai ulang SI. Sisa
                       1 byte, belum ada bentuk yang memberi KEDUANYA. */
                    for (;;) {
                        scrptr++;
                        if (*scrptr != 0xff)
                            continue;
                        if (*++scrptr == 0xff)
                            break;
                    }
                    scrptr++;
                    break;
                }
                sndon();
                break;

            case 0x05:          /* 0x2305 */
                putmsk(buf9c5, page2);
                break;

            case 0x06:          /* 0x2315 */
                prevx = 0x140;
                prevtop = 0x140;
                break;

            case 0x0d:          /* 0x2321 — tandai AWAL badan gelung */
                u58 = scrptr;
                u5a = -1;
                u5c = 0;
                break;

            case 0x0e:          /* 0x2334 — aktifkan mode TUNGGU TOMBOL */
                u5c = 1;
                break;

            case 0x0f:          /* 0x233c — akhir gelung / tunggu tombol */
                if (u5c == 1) {
                    /* Switch bersarang, tabelnya sendiri di 0x235a. */
                    switch (keyhit()) {
                    case 0x1b:
                    case 0x0d:
                    case 0x20:
                        /* ⚠ `continue`, bukan `break`: di biner badan ini
                           melompat LANGSUNG ke puncak gelung skrip dan
                           melewati switch kedua di bawah. */
                        u5a = 0;
                        scrptr++;
                        continue;
                    case 0x00:
                        break;
                    default:
                        getkey();
                        break;
                    }
                }
                switch (u5a) {
                case 0:
                    /* ⚠ Syaratnya `== 0xff` dengan `else` yang mem-`break`,
                       BUKAN `!= 0xff` lalu badan. Aslinya `jne <else>` lalu
                       badan-benar lalu `jmp` MELEWATI else ke badan case -1 —
                       jadi jatuh-tembusnya lewat cabang BENAR, dan cabang
                       salah keluar duluan. */
                    if (*scrptr == 0xff)
                        u5c = 1;
                    else {
                        scrptr++;
                        break;
                    }
                    /* ⚠ JATUH TEMBUS ke case -1 */
                case -1:
                    u5a = *scrptr++;
                    scrptr = u58;
                    break;
                default:
                    u5a--;
                    scrptr = u58;
                    break;
                }
                break;

            /* Badan `case 0xff` di 0x23d1 KOSONG dan paling belakang di biner,
               jadi labelnya WAJIB terakhir. */
            case 0xff:
                break;
            }
        }
        if (steps[i] == -1)
            c1++;
        else
            c2++;
    }

    if (u42 == 0) {
        prompts();
        if ((lvl == 2 && goal <= 1) || (sub == 6 && failed == 0))
            showhint();
        if (i != n1 + n2)
            bounce(buf9c5);
        while (keyhit() == 0)
            ;
    }

quit:
    sndoff();
    sndptr = snd;
    sndmode = 0;
    sndon();
    delay(1);
    sndrest();
    return failed;
}
