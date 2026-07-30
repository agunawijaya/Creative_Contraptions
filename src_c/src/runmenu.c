/* FUN_1000_34cc @ 1000:34cc, 547 byte — LOOP PILIH MENU (inti navigasi game).
 *
 * ⚠ Ukurannya 547, bukan 497 seperti laporan truesize.py, dan bukan 430 seperti
 * functions.txt. Sebabnya: sesudah epilog terakhir (0x36b4) masih ada
 *   0x36bd  jmp 0x3536        <- back-edge for(;;) / ujung switch
 *   0x36c0  TABEL SWITCH      <- 6 entri (nilai,label), 24 byte, di SEGMEN KODE
 *   0x36d8  loop pencari tabel + "jmp default"
 * dan itu semua masih milik fungsi ini. Batas atas = 0x36ef (kbflush).
 *
 * Menerima tabel entri tampilan (struct item, stride 0xc — sama dengan setsel()
 * dan show()) beserta jumlahnya. Entri yang bisa DIPILIH ditandai kind==0x80;
 * indeksnya dikumpulkan lebih dulu ke list[] supaya panah atas/bawah cukup
 * berjalan di list, bukan menyaring ulang tiap kali.
 *
 * Sorotan pilihan digambar sebagai bingkai berkedip: drawrect + 4 garis, dua
 * kali (j<2), diselingi tunggu 0x14 bingkai retrace. Loop berhenti begitu ada
 * tombol ditekan.
 *
 * Nilai balik: nomor entri terpilih + 1 (Enter), atau -1 (ESC).
 *
 *   kbflush()=36ef  keyhit()=1791  getkey()=1814  tone2()=3734
 *   drawrect()=4009 line()=5cbb    vbend()=5da1   vbwait()=5d98
 *
 * PETA SLOT (bingkai 0x4c): bp+0..4 = 3 TEMP, lalu
 *   bp+6=cur  8=cnt  0ah=j  0ch=t  0eh=p  10h=key
 *   12h=y  14h=x  16h=h  18h=w   1ah..4bh = list[25]
 * Argumen: bp+50h=tab, bp+52h=n.
 *
 * TABEL SWITCH: urutan entri di biner (0x1b, 0x0d, 0x250, 0x32, 0x248, 0x38)
 * adalah KEBALIKAN urutan `case` di sumber — sesuai aturan 8f di README. Badan
 * case-nya sendiri muncul urut sumber: naik(3663), turun(3679), Enter(3690),
 * ESC(36b5).
 */

struct item {
    char kind;              /* +0  0x80 = entri yang bisa dipilih */
    char pad1;              /* +1  */
    int  x;                 /* +2  dipakai drawrect sebagai koordinat y */
    int  y;                 /* +4  dipakai drawrect sebagai koordinat x */
    char a;                 /* +6  tinggi */
    char b;                 /* +7  lebar  */
    char c;                 /* +8  */
    char pad9;              /* +9  */
    int  spr;               /* +10 */
};                          /* = 0xc byte */

extern struct item *lastmen;    /* @0x1dcc  tabel menu yang terakhir dipakai */
extern int lastsel;             /* @0x1dce  pilihan terakhir di tabel itu */

runmenu(tab, n)
struct item *tab;
int n;
{
    int cur, cnt, j, t;
    struct item *p;
    int key, y, x, h, w;
    int list[25];

    kbflush();
    cnt = 0;
    p = tab;
    for (cur = 0; cur < n; cur++) {
        if (p++->kind == 0x80)
            list[cnt++] = cur;
    }
    if (lastmen == tab && cnt > 0)
        cur = lastsel;
    else
        cur = 0;
    if (cur > cnt)
        cur = 0;
    for (;;) {
        /* Penugasan BERSARANG: biner membandingkan [si] dulu, baru menyimpan si
           ke slot p (0x3551 sesudah 0x354e). Dua pernyataan terpisah akan
           menyimpan lebih dulu lalu memuat ulang. */
        if ((p = tab + list[cur])->kind == 0x80 && cnt > 0) {
            y = p->x;
            x = p->y;
            h = p->a;
            w = p->b;
            do {
                for (j = 0; j < 2; j++) {
                    drawrect(y, x, h, w, 1);
                    line(x + 1, y + 1, x + 1, y + h - 2, 1);
                    line(x + w - 2, y + 1, x + w - 2, y + h - 2, 1);
                    line(x, y - 1, x + w - 1, y - 1, 2);
                    line(x, y + h, x + w - 1, y + h, 2);
                    for (t = 0; t < 0x14 && keyhit() == 0; t++) {
                        vbend();
                        vbwait();
                    }
                }
            } while (keyhit() == 0);
        } else {
            while (keyhit() == 0)
                ;
        }
        if ((key = getkey()) == 0)
            key = getkey() + 0x200;
        switch (key) {
        case '8':
        case 0x248:
            if (cur - 1 >= 0)
                cur--;
            else
                cur = cnt - 1;
            break;
        case '2':
        case 0x250:
            if (cur + 1 < cnt)
                cur++;
            else
                cur = 0;
            break;
        case 0x0d:
            tone2();
            if (p->kind == 0x80) {
                lastmen = tab;
                lastsel = cur;
            }
            return cur + 1;
        case 0x1b:
            return -1;
        /* `default: break;` WAJIB ada — itu yang memancarkan "jmp loop_top"
           tersendiri di 0x36bd, tepat sebelum tabel switch. Tanpa itu
           kompiler melipat back-edge ke jump default saja dan fungsi kurang
           3 byte. Dibuktikan probes/probe8.c: dari enam varian (tanpa
           default, default kosong, continue, while(1), do-while(1),
           pernyataan kosong sesudah switch) hanya `default: break;` yang
           menghasilkan pola itu. */
        default:
            break;
        }
    }
}
