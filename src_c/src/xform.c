/* FUN_1000_5e3b @ 1000:5e3b, 107 byte — TRANSFORM koordinat logis -> layar + gambar.
 *
 * Inilah fungsi yang selama ini disebut "belum diturunkan" di CODE_MAP: ia yang
 * mengubah koordinat LOGIS bola (ballx@0x260, bally@0x25e) jadi posisi layar
 * sungguhan, memakai tabel sub-pixel ber-indeks (bally % 4).
 *
 *   tblA @0x2cc, tblB @0x2d4  = tabel geser sub-pixel, 4 entri masing-masing
 *   sx @0x2dc, sy @0x2de      = hasil geser yang dipakai penggambar
 *   page @0x2e0, page2 @0x2e2 = pasangan halaman gambar
 *   buf1 @0x29c, buf2 @0x2b4  = buffer baris
 *   prep()=6939, blend()=5ea6, putmsk()=6524, draw()=657c   (semuanya assembly)
 */

extern int ballx;           /* @0x260 */
extern int bally;           /* @0x25e */
extern int tblA[];          /* @0x2cc */
extern int tblB[];          /* @0x2d4 */
extern int sx;              /* @0x2dc */
extern int sy;              /* @0x2de */
extern int page;            /* @0x2e0 */
extern int page2;           /* @0x2e2 */
extern char buf1[];         /* @0x29c */
extern char buf2[];         /* @0x2b4 */

xform()
{
    /* TANPA lokal: di fungsi ini bingkai = 4 + 2*jumlah_lokal, jadi
       nol lokal -> sub sp,4 seperti aslinya. (Basis bingkai TIDAK
       selalu 2 -- bandingkan delay() yang basisnya 2.) */
    sx = tblA[bally % 4];
    sy = tblB[bally % 4];
    prep(ballx, bally, page);
    blend(page, page2, buf1, buf2);
    putmsk(buf2, page2);
    draw(page, sy, sx);
}
