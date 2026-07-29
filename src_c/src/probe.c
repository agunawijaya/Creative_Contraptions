/* Probe codegen MS C 1.04 — mempelajari pola yang dipakai kompiler,
 * supaya rekonstruksi tidak menebak-nebak.
 *
 * f1: fungsi 1 argumen TANPA lokal  -> prolog seperti apa? (asli pakai "mov bx,sp")
 * f2: hasil-kali word TINGGI lewat cast unsigned long
 * f3: sama, tapi lewat variabel long (punya lokal -> harusnya muncul bingkai BP)
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
    return (unsigned long)n * (unsigned long)seed >> 16;
}

int f3(n)
unsigned n;
{
    unsigned long p;
    p = (unsigned long)n * (unsigned long)seed;
    return p >> 16;
}
