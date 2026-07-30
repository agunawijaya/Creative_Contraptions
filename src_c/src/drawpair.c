/* FUN_1000_4a31 @ 1000:4a31, 392 byte — gambar satu part, plus "pasangannya"
 * kalau part berikutnya adalah lanjutan dari part ini.
 *
 * Dua record dibaca: milik slot i dan slot i+1. Kalau `row` record kedua tepat
 * 100 lebih dari yang pertama, keduanya satu kesatuan (mis. tali katrol yang
 * tergambar dua bagian) sehingga bagian kedua digambar lebih dulu.
 * Offset (dx,dy) di record adalah byte BERTANDA -- di MS C 1.04 char itu
 * unsigned, jadi tandanya dipulihkan dengan ternary "(v > 0x7f) ? v - 0x100 : v".
 *
 *   recbase @0x73c ; load()=53ff ; blit()=672f
 *
 * ⭐ Record diakses lewat PENUNJUK STRUCT (lihat "Varian ke-4" di README):
 * biner memakai displacement dari satu register -- "mov al,[si+4]",
 * "mov cl,[si+2]" -- dan menghitung r1/r2 dengan "imul 0ch" lalu "add bx,ax" /
 * "add si,ax" langsung ke register tujuan. Bentuk `char *r1` + `r1[4]` bisa
 * menghasilkan displacement juga, TAPI memaksa langkah tambahan
 * "mov cx,[rb]; add cx,ax; mov si,cx" saat menghitung r2.
 *
 * PETA SLOT (dari disassembly): bingkai 18h.
 *   bp+0..6   = 4 TEMP
 *   bp+8=dx, 0ah=dy, 0ch=id2, 0eh=id1, 10h=rb, 12h=r1, 14h=r2, 16h=spr
 * Argumen: 1ch=a, 1eh=b, 20h=x, 22h=y, 24h=tab, 26h=n, 28h=i, 2ah=sp
 *
 * Catat: KEDUA panggilan load() mendorong `word ptr [0x73c]` — yaitu GLOBAL
 * recbase, bukan salinan lokal `rb`. Lokal `rb` cuma dipakai menghitung r1/r2.
 */

struct part {
    char id;                /* +0  */
    char row;               /* +1  baris/tingkat; +100 = bagian lanjutan */
    char w;                 /* +2  lebar  */
    char h;                 /* +3  tinggi */
    char dx;                /* +4  geser x, BERTANDA */
    char dy;                /* +5  geser y, BERTANDA */
    char pad6;              /* +6  */
    char pad7;              /* +7  */
    char pad8;              /* +8  */
    char pad9;              /* +9  */
    int  spr;               /* +10 penunjuk data sprite */
};                          /* = 0xc byte */

/* Tabel penunjuk sprite per part, ARRAY GLOBAL di DGROUP 0x0a.
 * Buktinya displacement 16-BIT: "8b 87 0a 00" (mov ax,[bx+0000ah]). Kalau 0x0a
 * itu offset FIELD di dalam struct, kompiler memakai bentuk 8-bit "8b 47 0a" —
 * dan itulah yang keluar kalau ditulis sebagai cast-ke-penunjuk. Displacement
 * 16-bit = alamat global yang direlokasi linker. Entrinya 0xc byte dan yang
 * dibaca kata pertamanya, jadi basis array = 0x0a, bukan basis + 10. */
struct slot {
    int  spr;               /* +0  penunjuk data sprite */
    char rest[10];          /* +2..0bh */
};                          /* = 0xc byte */

extern struct slot sprtab[];    /* @0x0a */

extern int recbase;         /* @0x73c */

drawpair(a, b, x, y, tab, n, i, sp)
int   a, b, x, y;
int  *tab;
int   n, i, sp;
{
    /* Urutan slot dari biner: dx@bp+8, dy@0ah, id2@0ch, id1@0eh, rb@10h,
       r1@12h, r2@14h, spr@16h. `rb` menampung recbase: biner memuatnya SEKALI
       di awal ("a1 3c 07") lalu memakainya untuk KEDUA record. */
    int dx, dy, id2, id1;
    struct part *rb;
    struct part *r1;
    struct part *r2;
    int spr;

    rb = (struct part *)recbase;
    id1 = tab[i];
    r1 = rb + id1;
    id2 = tab[i + 1];
    r2 = rb + id2;
    if (i + 1 < n && r2->row - 100 == r1->row) {
        /* TERNARY, bukan "if" tanpa else. Biner: cmp ax,80h / store dx /
           jl skip / sub ax,100h / jmp done / skip: reload dx / done:
           -- ada cabang else yang MEMUAT ULANG nilainya. */
        dx = r2->dx;
        dx = (dx >= 0x80) ? dx - 0x100 : dx;
        dy = r2->dy;
        dy = (dy >= 0x80) ? dy - 0x100 : dy;
        if (sp >= 0)
            spr = sprtab[(sp + id2) - id1].spr;
        else {
            load(a, recbase, id2, b);
            spr = b;
        }
        blit(spr, x + dx, y + dy, r2->w, r2->h);
    }
    dx = r1->dx;
    dx = (dx >= 0x80) ? dx - 0x100 : dx;
    dy = r1->dy;
    dy = (dy >= 0x80) ? dy - 0x100 : dy;
    if (sp >= 0)
        spr = sprtab[sp].spr;
    else {
        load(a, recbase, id1, b);
        spr = b;
    }
    blit(spr, x + dx, y + dy, r1->w, r1->h);
}
