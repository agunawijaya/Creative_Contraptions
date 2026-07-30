/* FUN_1000_4bb9 @ 1000:4bb9, 75 byte — susutkan bilah waktu satu langkah (mode Mix Up).
 *
 *   mode @0x792 — hanya jalan di mode 4
 *   tw @0x7f0   = lebar langkah; tx @0x7ee = posisi ujung bilah sekarang
 *   ta @0x7ec, tb @0x7ea = salinan lebar (dipakai penggambar lain)
 *   fillrect() = FUN_1000_6869 ; refresh() = FUN_1000_5c84
 *
 * DUA HAL YANG SEMPAT SALAH:
 * 1. TANPA variabel lokal ("sub sp,2"). Nilainya cukup hidup di register: tw di AX,
 *    tx-1 di BX. Memberi nama lokal justru menambah slot dan meleset 7 byte.
 * 2. Batas bawah ditulis "tx >= 0", BUKAN "tx > -1". Aslinya "test bx,bx; js"
 *    (uji tanda); "> -1" menghasilkan "cmp bx,-1; jle" yang lebih panjang.
 */

extern int mode;            /* @0x792 */
extern int tw;              /* @0x7f0 */
extern int tx;              /* @0x7ee */
extern int ta;              /* @0x7ec */
extern int tb;              /* @0x7ea */

timebar()
{
    if (mode != 4)
        return;
    /* dibalik: store ter-hoist dipancarkan TERBALIK, biner menulis ta dulu */
    tb = tw;
    ta = tw;
    tx = tx - 1;
    if (tx < 0x140 && tx >= 0) {
        fillrect(tx, 0xa2, 0x13f, 0xa5, 0);
        refresh();
    }
}
