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
    int i, px, py;

    for (i = 1; i < n; i++) {
        px = x1 + ((x2 - x1) * i) / n;
        balltop = 199 - px;
        py = y1 + ((y2 - y1) * i) / n;
        bally = py;
        ballx = px;
        ballrow = py / 4;
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

/* ⏳ BELUM COCOK — versi ini 160 byte vs 163.
 * Yang sudah dicoba dan GAGAL (jangan diulang):
 *  a) menghoist dx=x2-x1, dy=y2-y1 ke lokal lalu memakai ekspresi inline
 *     dua kali  -> 38 byte beda
 *  b) memakai global (ballx/bally) sebagai penampung lalu dibaca lagi
 *     -> 139 byte (terlalu pendek)
 * Fakta dari biner: (x2-x1) dan (y2-y1) DIHITUNG SEKALI SEBELUM loop dan
 * disimpan (dx@bp+2), pencacah i@bp+4 -- jadi ada 3 slot lokal terpakai.
 * Berarti px/py memang bukan lokal. Cari bentuk yang memakai dx/dy hoisted
 * TAPI hanya menghitung px sekali per iterasi tanpa slot lokal ketiga.
 */
