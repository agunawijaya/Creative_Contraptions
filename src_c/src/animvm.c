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
 *   printf()=6a48  text()=6453  blitmsk()=6524
 *
 * ⏳ TAHAP 1: baru prolog. Angka penjajaran ada di JOURNAL.
 */

/* ⚠ `scrptr` sengaja `char *` (bukan `int` + cor) — lihat README §CAST
   PENUNJUK. Alamatnya sudah terdaftar di f2714.c, jadi tanpa komentar @ di
   sini supaya gendata tidak memanennya dua kali. */
extern char *scrptr;

extern int  prevtop;            /* @0x262 */
extern int  prevx;              /* @0x266 */
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
       draf ini baru menuntut 6 karena badan case belum ditulis. Tanpa ganjal
       ini SEMUA offset lokal bergeser 10 byte dan prolog yang sudah benar pun
       terhitung salah. BUANG begitu ekspresi asli menuntut temp-nya sendiri. */
    char tpad[8];               /* 0x06..0x0d */
    int  i;                     /* 0x0e — indeks langkah skrip */
    int  c1;                    /* 0x10 — pencacah cabang-1 */
    int  c2;                    /* 0x12 — pencacah cabang-2 */
    int  u14, u16;              /* 0x14, 0x16 */
    char ch18[4];               /* 0x18 — diakses per-BYTE */
    int  u1c, u1e, u20, u22, u24, u26, u28, u2a;
    int  snd[3];                /* 0x2c — penyangga BUNYI (lea -> sndptr) */
    int  u32, u34, u36, u38, u3a, u3c, u3e, u40;
    int  u42, u44, u46, u48, u4a, u4c, u4e;
    int  u50, u52, u54, u56, u58, u5a, u5c, u5e;
    char ch60[10];              /* 0x60/0x61 diakses per-BYTE */

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
    ticks = 0x27;
    prevtop = 0x140;
    prevx = 0x140;
    sndoff();
    sndmode = 2;
    sndptr = 0x978;
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
    sndmode = 1;
    sndptr = snd;
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
    sndmode = 0;
    sndptr = snd;
    sndon();
    delay(9);
    failed = 0;
    c2 = 0;
    c1 = 0;
    prevx = 0x140;
    prevtop = 0x140;
    kbflush();

    for (i = 0; i < n1 + n2; i++) {
        if (failed != 0)
            break;
        f66fd(0x16, 0);
        if (steps[i] == -1) {
            /* CABANG MEKANISME: jawaban slot c1 harus cocok dengan urutannya. */
            if (ord1[c1] != rec1[c1 * 3 + 2]) {
                failed = -1;
                both = i;
                fail[c1]++;
                zcnt++;
                g7e8++;
                ch18[0] = i + 0x41;
                printf(msgmech, ch18[0]);
                slot = c2;
                curz = c1;
                break;
            }
            u5e = fail[c1];
            fail[c1] = 0x8ad0;
            u4a = 0x1a8;
            u20 = sel1[c1];
            scrptr = parttab[u20].scr;
            u22 = rec1[c1 * 3];
            u24 = rec1[c1 * 3 + 1];
        }
        else {
            /* CABANG ZANY OBJECT: sama, tapi atas pencacah dan tabel kedua. */
            if (ord2[c2] != rec2[c2 * 3 + 2]) {
                failed = 1;
                both = i;
                zflag[c2]++;
                zcnt++;
                g7e8++;
                ch18[0] = i + 0x41;
                printf(msgzany, ch18[0]);
                curz = c1;
                slot = c2;
            }
            else {
                u5e = zflag[c2];
                zflag[c2] = 0x8ad0;
            }
            u4a = 4;
            u20 = sel2[c2];
            scrptr = sprtab[u20].scr;
            u22 = rec2[c2 * 3];
            u24 = rec2[c2 * 3 + 1];
        }
        /* Bonus hanya di langkah TERAKHIR, hanya mode 4, hanya kalau lolos. */
        if (i == n1 + n2 - 1 && mode == 4 && failed == 0) {
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
            if (*scrptr == 0xff)
                break;
            if (scrptr == 0)
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
                bounce(0x9c5);
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
                u2a = *scrptr++;
                if (u2a < 0)
                    break;
                delay(u2a);
                break;

            /* ⏳ 9 badan case menyusul; `case 0xff` (0x23d1, kosong) WAJIB
               tetap paling akhir karena badannya paling belakang di biner. */
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
            bounce(0x9c5);
        while (keyhit() == 0)
            ;
    }

quit:
    sndoff();
    sndmode = 0;
    sndptr = snd;
    sndon();
    delay(1);
    sndrest();
    return failed;
}
