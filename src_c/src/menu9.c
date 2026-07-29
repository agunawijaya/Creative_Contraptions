/* FUN_1000_30bb @ 1000:30bb, 37 byte — tampilkan layar menu bertabel 0x1634 (9 entri).
 * Pola sama untuk beberapa layar menu: pasang sorotan lalu jalankan menunya.
 *   setsel()  = FUN_1000_3769  (siapkan/gambar entri + sorotan)
 *   runmenu() = FUN_1000_34cc  (loop pilih)
 * Tidak ada variabel lokal: "sub sp,2" = bingkai minimum.
 */

extern char mtab9[];        /* tabel entri menu @0x1634 */

menu9()
{
    int unused;

    setsel(mtab9, 9);
    runmenu(mtab9, 9);
}
