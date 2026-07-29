/* FUN_1000_370e @ 1000:370e, 38 byte — bunyi pendek (klik/beep menu).
 *
 *   sndoff() = FUN_1000_5a74   (2 byte, assembly)
 *   sndon()  = FUN_1000_5a76   (2 byte, assembly)
 *   sndmode @0x722, sndper @0x720 = parameter speaker PC
 *   delay(5) = FUN_1000_2692, sudah direkonstruksi
 */

extern int sndmode;         /* @0x722 */
extern int sndper;          /* @0x720 */

tone()
{
    int unused;

    sndoff();
    sndper = 0x1dd0;
    sndmode = 2;
    sndon();
    delay(5);
}

/* ⏳ BELUM COCOK — 8 byte beda mulai +9.
 * Asli:  b8 d0 1d      mov ax,1dd0h      <- MEMUAT ke AX dulu
 *        c7 06 22 07 02 00               mov word [sndmode],2
 *        a3 20 07                        mov [sndper],ax
 * Kita:  c7 06 .. 02 00 / c7 06 .. d0 1d  (dua store immediate langsung)
 * Sudah dicoba: menukar urutan kedua penugasan -> tidak berubah.
 * Yang belum dicoba: sndper/sndmode sebagai elemen array, atau penugasan
 * berantai. Perlu satu putaran probe seperti probe3.c.
 */
