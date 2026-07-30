/* FUN_1000_3c4f @ 1000:3c4f, 704 byte — layar REVIEW MECHANISMS: strip palet
 * 9 mekanisme di bawah, kursor kedip-kedip, panah kiri/kanan menggulir strip.
 *
 * ⚠ Ukurannya 704 (0x3c4f..0x3f0e), bukan 362 (functions.txt) atau 650
 * (truesize.py): sesudah epilog terakhir masih ada back-edge for(;;), TABEL
 * SWITCH 7 entri di segmen kode (0x3edc), dan loop pencarinya (0x3efb).
 *
 * Nilai balik:  cur           = mekanisme dipilih dengan ENTER
 *               cur | 0x8000  = dipilih dengan SPASI (bit 15 = penanda)
 *               -1            = ESC
 *               0xfe          = waktu habis (mode 4, tx <= 0)
 *
 *   drawpal()=3b83  drawbox()=3886  hintmark()=4cd4  timebar()=4bb9
 *   keyhit()=1791   getkey()=1814   blit()=672f
 *   vbend()=5da1    vbwait()=5d98
 *   shftl()=5dce    shftr()=6600   — primitif geser layar (assembly, push es/ds)
 *
 * PETA SLOT (bingkai 0x10): bp+0..2 = 2 TEMP, lalu
 *   bp+4=t  6=j  8=key  0ah=addr  0ch=i  0eh=ok
 * Argumen: bp+14h=base, 16h=boxy, 18h=boxx, 1ah/1ch tak dipakai, 1eh=sel.
 *
 * ⚠ `t` dan `addr` DIISI TAPI TIDAK PERNAH DIBACA di ketiga tempat pemanggilan
 * blit. Itu memang ada di biner asli (store ke bp+4 dan bp+0ah sesudah semua
 * push), jadi bukan kelalaian rekonstruksi — lihat catatan "byte-identical !=
 * source aslinya" di README.
 *
 * BENTUK: dua label + `goto`, bukan loop bersarang. `goto top` dipakai 7 kali
 * dari dalam switch — dari sana `break`/`continue` tidak bisa mencapai titik
 * itu, jadi memang goto.
 */

extern int  nmech;          /* @0x3ac */
extern int  cur;            /* @0x51c */
extern int  lo;             /* @0x51e */
extern int  hi;             /* @0x520 */
extern char spr[];          /* @0x7fa */
extern char idtab[];        /* @0x2ea */
extern int  mode;           /* @0x792 */
extern int  tx;             /* @0x7ee */
extern int  ta;             /* @0x7ec */
extern int  tb;             /* @0x7ea */

review(base, boxy, boxx, u1, u2, sel)
int base, boxy, boxx, u1, u2, sel;
{
    int unused, t, j, key, addr, i, ok;

    drawpal(sel, base);
top:
    if (boxy != 0) {
        addr = base + spr[cur] * 0xc0;
        t = idtab[cur];
        blit(addr, boxy, boxx, 0x18, 0x20);
    }
    for (;;) {
        tb = ta;
        do {
            if (boxy != 0)
                drawbox(boxy, boxx);
            hintmark();
            blit(0x364, 0xc0, 0x90, 8, 0x20);
            for (i = 0; i < 0xc && keyhit() == 0; i++) {
                vbend();
                vbwait();
            }
            if (boxy != 0)
                drawbox(boxy, boxx);
            blit(0x31c, 0xc0, 0x90, 8, 0x20);
            for (i = 0; i < 0xc && keyhit() == 0; i++) {
                /* penugasan BERSARANG: biner menguji tb dulu (test ax,ax di
                   0x3d29) baru menyimpannya ke ta — dua pernyataan terpisah
                   akan menyimpan lebih dulu lalu memuat ulang */
                if ((ta = tb) <= 0)
                    timebar();
                vbend();
                vbwait();
            }
            ok = 1;
            if (mode == 4 && tx <= 0)
                ok = 0;
            if ((ta = tb) <= 0)
                timebar();
        } while (keyhit() == 0 && ok != 0);
        if (mode == 4 && tx <= 0)
            return 0xfe;
        if ((key = getkey()) == 0)
            key = getkey() + 0x100;
        switch (key) {
        case '4':
        case 0x14b:
            if (cur + 1 >= nmech)
                goto top;
            cur++;
            lo++;
            hi++;
            for (j = 0; j < 8; j++) {
                vbwait();
                shftl(0xa8, 0x10, 0x18, 0x120, 1);
            }
            /* uji POSITIF berblok lalu `goto` — bukan "if (hi >= nmech) goto
               top;". Lihat probes/probe10.c: bentuk ini memancarkan lompatan
               yang sama ("jl +3 / jmp jauh", karena lompatan-salah dirantai ke
               goto yang langsung menyusul) TAPI menahan nilai hi di AX, jadi
               indeksnya jadi "mov si,ax" seperti biner asli, bukan
               "mov si,[hi]". */
            if (hi < nmech) {
                addr = base + spr[hi] * 0xc0;
                t = idtab[hi];
                blit(addr, 0xa8, 0x10, 0x18, 0x20);
            }
            goto top;
        case '6':
        case 0x14d:
            if (cur - 1 < 0)
                goto top;
            cur--;
            lo--;
            hi--;
            for (j = 0; j < 8; j++) {
                vbwait();
                shftr(0xa8, 0x14, 0x18, 0x12c, -1);
            }
            if (lo >= 0) {
                if (lo < 0x32) {
                    addr = base + spr[lo] * 0xc0;
                    t = idtab[lo];
                    blit(addr, 0xa8, 0x110, 0x18, 0x20);
                }
            }
            goto top;
        case 0x0d:
        case ' ':
            if (key == ' ')
                return cur | 0x8000;
            return cur;
        case 0x1b:
            return -1;
        /* `default: break;` memancarkan back-edge for(;;) sebagai jmp
           tersendiri di 0x3ed9, tepat sebelum tabel — lihat probes/probe8.c */
        default:
            break;
        }
    }
}
