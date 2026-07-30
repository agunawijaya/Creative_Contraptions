/* FUN_1000_2a86 @ 1000:2a86, 139 byte — tampilkan skor di bilah atas.
 *
 *   sprintf(buf, fmt, lo, hi) = FUN_1000_7464 -- rutin MC.LIB, TERBUKTI lewat
 *     src_c/verify/libmatch.py (modul SPRINTF). Dulu keliru dinamai
 *     sprintf() dan diberi stub; nama pustakanya cukup.
 *   fillrect() = FUN_1000_6869 ; text() = FUN_1000_6453 ; line() = FUN_1000_5cbb
 *   tone() = FUN_1000_370e (sudah direkonstruksi) ; waitn() = FUN_1000_2b11 (BUKAN pause() @0x31b0 -- fungsi BERBEDA)
 *   Skor 32-bit disimpan sebagai PASANGAN word (lo,hi) — MS C 1.04 tidak punya
 *   unsigned long, jadi penjumlahannya dikerjakan tangan dengan carry.
 *
 * BINGKAI BER-ARRAY: "sub sp,16h" = 22 = array 20 byte + 2. Jadi pola bingkai
 * untuk fungsi ber-array lokal = ukuran_array + 2.
 * Kalau flash!=0, bilah dikedipkan (garis XOR digambar dua kali) + bunyi.
 */

extern char fmtstr[];       /* @0xa30 */

showsc(lo, hi, flash)
int lo, hi, flash;
{
    char buf[20];

    sprintf(buf, fmtstr, lo, hi);
    fillrect(0xd0, 0, 0x110, 7, 3);
    text(buf, 0xd0, 0, 1, 1, 2);
    if (flash >= 2) {      /* aslinya cmp 2 / jl -- bentuk >1 jadi cmp 1 / jle */
        line(0, 0, 0x13f, 7, 1);
        tone();
        waitn(0x14);
        line(0, 0, 0x13f, 7, 1);
    }
}
