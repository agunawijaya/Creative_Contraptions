/* FUN_1000_2a53 @ 1000:2a53, 51 byte — pasang posisi bola lalu gambar.
 *
 *   ballx @0x260, bally @0x25e  = koordinat LOGIS bola (bukan posisi layar —
 *       lihat CODE_MAP.md, transform ke layar dikerjakan FUN_1000_5e3b)
 *   balltop @0x25c = 199 - x    (jarak ke dasar layar)
 *   ballrow @0x268 = y / 4      (baris kasar; pembagian INT bertanda -> cdq/idiv,
 *       kompiler 1983 tidak mengubahnya jadi geser bit)
 *   drawball() = FUN_1000_26ae
 */

extern int ballx;           /* @0x260 */
extern int bally;           /* @0x25e */
extern int balltop;         /* @0x25c */
extern int ballrow;         /* @0x268 */

setball(x, y)
int x, y;
{
    ballx = x;
    balltop = 199 - x;
    bally = y;
    ballrow = y / 4;
    drawball(0);
}
