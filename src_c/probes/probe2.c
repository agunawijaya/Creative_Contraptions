/* Probe #2 — MS C 1.04 TIDAK punya tipe "unsigned long" (probe #1: Error 77).
 * Tipe yang tersedia: char, int, unsigned, long, float, double.
 *
 * f1: 1 argumen tanpa lokal   -> pola prolog (asli: "mov bx,sp", tanpa bingkai BP)
 * f2: satu cast saja          -> apakah jadi mul tunggal + ambil DX?
 * f3: perkalian melebar int*int -> long
 */

unsigned seed;

int f1(n)
int n;
{
    return n + 1;
}

int f2(n)
unsigned n;
{
    return ((long)n * seed) >> 16;
}

long f3(a, b)
unsigned a, b;
{
    return (long)a * b;
}
