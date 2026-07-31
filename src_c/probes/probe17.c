/* Probe #17 — kelanjutan probe16. Struct vs larik TERBUKTI TIDAK menentukan
 * SI vs BX (ketiganya BX). Sekarang uji apakah pemilihnya adalah KODE
 * SESUDAHNYA -- yaitu apakah alokator melihat ke depan.
 *
 * Ekspresi yang diuji SAMA di semua varian; yang berbeda cuma apa yang
 * terjadi sesudah panggilan.
 *
 * v1: tidak ada apa-apa sesudahnya
 * v2: sesudahnya memakai tab lagi lewat indeks
 * v3: sesudahnya memakai DUA penunjuk sekaligus (tab dan buf)
 */

v1(tab, i, buf)
int *tab, i, *buf;
{
    return nvar(tab[i * 3 + 2], buf);
}

v2(tab, i, buf)
int *tab, i, *buf;
{
    int n;

    n = nvar(tab[i * 3 + 2], buf);
    return n + tab[i * 3];
}

v3(tab, i, buf)
int *tab, i, *buf;
{
    int n;

    n = nvar(tab[i * 3 + 2], buf);
    drawpair(tab[i * 3], tab[i * 3 + 1], buf[0], n);
    return n;
}
