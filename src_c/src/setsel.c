/* FUN_1000_3769 @ 1000:3769, 177 byte — siapkan layar pilihan lalu gambar
 * deretan `n` record tampilan.
 *
 * Tiga langkah pembuka:
 *   fillrect(0, 0, 0x13f, 7, 3)      baris atas (8 piksel) diisi warna 3
 *   blit(0x526, 0, 0x88, 8, 0x30)    sprite 0x526 di kiri, y=136, 8x48
 *   fillrect(0, 8, 0x13f, 0xc7, 1)   sisa layar diisi warna 1
 * lalu badan loop yang SAMA PERSIS dengan show() (0x381a) — dibandingkan
 * byte-per-byte, 102 byte ekornya identik kecuali dua displacement `call`.
 * Jadi kode ini memang diduplikasi di sumber aslinya, bukan memanggil show().
 *
 *   fillrect() = FUN_1000_6869 ; blit() = FUN_1000_672f ; text() = FUN_1000_6453
 *
 * Dua nol pada fillrect pertama dipancarkan sebagai SATU "xor ax,ax" dengan DUA
 * "push ax" — ciri dua argumen `int` 0 yang di-CSE (bandingkan dengan `long 0`
 * yang me-nol-kan register ULANG; lihat README).
 *
 * Bingkai 8 = 2×1 lokal (`i` di bp+6) + 2×3 temp, identik dengan show().
 */

struct item {
    char kind;              /* +0  <0x80 = teks, >=0x80 = sprite */
    char pad1;              /* +1  */
    int  x;                 /* +2  */
    int  y;                 /* +4  */
    char a;                 /* +6  */
    char b;                 /* +7  */
    char c;                 /* +8  hanya dipakai cabang teks */
    char pad9;              /* +9  */
    int  spr;               /* +10 nomor sprite / alamat string */
};                          /* = 0xc byte */

setsel(p, n)
struct item *p;
int   n;
{
    int i;

    fillrect(0, 0, 0x13f, 7, 3);
    blit(0x526, 0, 0x88, 8, 0x30);
    fillrect(0, 8, 0x13f, 0xc7, 1);
    for (i = 0; i < n; i++) {
        if (p->kind < 0x80)
            text(p->spr, p->y, p->x, p->b, p->a, p->c);
        else
            blit(p->spr, p->x, p->y, p->a, p->b);
        p++;
    }
}
