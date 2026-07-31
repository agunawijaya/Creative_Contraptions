/* FUN_1000_278e @ 1000:278e (149 byte) — gambar satu part dari skrip.
 *
 * Baca SATU byte dari kursor skrip sebagai nomor part relatif, ambil
 * record-nya, lalu blit spritenya pada (x + dx, y + dy).
 *
 * ⚠ DUA pola byte yang BERBEDA dalam satu fungsi:
 *   - nomor part dibaca TANPA pemulihan tanda (cuma `xor ah,ah`)
 *   - geser dx/dy dipulihkan tandanya dengan ambang 0xC8, bukan 0x80
 *
 * ⚠ Menunggu `ticks` (0x2E4) turun ke <= 0 lalu menyetelnya 1 -- gelung
 * tunggu kosong `while (ticks > 0) ;`
 *
 *   blit()=672f
 *
 * ⏳ DRAF KASAR: 160 byte vs 149, TERJAJAR 21/149 (14%). Bingkai 0x14 vs
 * 0x10 -- KELEBIHAN 4, artinya ekspresi kita menuntut temp lebih banyak dari
 * aslinya (bukan soal pengganjal; tidak ada pengganjal di sini).
 * SUDAH DICOBA: `*(int *)(rp + 6)` -> `((int *)rp)[3]` memangkas 7 byte
 * (167 -> 160) tapi belum menutup selisih temp.
 * Yang belum dicoba: memakai penunjuk `struct rec *` alih-alih int + cast,
 * atau memecah ekspresi blit ke variabel antara.
 */

extern int  scrptr;             /* @0x3ae */
/* ⚠ 0x2E4 SUDAH bernama `ticks` di berkas lain -- JANGAN beri nama kedua. */
extern int  ticks;              /* @0x2e4 */

f278e(x, y, base, recs)
int  x, y, base;
char *recs;
{
    int rp;
    int idx;
    int dx, dy;

    idx = base + *(char *)scrptr;
    scrptr++;
    rp = (int)recs + idx * 0xc;
    dx = ((char *)rp)[4];
    dx = (dx >= 0xc8) ? dx - 0x100 : dx;
    dy = ((char *)rp)[5];
    dy = (dy >= 0xc8) ? dy - 0x100 : dy;
    while (ticks > 0)
        ;
    ticks = 1;
    blit(((int *)rp)[3], x + dx, y + dy,
         ((char *)rp)[2], ((char *)rp)[3]);
}
