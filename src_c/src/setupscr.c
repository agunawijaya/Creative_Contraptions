/* FUN_1000_1620 @ 1000:1620, 255 byte — siapkan layar permainan.
 *
 * Bersihkan bilah atas & badan layar, gambar sprite kepala, lalu gambar deretan
 * bola "nyawa/goal" di kiri (satu per goal yang sudah dilewati). Bilah bawah
 * diwarnai tergantung mode dan apakah skor sudah bergerak.
 *
 *   mode @0x792 ; sclo @0x730, schi @0x732 (skor 32-bit sbg pasangan word)
 *   goal @0x718 ; prevtop @0x262, prevx @0x266
 *   fillrect()=6869, blit()=672f, setball()=2a53 (sudah direkonstruksi)
 *
 * SLOT dari disassembly: i@bp+2 (pencacah loop), col@bp+4 (warna bilah).
 * Urutan deklarasi mengikuti itu: i lebih dulu.
 */

extern int  mode;           /* @0x792 */
extern int  sclo;           /* @0x730 */
extern int  schi;           /* @0x732 */
extern int  goal;           /* @0x718 */
extern int  prevtop;        /* @0x262 */
extern int  prevx;          /* @0x266 */
extern char hdrspr[];       /* @0x526 */

setupscr(sub)
int sub;
{
    int i, col;

    fillrect(0, 0, 0x13f, 7, 3);
    fillrect(0, 8, 0x13f, 0x9f, 1);
    if (mode == 0 || mode == 1)
        col = 1;
    else
        col = 0;
    /* OR BITWISE, bukan || logis: biner memakai "mov ax,[schi]; or ax,[sclo]"
       satu uji, bukan dua pembandingan berurutan (hemat 5 byte). */
    if (mode == 4 && (schi | sclo) != 0)
        fillrect(0, 0xa8, 0x13f, 199, 0);
    else
        fillrect(0, 0xa0, 0x13f, 199, col);
    blit(hdrspr, 0, 0x88, 8, 0x30);
    for (i = 0; i < goal; i++) {
        /* URUTAN INI dibalik dari yang "masuk akal": store konstanta
           ter-hoist dipancarkan TERBALIK, dan biner menulis prevx dulu.
           Diverifikasi src_c/verify/symcheck.py. */
        prevtop = 0x140;
        prevx = 0x140;
        setball(0, i * 10);
    }
    if (sub == 1 && mode != 0 && mode != 1)
        fillrect(0x10, 0xc0, 0x12f, 199, 1);
}
