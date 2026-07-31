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
 * Bingkai asli 0x28: temp [00..13], lalu lokal MENAIK sesuai urutan deklarasi —
 * xbase@14, lna@18, hun@1c, li@20, i@24, dy@26.
 *
 * `hun` BUKAN literal: probe19 membuktikan `x / 100` dan `x / 100L` sama-sama
 * memancarkan `xor cx,cx / mov dx,64h` langsung di tempat pembagian, sedangkan
 * hanya VARIABEL long yang memberi slot bingkai berisi 100 yang diisi sekali
 * lalu dibaca dua kali — persis seperti aslinya. Probe yang sama juga
 * menunjukkan `(tx - fx)` TIDAK boleh dicor `(long)`: aslinya menyimpan hasil
 * int-nya dulu dan baru memperluas tandanya di titik penjumlahan.
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
    long hun;
    long li;
    int  i;
    int  dy;

    lna = -a;
    hun = 100;
    xbase = (tx - fx) + lna * n * n / hun;
    dy = ty - fy;
    for (i = 1; i < n; i++) {
        li = i;
        ballx = fx + xbase * i / n - lna * i * i / hun;
        balltop = 0xc7 - ballx;
        bally = fy + dy * li / n;
        ballrow = bally / 4;
        drawball(flag);
    }
    ballx = tx;
    balltop = 0xc7 - ballx;
    bally = ty;
    ballrow = bally / 4;
    drawball(flag);
    sndptr = sndnull;
    sndmode = 0;
}
