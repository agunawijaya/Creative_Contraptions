/* FUN_1000_29b0 @ 1000:29b0, 163 byte — gerak bola LURUS (interpolasi linier).
 *
 * Versi sederhana dari FUN_1000_2823 (yang parabola). Bola digeser dari (x1,y1)
 * ke (x2,y2) dalam n langkah; tiap langkah menghitung ulang koordinat logis lalu
 * memanggil drawball(). Langkah terakhir dipaksa tepat di tujuan supaya tidak
 * meleset karena pembagian bilangan bulat.
 *
 *   balltop @0x25c = 199 - x ; bally @0x25e ; ballx @0x260 ; ballrow @0x268 = y/4
 *   drawball() = FUN_1000_26ae (sudah direkonstruksi)
 *   sndmode @0x722, sndptr @0x720 dinolkan di akhir (matikan bunyi gerak)
 */

extern int balltop;         /* @0x25c */
extern int bally;           /* @0x25e */
extern int ballx;           /* @0x260 */
extern int ballrow;         /* @0x268 */
extern int sndmode;         /* @0x722 */
extern int *sndptr;         /* @0x720 */
extern int sndnull[];       /* @0x724 */

moveball(a, x1, y1, x2, y2, n, d)
int a, x1, y1, x2, y2, n, d;
{
    int dx, i, dy;      /* slot dari biner: dx@bp+2, i@bp+4, dy@bp+6 */

    dx = x2 - x1;       /* selisih dihitung SEKALI sebelum loop */
    dy = y2 - y1;
    for (i = 1; i < n; i++) {
        balltop = 199 - (x1 + (dx * i) / n);
        bally = y1 + (dy * i) / n;
        ballx = x1 + (dx * i) / n;
        ballrow = bally / 4;
        drawball(d);
    }
    ballx = x2;
    bally = y2;
    balltop = 199 - x2;
    ballrow = y2 / 4;
    drawball(d);
    sndmode = 0;
    sndptr = sndnull;
}

/* ⏳ BELUM COCOK — panjang SUDAH TEPAT 163, struktur IDENTIK.
 * Satu-satunya beda: seluruh offset bp kita bergeser +2 karena ada SATU slot
 * sementara berlebih.
 *     kita: sub sp,0ah  -> bp+0,+2 scratch, dx@+4, i@+6, dy@+8
 *     asli: sub sp,08h  -> bp+0 scratch,    dx@+2, i@+4, dy@+6
 * Instruksinya sama persis (8b 46 .. / 2b 46 .. / f7 6e .. / 99 f7 fb).
 * Tinggal cari bentuk yang memakai satu scratch lebih sedikit.
 * SUDAH DICOBA & GAGAL (jangan diulang):
 *   - ballx dihitung dulu lalu balltop = 199 - ballx      -> 139 byte
 *   - ballrow dari ekspresi bersarang (y1+(dy*i)/n)/4     -> tetap 0ah
 *   - global dipakai sebagai penampung                    -> 139 byte
 *   - tanpa hoist dx/dy (int i, px, py)                   -> 160 byte
 */
