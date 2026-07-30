/* FUN_1000_5505 @ 1000:5505, 964 byte — LOOP UTAMA satu layar permainan.
 *
 * Menggabungkan dua jenis slot dalam satu putaran: slot ZANY (dipilih lewat
 * review()) dan slot MEKANISME (dipilih lewat pickvar()). `both` @0x844
 * berjalan melintasi KEDUA kelompok; `state[both]` menentukan yang mana.
 * Kalau -1, giliran kelompok zany; selain itu kelompok mekanisme.
 *
 * Pembuka menyiapkan bilah waktu: kalau `tinit == 1`, batas `range` diacak
 * (rnd(200) diskalakan ke 0x17/199 lalu dikurangkan dari `tx`), sesudah itu
 * `tinit` dimatikan supaya pengacakan hanya sekali per permainan.
 *
 * Nilai balik: 0xfe = waktu habis (dan pemain menekan SPASI untuk lanjut),
 * -1 = batal/ESC, selain itu nomor pilihan terakhir.
 *
 *   sndsave()=5a7f  sndrest()=5ac9  timedrw()=4c04  kbflush()=36ef
 *   redraw()=5936   mkpal()=3909    review()=3c4f   fillrect()=6869
 *   nvar()=4094     pickvar()=42ca  showhint()=24bb text()=6453
 *   keyhit()=1791   getkey()=1814   clrbot()=5911   place()=4e3e  rnd()=5a5b
 *
 * PETA SLOT (bingkai 0x84): bp+0..0ah = 6 TEMP, lalu
 *   bp+0ch=chg1  0eh=a1  10h=sel  12h=u  14h=v  16h=w  18h=t
 *   1ah=list[50] (1ah..7dh)  7eh=a2  80h=chg2  82h=key
 * Argumen: bp+88h=p1 .. 0b0h=p21; bp+8eh (p4) TIDAK DIPAKAI.
 */

extern int  timer;          /* @0x7f2 */
extern int  lvl6;           /* @0x7f6 */
extern int  nmax;           /* @0x3b4 */
extern int  tx;             /* @0x7ee */
extern int  range;          /* @0x830 */
extern int  best;           /* @0x82e */
extern int  tinit;          /* @0x832 */
extern int  both;           /* @0x844 */
extern int  state[];        /* @0x4f2 */
extern int  seed;           /* @0x72a */
extern int  nmech;          /* @0x3ac */
extern int  curz;            /* @0x2e6 */
extern char idtab[];        /* @0x2ea */
extern char *base;          /* @0x73a */
extern int  slot;           /* @0x51a */
extern int  fh;             /* @0x72c */
extern char *recbase;       /* @0x73c -- char* DI SINI: biner memuatnya
                               langsung ke SI ("mov si,[73ch] / add si,ax").
                               Sebagai int, penjumlahannya lewat CX lalu
                               "mov si,cx" -- 2 byte kelebihan. */
extern char sndbuf[];       /* @0x670e */

runplay(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11,
        p12, p13, p14, p15, p16, p17, p18, p19, p20, p21)
int  p1;
char p2;            /* BUKAN int: biner memuatnya "mov al,[bp+8ah]" +
                       "xor ah,ah" tiap dipakai */
