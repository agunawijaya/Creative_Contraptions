/* FUN_1000_5318 @ 1000:5318, 5 byte — fungsi KOSONG.
 *
 *   5318  55        push bp
 *   5319  8b ec     mov  bp,sp
 *   531b  5d        pop  bp
 *   531c  c3        ret
 *
 * Itu persis yang dipancarkan MS C 1.04 untuk badan kosong: prolog + epilog,
 * tanpa apa pun di antaranya. Tidak ada `xor ax,ax`, jadi nilai baliknya
 * memang tidak diset — bukan `return 0`, melainkan benar-benar `{ }`.
 *
 * TIDAK ADA satu pun `call` di biner yang menunjuk ke sini (dipindai
 * byte-per-byte atas E8 di 0x0082..0x9062). Jadi ia mati di rilis — sisa
 * rutin yang isinya dicabut, sama seperti `setup` (0x5F90) yang tinggal
 * `SUB AX,AX / RET`. Dua-duanya menunjukkan pola yang sama: fungsi yang
 * dikosongkan tapi pemanggilnya ikut dihapus.
 *
 * Ditulis bukan karena ada yang memanggilnya, melainkan karena byte-nya ADA
 * di biner asli: tanpa modul ini, tata letak seluruh isi sesudahnya bergeser
 * 5 byte. Ia satu-satunya lubang yang tersisa di wilayah kode 0x82..0x6a48.
 */

f5318()
{
}
