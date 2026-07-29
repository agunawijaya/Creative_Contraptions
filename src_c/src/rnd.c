/* FUN_1000_5a5b @ 1000:5a5b, 25 byte — generator acak kongruen linier.
 *
 * Dipakai game untuk memilih varian contraption & mengocok palet part.
 * Seed = variabel global 16-bit di DGROUP:0x71a.
 *
 * GAYA: K&R (MS C 1.04 = pra-ANSI, 1983). Parameter dideklarasikan SETELAH
 * baris nama fungsi, tanpa prototype.
 *
 * Target byte (dari CONTRAP_UNPACKED.EXE):
 *   8b dc            mov  bx, sp
 *   b8 85 3e         mov  ax, 3e85h
 *   f7 26 1a 07      mul  word ptr [seed]
 *   05 19 36         add  ax, 3619h
 *   a3 1a 07         mov  [seed], ax
 *   8b 47 02         mov  ax, [bx+2]        <- parameter n
 *   f7 26 1a 07      mul  word ptr [seed]
 *   8b c2            mov  ax, dx            <- ambil word TINGGI hasil kali
 *   c3               ret
 */

unsigned seed;

int rnd(n)
unsigned n;
{
    seed = seed * 0x3e85 + 0x3619;
    return (int)(((long)n * (long)seed) >> 16);
}