int *p3;
int  p4, p5;
int *p6;
int  p7;
int *p8;
int *p9;
int  p10, p11, p12, p13;
int *p14;
int *p15;
int *p16;
int *p17;
int  p18, p19, p20, p21;
{
    char pad0[2];       /* 2 slot di depan: tanpa ini `sel` jatuh di bp+0ch,
                           padahal biner memakai bp+10h (bingkai 0x84). */
    int chg1, a1, sel, u, v, w, t;
    int list[50];
    int a2, chg2, key;

    sel = 0;
    sndsave(sndbuf);
    timer = -1;
    lvl6 = nmax;
    chg1 = 0;
    chg2 = 0;
    if (tinit == 1) {
        range = tx - (rnd(200) * 0x17 / 199 + 2);
        tinit = 0;
    }
    else
        range = 0x140;
    if (best > range)
        best = tx - range;
    timedrw();
    /* BUKAN for(;;): tidak ada back-edge di ujung. Satu-satunya jalan
       kembali adalah `goto top` dari case 0x0d; ujung switch jatuh ke `fin`. */
top:
    kbflush();
        redraw();
        while (sel >= 0 && sel != 0xfe) {
            if (state[both] == -1) {
                nmech = mkpal(seed, p1, p3, p2, p7);
                /* ENAM argumen, dan nilainya didorong LANGSUNG dari [si]/[bx]
                   -- bukan lewat lokal. Ghidra menampilkan argumen ke-7
                   (curz*3*2) yang TIDAK ada di biner: hanya 6 push. */
                sel = review(p1, p3[3 * curz], p3[3 * curz + 1], list, p5,
                             p6[curz]);
                if (sel != -1 && sel != 0xfe) {
                    a1 = sel & 0x7fff;
                    if (p6[curz] != a1) {
                        chg1 = 1;
                        p6[curz] = a1;
                        p8[curz] = idtab[a1];
                        p9[curz] = base[p8[curz] * 0xc];
                    }
                    curz++;
                    if (curz >= p2)
                        curz = 0;
                }
            }
            else {
                fillrect(0, 0xa8, 0x13f, 0xbf, 0);
                w = p17[slot * 3 + 2];
                t = nvar(w, list);
                u = p17[3 * slot];
                v = p17[3 * slot + 1];
                /* TUJUH argumen di sini (runfill memanggilnya dengan delapan).
                   Argumen ke-8 `slot*3*2` menciptakan CSE atas `3*slot`
                   sehingga perkaliannya berubah jadi bentuk offset. */
                sel = pickvar(fh, p19, u, v, list, t, p14[slot]);
                if (sel != -1 && sel != 0xfe) {
                    a2 = sel & 0x7fff;
                    if (a2 != p14[slot]) {
                        chg2 = 1;
                        p14[slot] = a2;
                        p15[slot] = list[a2];
                        p16[slot] = recbase[p15[slot] * 0xc];
                    }
                    slot++;
                    if (slot >= p13 - 1)
                        slot = 0;
                }
            }
            both++;
            if (both >= p13 + p2 - 1)
                both = 0;
        }
        if (sel == 0xfe) {
            showhint();
            fillrect(0, 0xa0, 0x13f, 199, 0);
            text(0x1ebe, 0x38, 0xb8, 1, 1, 2);
            for (;;) {
                while (keyhit() == 0)
                    ;
                key = getkey();
                /* ESC me-return DI TEMPAT (epilog dipancarkan ulang), bukan
                   `break` lalu return sesudah loop. */
                if (key == 0x1b) {
                    sndrest();
                    return -1;
                }
                if (key == 0x20) {
                    sndrest();
                    return 0xfe;
                }
            }
        }
        if (sel == -1 || sel == 0xfe)
            goto out;
        /* SWITCH, bukan rantai if: badan case ditaruh lebih dulu (0x0d di
           +817, 0x1b di +825) lalu rantai pembanding di bawah, dan rantai itu
           TERBALIK dari urutan case di sumber (0x1b, 0x0d, 0x20 -> sumbernya
           0x20, 0x0d, 0x1b). Case 0x0d kembali ke ATAS loop, dua lainnya
           jatuh ke `fin`. */
        switch (clrbot()) {
        case ' ':
            break;
        case 0x0d:
            sel = 1;
            goto top;
        case 0x1b:
            sel = -1;
            break;
        }
fin:
    if (chg1 == 1) {
        place(0x1a8, base, seed, p11, p12, p2, p8, p10, 0, 0);
        chg1 = 0;
    }
    if (chg2 == 1) {
        place(4, recbase, fh, p20, p21, p13, p15, p18);
        chg2 = 0;
    }
out:
    sndrest();
    return sel;
}
