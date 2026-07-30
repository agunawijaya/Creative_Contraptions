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
    int dx, dy, id2, id1;
    char *rb;               /* penunjuk, bukan int: menghindari "mov cx,..; mov si,cx" */
    char *r1;
    char *r2;
    int spr;

    rb = (char *)recbase;
    id1 = tab[i];
    r1 = rb + id1 * 0xc;
    id2 = tab[i + 1];
    r2 = rb + id2 * 0xc;
    if (i + 1 < n && r2[1] - 100 == r1[1]) {
        /* TERNARY, bukan "if" tanpa else. Biner: cmp ax,80h / store dx /
           jl skip / sub ax,100h / jmp done / skip: reload dx / done:
           -- ada cabang else yang MEMUAT ULANG nilainya. */
        dx = r2[4];
        dx = (dx > 0x7f) ? dx - 0x100 : dx;
        dy = r2[5];
        dy = (dy > 0x7f) ? dy - 0x100 : dy;
        if (sp < 0) {
            load(a, rb, id2, b);
            spr = b;
        }
        else
            spr = *(int *)(((sp + id2) - id1) * 0xc + 10);
        blit(spr, x + dx, y + dy, r2[2], r2[3]);
    }
    dx = r1[4];
    dx = (dx > 0x7f) ? dx - 0x100 : dx;
    dy = r1[5];
    dy = (dy > 0x7f) ? dy - 0x100 : dy;
    if (sp < 0) {
        load(a, recbase, id1, b);
        spr = b;
    }
    else
        spr = *(int *)(sp * 0xc + 10);
    blit(spr, x + dx, y + dy, r1[2], r1[3]);
}

/* ⏳ BELUM COCOK — 397 byte vs 392 (5 KELEBIHAN). Perjalanan:
 * 370 -> 373 -> 399 -> 397. Divergensi pertama bergerak +3 -> +26 -> +62.
 *
 * SUDAH COCOK & JANGAN DIUBAH:
 *   - bingkai 18h dan URUTAN SLOT: dx@bp+8, dy@0ah, id2@0ch, id1@0eh,
 *     rb@10h, r1@12h, r2@14h, spr@16h
 *   - `rb` = salinan lokal recbase (biner memuatnya sekali "a1 3c 07")
 *   - pemulihan tanda dx/dy memakai TERNARY, bukan "if" tanpa else
 *     (biner punya cabang else yang MEMUAT ULANG nilainya) -- ini yang
 *     memindahkan hasil dari 19 byte KURANG ke 7 byte KELEBIHAN
 *   - record diakses lewat penunjuk char (r1[1], r1[2], ...) = displacement
 *
 * SISA 5 byte, di +62:
 *     kita: mov cx,[rb] / add cx,ax / mov si,cx     (7 byte)
 *     asli: mov si,[rb] / add si,ax                 (5 byte)
 * SUDAH DICOBA & GAGAL: rb sebagai penunjuk char (399 -> 397, membantu 2 byte
 * tapi belum menghapus "mov si,cx").
 */
