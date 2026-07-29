/* FUN_1000_3105 @ 1000:3105, 37 byte — layar menu bertabel 0x18f8 (12 entri).
 * Sama persis polanya dengan menu9 (bingkai minimum, tanpa lokal).
 */

extern char mtab12[];       /* tabel entri menu @0x18f8 */

menu12()
{
    int unused;

    setsel(mtab12, 12);
    runmenu(mtab12, 12);
}
