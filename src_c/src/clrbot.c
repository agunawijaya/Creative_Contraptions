/* FUN_1000_5911 @ 1000:5911, 37 byte — bersihkan bilah bawah layar, balikan 32.
 *
 * fillrect(x1=0, y1=0xa8, x2=0x13f, y2=199, warna=0) = FUN_1000_6869
 * y 0xa8..199 = 24 baris terbawah (bilah status), x 0..319 = selebar layar.
 * Nilai balik 32 dipakai pemanggil sebagai tinggi bilah.
 *
 * "sub sp,4" = satu lokal yang tidak pernah dipakai (sama seperti menu11).
 */

clrbot()
{
    int unused, unused2;

    fillrect(0, 0xa8, 0x13f, 199, 0);
    return 0x20;
}
