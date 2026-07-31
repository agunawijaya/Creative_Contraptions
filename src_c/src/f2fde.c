/* FUN_1000_2fde @ 1000:2fde (45 byte) dan FUN_1000_300b @ 1000:300b (21 byte).
 *
 * DUA fungsi kecil dalam satu berkas — keduanya menampilkan sepotong teks lalu
 * mengosongkan penyangga papan ketik. Ditemukan saat merekonstruksi `main`,
 * yang memanggil yang pertama dari case 1 (mode ensiklopedia).
 *
 * ⚠ Keduanya TIDAK punya lokal maupun temp: prolognya `push bp; mov bp,sp`
 * TANPA `sub sp,N`. Menambahkan satu lokal saja akan memunculkan `sub sp`
 * dan merusak kecocokan.
 *
 *   fillrect()=6869  show()=381a  kbflush()=36ef
 */

f2fde()
{
    /* Bersihkan seluruh layar di bawah baris 8, lalu tulis pesannya. */
    fillrect(0, 8, 0x13f, 0x9f, 1);
    show(0xc04, 7);
    kbflush();
}

f300b()
{
    show(0xca2, 3);
    kbflush();
}
