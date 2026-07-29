/* FUN_1000_2b77 @ 1000:2b77, 410 byte — gambar baris petunjuk di bawah layar.
 *
 * Teks yang ditampilkan tergantung mode, sub-mode, level, dan apakah contraption
 * sedang dalam keadaan gagal. Semua string adalah alamat di DGROUP.
 *
 *   mode @0x792, sub @0x3b2, failed @0x842, lvl @0x734, goal @0x718
 *   text() = FUN_1000_6453 (skala 1x1)
 *
 * SLOT dari disassembly: bp+2 dan bp+4 dipakai; bingkai 6.
 */

extern int  mode;           /* @0x792 */
extern int  sub;            /* @0x3b2 */
extern int  failed;         /* @0x842 */
extern int  lvl;            /* @0x734 */
extern int  goal;           /* @0x718 */

extern char s_a37[];        /* @0xa37 */
extern char s_a3e[];        /* @0xa3e */
extern char s_a5d[];        /* @0xa5d */
extern char s_a7b[];        /* @0xa7b */
extern char s_a95[];        /* @0xa95 */
extern char s_aab[];        /* @0xaab */
extern char s_ac1[];        /* @0xac1 */
extern char s_ad4[];        /* @0xad4 */
extern char s_ae9[];        /* @0xae9 */
extern char s_afe[];        /* @0xafe */

prompts()
{
    int row, done;

    if (mode != 0 && mode != 1) {
        if (mode == 4)
            row = 0x15;
        else
            row = 0x14;
        if (failed == 0)
            text(s_a37, 0x80, row * 8 + 2, 1, 1, 3);
    }
    /* SATU penugasan dari ekspresi boolean, bukan if/else: biner memakai
       "xor ax,ax; inc ax" / "xor ax,ax" lalu SATU store yang ditunda
       (89 46 04 muncul setelah cabang menyatu). */
    done = (sub == 6 && failed == 0);
    if (mode == 4 && (done || (lvl == 2 && goal <= 1)   /* cmp 1/jg, bukan cmp 2/jge */)) {
        goal = 0;
        text(s_a3e, 0x20, 0xc0, 1, 1, 2);
    }
    /* Cabang GAGAL diuji DULU dan badannya ditaruh tepat setelah ujinya
       (je +1dh di biner), bukan dilompati jauh. */
    else if (failed != 0)
        text(s_a5d, 0x28, 0xc0, 1, 1, 2);
    else {
        if (mode == 4)
            text(s_a7b, 0x38, 0xc0, 1, 1, 2);
        else if (mode == 0)
            text(s_a95, 0x48, 0xc0, 1, 1, 2);
        else {
            if (mode == 1) {
                text(s_aab, 0x40, 0xac, 1, 1, 2);
                text(s_ac1, 0x40, 0xb6, 1, 1, 2);
            }
            else {
                text(s_ad4, 0x40, 0xac, 1, 1, 2);
                text(s_ae9, 0x40, 0xb6, 1, 1, 2);
            }
            text(s_afe, 0x10, 0xc0, 1, 1, 2);
        }
    }
}
