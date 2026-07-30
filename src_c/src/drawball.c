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
extern char pbufA[];        /* buffer halaman @0x26c */
extern char pbufB[];        /* buffer halaman @0x284 */
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
    /* 0x26c/0x284 adalah ALAMAT buffer halaman, bukan angka biasa. Alamat
       relokatabel WAJIB lewat register ("mov ax,OFFSET x"), itulah sebabnya
       biner memuat kedua nilai ke AX/BX dulu baru menyimpan -- bukan
       store-immediate. Tipe page/page2 tetap int, jadi dipakai cast. */
    if (page == (int) pbufA) {
        page = (int) pbufB;
        page2 = (int) pbufA;
    }
    else {
        page = (int) pbufA;
        page2 = (int) pbufB;
    }
    prevtop = balltop;
    prevrow = ballrow;
    prevy = bally;
    prevx = ballx;
}

/* ⚠ TEMUAN symcheck.py yang BELUM dibereskan (2026-07-30).
 * Byte-nya cocok, tapi IDENTITAS simbolnya bergeser satu putaran:
 *     biner baca : ballx, ballrow, bally   -- kita: ballrow, bally, ballx
 *     biner tulis: prevrow, prevy, prevx   -- kita: prevy, prevx, prevrow
 * Dipasangkan lewat aturan store-terbalik, urutan sumber yang cocok adalah
 * `prevx = ballx; prevy = ballrow; prevrow = bally;` -- yang TIDAK masuk akal
 * secara semantik. Kemungkinan besar LABEL alamatnya sendiri yang salah
 * (prevy/prevrow/bally/ballrow tertukar di komentar @0x...), bukan kodenya.
 * Jangan asal tukar urutan penugasan sebelum label alamatnya diverifikasi
 * dari pemakaian di fungsi lain.
 */
