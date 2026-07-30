/* FUN_1000_5936 @ 1000:5936, 30 byte — bersihkan/gambar ulang kotak papan utama.
 *
 * Satu panggilan saja: fillrect() = FUN_1000_6869 (primitif assembly).
 * Argumen didorong kanan-ke-kiri: 1, 0xc7, 0x12f, 0xc0, 0x10 -> jadi
 * fillrect(0x10, 0xc0, 0x12f, 0xc7, 1) = (x0, y0, x1, y1, warna/pola).
 * 0x10..0x12f = 16..303 mendatar, 0xc0..0xc7 = 192..199 menurun — jalur
 * setinggi 8 piksel di dasar layar, yaitu baris status.
 *
 * Bingkai NOL: tak ada `sub sp`, prolognya cuma "push bp; mov bp,sp" dan
 * epilognya "mov sp,bp; pop bp; ret" (bentuk untuk fungsi tanpa lokal yang
 * memanggil fungsi lain).
 */

redraw()
{
    fillrect(0x10, 0xc0, 0x12f, 0xc7, 1);
}
