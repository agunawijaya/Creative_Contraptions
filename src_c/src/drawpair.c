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
    /* Urutan slot dari biner: dx@bp+8, dy@0ah, id2@0ch, id1@0eh, rb@10h,
       r1@12h, r2@14h, spr@16h. */
    int dx, dy, id2, id1, rb;
    char *r1;
    char *r2;
    int spr;

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

/* ⏳ BELUM COCOK — 373 byte vs 392 (19 KURANG). Bingkai DAN urutan slot
 * SUDAH COCOK: dx@bp+8, dy@0ah, id2@0ch, id1@0eh, rb@10h, r1@12h, r2@14h,
 * spr@16h (bingkai 18h = 8 lokal + 4 temp).
 *
 * Beda pertama tinggal di +62, dan bentuknya alokasi register:
 *     kita: 8b 4e 10  03 c8  8b f1     (mov cx,[rb]; add cx,ax; mov si,cx)
 *     asli: 8b 76 10  03 f0            (mov si,[rb]; add si,ax)
 * Kita punya "mov si,cx" ekstra -- kompiler menghitung ke CX lalu memindah.
 * Karena di titik ini kita 2 byte LEBIH PANJANG padahal total 19 byte KURANG,
 * ada ~21 byte yang belum ditulis di tempat lain.
 * Kandidat: pemulihan tanda dx/dy mungkin ditulis empat kali terpisah di asli
 * (dua blok gambar x dua sumbu) dengan bentuk yang lebih panjang dari milik kita.
 */
