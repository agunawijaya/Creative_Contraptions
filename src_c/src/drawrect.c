/* FUN_1000_4009 @ 1000:4009, 139 byte — gambar bingkai kotak berukuran bebas.
 *
 *   line() = FUN_1000_5cbb (assembly)
 *   x == 0xff berarti "rata kanan": x dihitung jadi 320 - lebar.
 *   Empat garis: atas, kanan, bawah, kiri.
 */

drawrect(y, x, h, w, col)
int y, x, h, w, col;
{
    if (x == 0xff)
        x = 0x140 - w;
    line(x, y, x + w - 2, y, col);
    line(x + w - 1, y, x + w - 1, y + h - 1, col);
    line(x + 1, y + h - 1, x + w - 2, y + h - 1, col);
    line(x, y + 1, x, y + h - 1, col);
}
