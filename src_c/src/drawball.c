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
        page = 0x284;
        page2 = 0x26c;
    }
    else {
        page = 0x26c;
        page2 = 0x284;
    }
    prevtop = balltop;
    prevrow = ballrow;
    prevy = bally;
    prevx = ballx;
}


/* ⏳ BELUM COCOK — 97 byte vs 102 (5 KURANG).
 * Asli memuat KEDUA konstanta ke register dulu lalu menyimpan:
 *     b8 6c 02 / 8b 1e [page] / 3b d8   (banding)
 *     b8 84 02 / bb 6c 02 / a3 [page] / 89 1e [page2]   (simpan)
 * Kita selalu dapat store-immediate (c7 06 .. / 81 3e ..).
 * SUDAH DICOBA & GAGAL: konstanta di kiri (0x26c == page) -> 97;
 * menukar urutan page/page2 -> 97; page/page2 sbg PENUNJUK ke buffer
 * beralamat 0x26c/0x284 -> 84 (terlalu pendek).
 */
