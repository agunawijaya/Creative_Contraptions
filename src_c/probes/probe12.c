/* Probe #12 - lanjutan probe11. Di probe11 SEMUA varian meng-commit store
 * `pick` segera (benar). Jadi bentuk sumbernya bukan pemicunya; yang berbeda
 * antara probe11 dan loadcon adalah KONTEKS:
 *   probe11 : cnt/lastvar global, first PARAMETER, pick di bp+2 (bingkai kecil)
 *   loadcon : cnt/first/pick semuanya LOKAL di bingkai 0x124 (slot >= 0xec,
 *             sehingga store-nya butuh displacement 16-bit: 89 86 f0 00)
 * Probe ini menguji apakah UKURAN BINGKAI / lebar displacement yang menentukan.
 */

extern int gA, gB, lastvar;

/* x1: bingkai kecil, semua lokal */
x1()
{
    int small[2];
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* x2: bingkai besar (216 byte array) seperti loadcon */
x2()
{
    int big[108];
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}
