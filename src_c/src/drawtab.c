/* FUN_1000_3769 @ 1000:3769, 177 byte — gambar seluruh entri tabel layar.
 *
 * Bersihkan bilah atas, gambar sprite kepala, bersihkan badan layar, lalu
 * jalankan tabel entri 12-byte: tiap entri boleh berupa TEKS atau SPRITE.
 *   kind < 0x80 -> teks lewat FUN_1000_6453
 *   kind >= 0x80 -> sprite lewat FUN_1000_672f
 * Inilah rutin yang tata letak teksnya kita ekstrak untuk port (review_layout.json).
 *
 * Struktur entri 12 byte diturunkan dari offset yang dipakai:
 *   +0 kind, +2 x, +4 y, +6 c6, +7 c7, +8 c8, +10 penunjuk teks/sprite
 * char di MS C 1.04 unsigned, jadi "kind < 0x80" langsung benar.
 */

struct ent {
    char kind;
    char f1;
    int  x;
    int  y;
    char c6;
    char c7;
    char c8;
    char f9;
    int  str;
};

extern char hdrspr[];       /* @0x526 */

drawtab(p, n)
struct ent *p;
int n;
{
    int i;

    fillrect(0, 0, 0x13f, 7, 3);
    blit(hdrspr, 0, 0x88, 8, 0x30);
    fillrect(0, 8, 0x13f, 199, 1);
    for (i = 0; i < n; i++) {
        if (p->kind < 0x80)
            text(p->str, p->y, p->x, p->c7, p->c6, p->c8);
        else
            blit(p->str, p->x, p->y, p->c6, p->c7);
        p = p + 1;
    }
}
