/* FUN_1000_3734 @ 1000:3734, 53 byte — bunyi kedua (deskriptor nada @0x1ddb).
 * Pola sama dengan tone(), plus simpan/pulihkan konteks suara:
 *   sndsave() = FUN_1000_5a7f  (dipanggil dgn 0x670e = alamat buffer)
 *   sndrest() = FUN_1000_5ac9
 */

extern int  sndmode;        /* @0x722 */
extern int *sndptr;         /* @0x720 */
extern int  tune2[];        /* deskriptor nada @0x1ddb */
extern      sndisr();       /* @0x670e -- ISR timer (keyio.asm), bukan buffer */

tone2()
{
    int unused;

    sndsave(sndisr);
    sndoff();
    sndptr = tune2;
    sndmode = 2;
    sndon();
    delay(5);
    sndoff();
    sndrest();
}
