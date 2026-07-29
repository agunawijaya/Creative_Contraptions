/* FUN_1000_30e0 @ 1000:30e0, 37 byte — layar menu bertabel 0x1796 (11 entri).
 *
 * Isinya identik dengan menu9, TAPI bingkainya "sub sp,4" bukan "sub sp,2":
 * ada SATU variabel lokal yang dideklarasikan tapi tidak pernah dipakai
 * (tak ada satu pun store ke bp+2 di seluruh fungsi). Sisa kode penulis aslinya.
 * Variabel itu harus tetap ditulis, kalau tidak ukuran bingkai meleset 2 byte.
 */

extern char mtab11[];       /* tabel entri menu @0x1796 */

menu11()
{
    int unused, unused2;

    setsel(mtab11, 11);
    runmenu(mtab11, 11);
}
