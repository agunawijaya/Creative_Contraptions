/* FUN_1000_3886 @ 1000:3886, 131 byte — gambar kotak sorotan menu (4 garis).
 *
 *   line(x1,y1,x2,y2,warna) = FUN_1000_5cbb (assembly, penggambar span XOR)
 *   param_1 = y atas, param_2 = x kiri. Kotak: lebar 0x1e, tinggi 0x17.
 *
 * Urutan hitung di biner: y+0x17, lalu x+1, baru x+0x1e — bukan urutan menaik.
 * Ikuti urutan itu, karena urutan penugasan menentukan alokasi register.
 */

drawbox(y, x)
int y, x;
{
    int xlf, xrt, ybot;   /* ybot HARUS ketiga: aslinya disimpan di bp+6 */

    ybot = y + 0x17;
    xlf = x + 1;
    xrt = x + 0x1e;
    line(xlf, y, x + 0x1d, y, 3);
    line(xrt, y, xrt, y + 0x16, 3);
    line(x + 2, ybot, xrt, ybot, 3);
    line(xlf, y + 1, xlf, ybot, 3);
}
