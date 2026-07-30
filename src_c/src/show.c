/* FUN_1000_381a @ 1000:381a, 108 byte — gambar deretan `n` record tampilan.
 *
 * Tiap record 0xC byte. Byte ke-0 memilih jenisnya: < 0x80 = TEKS, selain itu
 * SPRITE. (char di MS C 1.04 UNSIGNED, jadi biner memuatnya dengan
 * "mov al,[si]; xor ah,ah" lalu "cmp ax,80h" — bukan uji tanda.)
 *
 *   text() = FUN_1000_6453 ; blit() = FUN_1000_672f  (dua-duanya assembly)
 *
 * ⭐ KUNCI BENTUK: recordnya diakses lewat penunjuk STRUCT, bukan hitung alamat.
 * Biner memuat basis SEKALI ("mov si,[bp+0ch]") lalu memakai displacement dari
 * SI untuk byte MAUPUN kata: "8a 44 07" (mov al,[si+7]) dan "ff 74 02"
 * (push [si+2]). Bentuk `*(int *)(p + 10)` TIDAK bisa menghasilkan itu — ia
 * memancarkan "mov ax,si; add ax,0ah; push [bx/si]" dan membengkak jadi 176
 * byte dengan bingkai 0eh (3 temp ekstra). Dengan struct: 108 byte, bingkai 8.
 * Kenaikan `p++` pun jadi "add word ptr [bp+0ch], 0ch" sendirinya.
 *
 * Urutan argumen dibaca dari urutan PUSH (kanan-ke-kiri):
 *   teks  : push cx,bx,ax,[si+2],[si+4],[si+0ah]
 *   sprite: push bx,ax,[si+4],[si+2],[si+0ah]
 * Perhatikan x/y TERTUKAR antara dua cabang — itu memang begitu di biner.
 *
 * Bingkai 8 = 2×1 lokal (`i` di bp+6) + 2×3 temp (bp+0,2,4); lokal menempati
 * slot TERATAS. `p` adalah ARGUMEN yang dimaju-majukan sendiri, bukan salinan.
 */

struct item {
    char kind;              /* +0  <0x80 = teks, >=0x80 = sprite */
    char pad1;              /* +1  tak dipakai fungsi ini */
    int  x;                 /* +2  */
    int  y;                 /* +4  */
    char a;                 /* +6  */
    char b;                 /* +7  */
    char c;                 /* +8  hanya dipakai cabang teks */
    char pad9;              /* +9  tak dipakai fungsi ini */
    int  spr;               /* +10 nomor sprite / alamat string */
};                          /* = 0xc byte */

show(p, n)
struct item *p;
int   n;
{
    int i;

    for (i = 0; i < n; i++) {
        if (p->kind < 0x80)
            text(p->spr, p->y, p->x, p->b, p->a, p->c);
        else
            blit(p->spr, p->x, p->y, p->a, p->b);
        p++;
    }
}
