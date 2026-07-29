/* FUN_1000_2692 @ 1000:2692, 28 byte — tunggu timer habis.
 *
 * Dipakai opcode 0x02 VM animasi sebagai jeda. Variabel `ticks` adalah pencacah
 * 16-bit di DGROUP:0x2e4 yang dihitung-mundur oleh ISR timer, jadi loop kosong
 * di bawah memang menunggu interupsi — bukan kesalahan tulis.
 *
 * GAYA: K&R (MS C 1.04 pra-ANSI): parameter dideklarasikan setelah baris nama,
 * tanpa prototype, tanpa "void".
 *
 * Target byte:
 *   55            push bp
 *   83 ec 02      sub  sp, 2
 *   8b ec         mov  bp, sp
 *   8b 46 06      mov  ax, [bp+6]      <- parameter n
 *   85 c0         test ax, ax
 *   7e 03         jle  +3
 *   a3 e4 02      mov  [ticks], ax
 *   83 3e e4 02 00  cmp word ptr [ticks], 0
 *   7f f7         jg   -9
 *   83 c4 02      add  sp, 2
 *   5d            pop  bp
 *   c3            ret
 */

int ticks;

delay(n)
int n;
{
    if (n > 0)
        ticks = n;
    while (ticks > 0)
        ;
}
