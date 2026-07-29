/* FUN_1000_666a @ 1000:666a, 147 byte — DEKODER RLE aset (escape 0xE4).
 *
 * Format: 0xE4 <jumlah> <nilai> -> nilai diulang <jumlah> kali; byte lain literal.
 * Dekoder yang sama sudah diport ke Python (port/cc/assets.py:decode_rle).
 *
 *   src = data terkompresi, dst = tujuan, n = jumlah byte SUMBER yang diproses
 *   Balikan = jumlah byte HASIL yang ditulis.
 *
 * DUA HAL YANG MENENTUKAN BENTUKNYA:
 * 1. Penunjuk DIMAJUKAN untuk membaca ("s = s + 1; cnt = *s;"), BUKAN diindeks
 *    ("cnt = s[1]"). Bentuk indeks menghasilkan kode 11 byte lebih pendek.
 * 2. Tata letak slot dari biner: i@bp+4, j@bp+6, out@bp+8, cnt@bp+0ah,
 *    val@bp+0bh, s@bp+0ch, d@bp+0eh. cnt & val bersebelahan sebagai char
 *    (masing-masing 1 byte) -> urutan deklarasi harus persis begini.
 * 0xE4 muncul di Ghidra sebagai -0x1c karena char bertanda di sana; di MS C 1.04
 * char justru unsigned, jadi perbandingan langsung dengan 0xe4 benar.
 */

unrle(src, dst, n)
char *src;
char *dst;
int n;
{
    int i, j, out;
    char cnt, val;
    char *s, *d;

    i = 0;
    out = 0;
    s = src;
    d = dst;
    while (i < n) {
        if (*s == 0xe4) {
            s = s + 1;
            cnt = *s;
            s = s + 1;
            val = *s;
            for (j = 0; j < cnt; j++) {
                *d++ = val;         /* post-increment: "mov bx,[d]; inc [d]" */
                out++;
            }
            s++;                    /* s++ SEBELUM i += 3 */
            i += 3;
        }
        else {
            *d++ = *s++;
            out++;
            i++;
        }
    }
    return out;
}

/* ⏳ BELUM COCOK — 141 byte vs 147 (6 kurang).
 * Tata letak slot & pemajuan penunjuk sudah benar (dari 11 kurang jadi 6).
 * Sisa selisih ada SETELAH loop dalam; periksa bagaimana i dan s dimajukan
 * di ujung cabang 0xE4 (mungkin bukan "i = i + 3" melainkan tiga penambahan,
 * atau s dimajukan lagi sebelum i).
 */
