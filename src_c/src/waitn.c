/* FUN_1000_2b11 @ 1000:2b11, 35 byte — jeda `n` bingkai TANPA bisa dibatalkan.
 *
 * Kembaran pause() (0x31b0) tapi tanpa cek keyhit() di syarat for. Bedanya
 * kecil di sumber, besar di perilaku: ini dipakai showsc() untuk menahan
 * tampilan skor supaya tidak terlewat karena pemain sedang menekan tombol.
 *
 *   vbend()  = FUN_1000_5da1 ; vbwait() = FUN_1000_5d98
 * Keduanya berpasangan = tepat satu bingkai layar per putaran.
 *
 * Bingkai 4 = 2 + 2x1 lokal (`i` di bp+2), argumen `n` di bp+8 -- identik
 * dengan pause(). Lihat src_c/src/pause.c untuk kenapa cek tombol di syarat
 * `for` menghasilkan byte yang berbeda jauh.
 */

waitn(n)
int n;
{
    int i;

    for (i = 0; i < n; i++) {
        vbend();
        vbwait();
    }
}
