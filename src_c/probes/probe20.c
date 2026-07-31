/* PROBE 20 — bentuk mana yang memancarkan `mov ax,3 / imul word ptr [mem]`?
 *
 * Di animvm (0x1afd) aslinya memuat KONSTANTA ke AX lalu `imul` dengan operan
 * MEMORI langsung (5 byte). Draf kita memuat VARIABEL ke AX, konstanta ke BX,
 * lalu `imul bx` (8 byte) — selisih 3 byte yang menggeser sisa fungsi.
 *
 * Menukar urutan operan di sumber (`c1 * 3` -> `3 * c1`) TIDAK mengubah apa pun,
 * jadi penyebabnya bukan urutan. Probe ini menguji apakah KONTEKS-nya yang
 * menentukan: indeks larik vs ekspresi biasa, dan ada/tidaknya penunjuk lain
 * yang masih hidup di titik itu.
 */

extern int  tab[];

p20a(a)                         /* indeks larik, variabel dulu */
int a;
{
    return tab[a * 3 + 2];
}

p20b(a)                         /* indeks larik, konstanta dulu */
int a;
{
    return tab[3 * a + 2];
}

p20c(a, t)                      /* lewat PARAMETER penunjuk, bukan extern */
int a;
int *t;
{
    return t[a * 3 + 2];
}

p20d(a, t, u)                   /* DUA penunjuk hidup bersamaan */
int a;
int *t, *u;
{
    return u[a] != t[a * 3 + 2];
}
