/* FUN_1000_2714 @ 1000:2714 (122 byte) — baca satu langkah bola dari skrip.
 *
 * Mengambil DUA byte BERTANDA berturut dari kursor skrip (global 0x3AE),
 * menambahkannya ke basis (dx, dy) yang dioper pemanggil, lalu memperbarui
 * posisi bola dan menggambarnya.
 *
 * ⚠ Ambang tandanya 0xC8 (200), BUKAN 0x80. Jadi nilai 0x80..0xC7 tetap
 * POSITIF di sini -- rentangnya sengaja digeser supaya koordinat sampai 199
 * bisa disimpan dalam satu byte.
 *
 *   drawball()=26ae
 *
 * ⏳ DRAF KASAR: 125 byte vs 122, TERJAJAR 76/122 (62%). Bingkai 4 TEPAT.
 * SUDAH DICOBA & GAGAL: menukar urutan balltop/scrptr++ (3 bentuk, termasuk
 * penugasan bersarang `balltop = 0xc7 - (ballx = ...)`) -- tidak satu pun
 * menaikkan penjajaran.
 * ⭐ DIVERGENSI SUDAH TERLOKALISASI (0x273A): aslinya `inc word ptr [3AEh]`
 * -- menaikkan kursor DI MEMORI lalu MEMUAT ULANG (`mov si,[3AEh]`) untuk
 * pembacaan berikutnya. Punya kita menyimpan kursor di register
 * (`mov bx,[3AEh]; inc bx`) dan memakainya ulang, jadi 3 byte lebih pendek
 * di satu tempat dan lebih panjang di tempat lain.
 * ⚠ BEDA dari f278e: di sana post-increment satu-ekspresi (`*(char*)p++`)
 * yang benar; di SINI justru bentuk dua-pernyataan dengan muat-ulang.
 * Yang belum dicoba: menyisipkan pemakaian scrptr lain di antaranya, atau
 * memaksa muat ulang dengan menulis `scrptr = scrptr + 1;`.
 */

extern int  scrptr;             /* @0x3ae  kursor baca skrip (char *) */
extern int  ballx;              /* @0x260 */
extern int  bally;              /* @0x25e */
extern int  balltop;            /* @0x25c */
extern int  ballrow;            /* @0x268 */

f2714(dx, dy)
int dx, dy;
{
    /* Tanpa lokal: bingkai 4 byte itu murni temp. */
    ballx = ((*(char *)scrptr >= 0xc8) ? *(char *)scrptr - 0x100
                                       : *(char *)scrptr) + dx;
    scrptr++;
    balltop = 0xc7 - ballx;
    bally = ((*(char *)scrptr >= 0xc8) ? *(char *)scrptr - 0x100
                                       : *(char *)scrptr) + dy;
    scrptr++;
    ballrow = bally / 4;
    drawball(1);
}
