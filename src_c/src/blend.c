/* FUN_1000_5ea6 @ 1000:5ea6, 234 byte — salin bagian sel bola yang BERTUMPANG
 * antara posisi lama dan posisi baru.
 *
 * Sel bola = 8 kolom x 3 baris = 24 byte. Fungsi ini:
 *   1. mengosongkan kedua mask (24 byte masing-masing),
 *   2. menyusuri kolom x dari `ballx` sampai `ballx+8`, dan baris y dari
 *      `ballrow` sampai `ballrow+3`,
 *   3. untuk sel yang juga masuk kotak LAMA (prevx..prevx+8, prevrow..prevrow+3)
 *      menyalin piksel dari buffer lama dan menandai kedua mask 0xff.
 * Sel di luar tumpangan dilewati: penunjuk tujuan dimaju-majukan 3 (satu kolom).
 *
 *   ballx @0x260, ballrow @0x268, prevx @0x266, prevrow @0x26a
 *   ballx == 0x140 (320) = bola tidak aktif -> langsung keluar.
 *
 * PETA SLOT (bingkai 18h, temp di bp+0/bp+2; lokal bp+4..16h berurutan):
 *   bp+4  i     (dipakai DUA KALI: pencacah loop pengosongan, lalu kolom x)
 *   bp+6  y
 *   bp+8  t     (indeks di buffer lama; store-nya DITUNDA ke akhir blok)
 *   bp+0ah xe   = ballx + 8
 *   bp+0ch pxe  = prevx + 8
 *   bp+0eh pye  = prevrow + 3
 *   bp+10h ye   = ballrow + 3
 *   bp+12h base = (i - prevx) * 3 - prevrow
 *   bp+14h p, bp+16h q  (salinan dmask/smask untuk loop pengosongan)
 * Argumen: bp+1ch dst, 1eh src, 20h dmask, 22h smask — dst & dmask dimajukan
 * LANGSUNG di stack pemanggil, bukan lewat salinan lokal.
 */

extern int ballx;           /* @0x260 */
extern int prevx;           /* @0x266 */
extern int ballrow;         /* @0x268 */
extern int prevrow;         /* @0x26a */

blend(dst, src, dmask, smask)
char *dst;
char *src;
char *dmask;
char *smask;
{
    int i, y, t, xe, pxe, pye, ye, base;
    char *p;
    char *q;

    if (ballx != 0x140) {
        p = dmask;
        q = smask;
        /* Penugasan BERANTAI: biner memuat "mov bl,0" SEKALI lalu dua store
           byte, dan yang ditulis lebih dulu adalah *q (kanan ke kiri). */
        for (i = 0; i < 0x18; i++)
            *p++ = *q++ = 0;
        xe = ballx + 8;
        pxe = prevx + 8;
        pye = prevrow + 3;
        ye = ballrow + 3;
        for (i = ballx; i < xe; i++) {
            if (i >= prevx && i < pxe) {
                base = (i - prevx) * 3 - prevrow;
                for (y = ballrow; y < ye; y++) {
                    if (y >= prevrow && y < pye) {
                        t = base + y;
                        *dst = src[t];
                        /* DUA pernyataan, bukan berantai. Biner memuat
                           "mov al,0ffh" lalu langsung store ke *dmask, BARU
                           menghitung alamat smask+t. Bentuk berantai
                           "smask[t] = *dmask = 0xff" menghitung alamat
                           smask+t LEBIH DULU (lvalue kiri dievaluasi awal)
                           dan itu 2 byte lebih. */
                        *dmask = 0xff;
                        smask[t] = 0xff;
                    }
                    dmask = dmask + 1;
                    dst = dst + 1;
                }
            }
            else {
                dmask = dmask + 3;
                dst = dst + 3;
            }
        }
    }
}
