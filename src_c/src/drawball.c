/* FUN_1000_26ae @ 1000:26ae, 102 byte — gambar bola + tukar halaman buffer.
 *
 *   ticks @0x2e4 (dihitung mundur ISR timer), xform() = FUN_1000_5e3b
 *   page @0x2e0 / page2 @0x2e2 = pasangan alamat halaman gambar, ditukar tiap panggil
 *   Salinan koordinat frame sebelumnya: prevtop @0x262, prevy @0x264,
 *   prevx @0x266, prevrow @0x26a  (sumbernya balltop/bally/ballx/ballrow)
 *
 * Bingkai "sub sp,2" = TANPA lokal; nilai-nilai cukup hidup di register.
 * Urutan penyalinan di bawah mengikuti biner (top, row, y, x) — bukan urutan alamat.
 */

extern int ticks;           /* @0x2e4 */
extern int page;            /* @0x2e0 */
extern int page2;           /* @0x2e2 */
extern int balltop;         /* @0x25c */
extern int bally;           /* @0x25e */
extern int ballx;           /* @0x260 */
extern int ballrow;         /* @0x268 */
extern int prevtop;         /* @0x262 */
extern int prevy;           /* @0x264 */
extern int prevx;           /* @0x266 */
extern int prevrow;         /* @0x26a */

drawball(n)
int n;
{
    if (n > 0) {
        while (ticks > 0)
            ;
        ticks = n;
    }
    xform();
    if (page == 0x26c) {
        page2 = 0x26c;
        page = 0x284;
    }
    else {
        page2 = 0x284;
        page = 0x26c;
    }
    prevtop = balltop;
    prevrow = ballrow;
    prevy = bally;
    prevx = ballx;
}

/* ⏳ BELUM COCOK — 97 byte vs 102 (5 KURANG).
 * Asli menaruh SEMUA konstanta halaman di register lebih dulu:
 *     b8 6c 02   mov ax,26ch          <- untuk pembandingan
 *     8b 1e ..   mov bx,[page]
 *     3b d8      cmp bx,ax
 *     b8 84 02   mov ax,284h          <- lalu nilai baru
 *     bb 6c 02   mov bx,26ch
 *     a3 ..      mov [page],ax
 *     89 1e ..   mov [page2],bx
 * Kita selalu dapat store-immediate langsung (c7 06 .. / 81 3e ..).
 * SUDAH DICOBA & GAGAL: konstanta di kiri (0x26c == page), menukar urutan
 * penugasan page/page2. Dugaan berikutnya: kedua nilai berasal dari variabel
 * (mis. sepasang global atau elemen array) yang isinya 0x26c/0x284, bukan
 * konstanta literal di sumber.
 */
