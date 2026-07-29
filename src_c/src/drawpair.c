/* FUN_1000_4a31 @ 1000:4a31, 392 byte — gambar satu part, plus "pasangannya"
 * kalau part berikutnya adalah lanjutan dari part ini.
 *
 * Dua record dibaca: milik slot i dan slot i+1. Kalau tinggi record kedua
 * tepat 100 lebih dari yang pertama, keduanya satu kesatuan (mis. tali katrol
 * yang tergambar dua bagian) sehingga bagian kedua digambar lebih dulu.
 * Offset (dx,dy) di record adalah byte BERTANDA -- di MS C 1.04 char itu
 * unsigned, jadi tandanya dipulihkan dengan "if (v > 0x7f) v -= 0x100".
 *
 *   recbase @0x73c ; sprtab @0x0a (dibaca sbg *(int *)(idx*0xc + 10))
 *   load()=53ff, blit()=672f
 *
 * PETA SLOT (disassembly): bingkai 18h = bp+0..17h.
 *   bp+0..6  = 4 TEMP
 *   bp+8..16h = 8 LOKAL
 * Record diakses lewat penunjuk char (r1[1], r1[2], ...) supaya jadi bentuk
 * displacement, bukan penjumlahan basis.
 */

extern int recbase;         /* @0x73c */

drawpair(a, b, x, y, tab, n, i, sp)
int   a, b, x, y;
int  *tab;
int   n, i, sp;
{
    /* DELAPAN lokal (bingkai 18h = 8 lokal + 4 temp). `rb` menampung recbase:
       biner memuatnya SEKALI di awal ("a1 3c 07") lalu menyimpannya ke lokal
       dan memakainya untuk KEDUA record. */
    int id1, id2, dx, dy, spr, rb;
    char *r1;
    char *r2;

    rb = recbase;
    id1 = tab[i];
    r1 = (char *)(rb + id1 * 0xc);
    id2 = tab[i + 1];
    r2 = (char *)(rb + id2 * 0xc);
    if (i + 1 < n && r2[1] - 100 == r1[1]) {
        dx = r2[4];
        if (dx > 0x7f)
            dx = dx - 0x100;
        dy = r2[5];
        if (dy > 0x7f)
            dy = dy - 0x100;
        if (sp < 0) {
            load(a, rb, id2, b);
            spr = b;
        }
        else
            spr = *(int *)(((sp + id2) - id1) * 0xc + 10);
        blit(spr, x + dx, y + dy, r2[2], r2[3]);
    }
    dx = r1[4];
    if (dx > 0x7f)
        dx = dx - 0x100;
    dy = r1[5];
    if (dy > 0x7f)
        dy = dy - 0x100;
    if (sp < 0) {
        load(a, recbase, id1, b);
        spr = b;
    }
    else
        spr = *(int *)(sp * 0xc + 10);
    blit(spr, x + dx, y + dy, r1[2], r1[3]);
}

/* ⏳ BELUM COCOK — 373 byte vs 392 (19 KURANG), bingkai 18h SUDAH COCOK.
 * Perjalanan: 370 -> 373 setelah `rb` (salinan recbase) ditambahkan.
 * PETA SLOT ASLI: bingkai 18h = bp+0..6 (4 TEMP) + bp+8..16h (8 LOKAL).
 * Delapan lokal kita sekarang: id1, id2, dx, dy, spr, rb, r1, r2.
 * Biner memuat recbase SEKALI ("a1 3c 07") lalu menyimpannya ke lokal.
 * SISA: 19 byte kurang -- kita masih lebih pendek, jadi ada kode di asli yang
 * belum ditulis. Kandidat: pemulihan tanda (dx/dy) mungkin ditulis lain,
 * atau kedua blok gambar TIDAK memakai variabel yang sama (asli mungkin punya
 * dx2/dy2 tersendiri, bukan menimpa dx/dy).
 */
