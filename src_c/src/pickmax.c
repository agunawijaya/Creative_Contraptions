/* FUN_1000_4e01 @ 1000:4e01, 61 byte — ambil nilai acak TERBESAR dari sekumpulan undian.
 *
 *   best  @0x82e  (dimulai dari -1000 = 0xfc18)
 *   count @0x82c  (dikurangi satu dulu, lalu dipakai sebagai batas ulangan)
 *   range @0x830  (batas atas undian)
 *   rnd() = FUN_1000_5a5b (assembly, LCG)
 */

extern int best;            /* @0x82e */
extern int count;           /* @0x82c */
extern int range;           /* @0x830 */

pickmax()
{
    int r, i;

    best = -1000;
    count = count - 1;
    for (i = 0; i < count; i++) {
        r = rnd(range);
        if (r > best)          /* HARUS r di kiri: aslinya "cmp ax,[best]"
                               langsung; menulis (best < r) memaksa kompiler
                               memuat best ke register dulu -> 2 byte lebih */
            best = r;
    }
}
