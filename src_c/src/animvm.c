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
 *   bounce()=2504  shftr()=6600  keyio()=66fd  blit()=672f  fillrect()=6869
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

animvm(steps, nb, rec1, sel1, ord1, cnt1, rec2, sel2, ord2)
int steps, nb, rec1, sel1, ord1, cnt1, rec2, sel2, ord2;
{
    /* ⚠ TATA LETAK BINGKAI, bukan daftar variabel yang sudah dipahami.
       Offsetnya TERUKUR dari biner; nama `uNN` berarti slot itu memang
       dirujuk tapi perannya belum diturunkan. Urutan deklarasi menentukan
       offset (README aturan 9), jadi JANGAN diurutkan ulang. */
    /* ⏳ PENGGANJAL SEMENTARA. Aslinya 14 byte temp (bingkai 0x6a - 92 lokal);
       draf ini baru menuntut 4 karena badan case belum ditulis. Tanpa ganjal
       ini SEMUA offset lokal bergeser 10 byte dan prolog yang sudah benar pun
       terhitung salah. BUANG begitu ekspresi asli menuntut temp-nya sendiri. */
    char tpad[10];              /* 0x04..0x0d */
    int  i;                     /* 0x0e — indeks langkah skrip */
    int  c1;                    /* 0x10 — pencacah cabang-1 */
    int  c2;                    /* 0x12 — pencacah cabang-2 */
    int  u14, u16;              /* 0x14, 0x16 */
    char ch18[4];               /* 0x18 — diakses per-BYTE */
    int  u1c, u1e, u20, u22, u24, u26, u28, u2a;
    int  snd[11];               /* 0x2c — penyangga BUNYI (lea -> sndptr) */
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

quit:
    return failed;
}
