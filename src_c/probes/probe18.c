/* Probe #18 — probe17 menunjukkan: BX dipakai LEBIH DULU; SI/DI baru muncul
 * kalau LEBIH DARI SATU penunjuk hidup bersamaan.
 *
 * Konsekuensinya: aslinya memakai SI di f498c berarti di titik itu ada
 * penunjuk LAIN yang masih hidup. Uji bentuk sumber yang menahan satu
 * penunjuk tetap hidup melintasi panggilan.
 *
 * v1: ekspresi lepas (bentuk kita sekarang)     -> harusnya BX
 * v2: penunjuk ditahan di lokal lalu dipakai    -> harusnya SI?
 * v3: dua akses tab dalam SATU ekspresi          -> harusnya SI + BX
 */

v1(tab, i, buf)
int *tab, i, *buf;
{
    return nvar(tab[i * 3 + 2], buf);
}

v2(tab, i, buf)
int *tab, i, *buf;
{
    int *p;
    int  n;

    p = tab + i * 3;
    n = nvar(p[2], buf);
    return n + p[0];
}

v3(tab, i, buf)
int *tab, i, *buf;
{
    return nvar(tab[i * 3 + 2] + tab[i * 3], buf);
}
