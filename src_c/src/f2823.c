/* FUN_1000_2823 @ 1000:2823 (397 byte) — gerak bola PARABOLA.
 *
 * Memindahkan bola dari (fx,fy) ke (tx,ty) dalam n langkah: y bergerak
 * LINEAR, x linear ditambah lendutan parabola yang dikendalikan `a`.
 *
 * ⚠ Seluruh perhitungan pakai `long` (32-bit). MS C 1.04 tidak punya operasi
 * 32-bit, jadi tiap kali muncul panggilan pustaka: 0x69D7 = kali long,
 * 0x7040 = bagi long. Itu sebabnya fungsinya sepanjang ini.
 *
 * Semantiknya SUDAH TERVALIDASI 100% lewat jalur port
 * (`interp_2823` di port/cc/animvm.py, dicocokkan ke emulator), jadi rumusnya
 * TIDAK ditebak -- yang dicari di sini cuma BENTUK penulisannya.
 *
 *   drawball()=26ae
 *
 * ⏳ DRAF: 366 byte vs 397, TERJAJAR 118/397 (30%). Bingkai 0x20 vs 0x28 --
 * KURANG 8 byte, artinya aslinya punya DUA long lagi yang belum kita tulis.
 * Slot yang terlihat di biner: [14h/16h] long (xbase), [18h/1Ah] long (na),
 * [1Ch/1Eh] long berisi 100, [24h] i, [26h] dy, dan temp di [00h/02h/04h].
 * Slot [1Ch/1Eh] yang berisi KONSTANTA 100 sebagai long itu petunjuk kuat:
 * pembaginya kemungkinan variabel long, bukan literal `100`.
 *
 * KEMAJUAN: menyimpan `na` sebagai LONG dan menghitung `ty - fy` SEKALI
 * sebelum gelung menaikkan penjajaran 100 -> 118.
 */

extern int ballx;               /* @0x260 */
extern int bally;               /* @0x25e */
extern int balltop;             /* @0x25c */
extern int ballrow;             /* @0x268 */
extern int *sndptr;             /* @0x720 */
extern int sndmode;             /* @0x722 */
extern int sndnull[];           /* @0x724 */

f2823(a, fx, fy, tx, ty, n, flag)
int a, fx, fy, tx, ty, n, flag;
{
    long xbase;
    long lna;
    int  i;
    int  dy;

    /* `na` disimpan sebagai LONG (aslinya diperluas tandanya ke [bp+18h]
       lalu dipakai berulang), dan `ty - fy` dihitung SEKALI sebelum gelung
       (aslinya di [bp+26h]). */
    lna = -a;
    xbase = (long)(tx - fx) + lna * n * n / 100;
    dy = ty - fy;
    for (i = 1; i < n; i++) {
        ballx = fx + (int)(xbase * i / n - lna * i * i / 100);
        bally = fy + (int)((long)dy * i / n);
        balltop = 0xc7 - ballx;
        ballrow = bally / 4;
        drawball(flag);
    }
    ballx = tx;
    bally = ty;
    balltop = 0xc7 - tx;
    ballrow = ty / 4;
    drawball(flag);
    sndptr = sndnull;
    sndmode = 0;
}
