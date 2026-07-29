/* FUN_1000_370e @ 1000:370e, 38 byte — bunyi pendek (klik/beep menu).
 *
 *   sndoff() = FUN_1000_5a74   (assembly)
 *   sndon()  = FUN_1000_5a76   (assembly)
 *   sndmode @0x722, sndptr @0x720
 *
 * KUNCI: 0x1dd0 bukan bilangan biasa, melainkan ALAMAT di DGROUP — penunjuk ke
 * deskriptor nada. Karena alamat itu relokatabel, kompiler wajib memuatnya ke AX
 * dulu ("mov ax,OFFSET tune1") baru menyimpan, bukan store-immediate langsung.
 * Menulisnya sebagai konstanta biasa menghasilkan "c7 06 .. d0 1d" dan TIDAK cocok.
 * Bukti pendukung: FUN_1000_18db menyimpan "&local_40" ke 0x720 — memang penunjuk.
 */

extern int  sndmode;        /* @0x722 */
extern int *sndptr;         /* @0x720 */
extern int  tune1[];        /* deskriptor nada @0x1dd0 */

tone()
{
    int unused;

    sndoff();
    sndptr = tune1;
    sndmode = 2;
    sndon();
    delay(5);
}
