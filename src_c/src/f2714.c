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
 * ✅ COCOK byte-per-byte (122/122). Bingkai 4 (murni temp, tanpa lokal).
 *
 * ⭐ SATU perubahan membawanya dari 62% ke cocok penuh: `scrptr` dideklarasikan
 * `char *`, bukan `int` yang dicor `*(char *)`. Divergensi lama sudah benar
 * terlokalisasi (aslinya MEMUAT ULANG `mov si,[3AEh]` tiap pembacaan sedangkan
 * kita menyimpan kursor di register) -- yang salah cuma DIAGNOSISNYA: itu
 * bukan soal urutan pernyataan melainkan soal TIPE. Penunjuk asli dimuat
 * langsung ke SI tiap kali dirujuk; bentuk cor memaksa lewat AX dan membuat
 * kompiler menahan nilainya di register.
 *
 * ⚠ Catatan lama "beda dari f278e: di sini bentuk dua-pernyataan yang benar"
 * KELIRU dan sudah dicabut. Kedua fungsi memakai tipe yang sama; yang berbeda
 * memang cuma post-increment (f278e) vs `scrptr++` terpisah (di sini), dan
 * itu memang mengikuti aslinya.
 */

extern char *scrptr;            /* @0x3ae  kursor baca skrip */
extern int  ballx;              /* @0x260 */
extern int  bally;              /* @0x25e */
extern int  balltop;            /* @0x25c */
extern int  ballrow;            /* @0x268 */

f2714(dx, dy)
int dx, dy;
{
    /* Tanpa lokal: bingkai 4 byte itu murni temp. */
    ballx = ((*scrptr >= 0xc8) ? *scrptr - 0x100 : *scrptr) + dx;
    scrptr++;
    balltop = 0xc7 - ballx;
    bally = ((*scrptr >= 0xc8) ? *scrptr - 0x100 : *scrptr) + dy;
    scrptr++;
    ballrow = bally / 4;
    drawball(1);
}
