/* PROBE 19 — dari mana datangnya slot bingkai berisi KONSTANTA 100 (long)?
 *
 * Di f2823 (0x2823) ada lokal long di [bp+0x1c] yang diisi 100 SEKALI di awal
 * fungsi lalu dipakai sebagai pembagi di DUA tempat. Pertanyaannya: apakah itu
 *   (a) literal int `100` yang dipromosikan kompiler ke slot bingkai,
 *   (b) literal long `100L`, atau
 *   (c) VARIABEL long yang memang ditulis programmernya.
 *
 * Ketiganya ditulis dengan bentuk ekspresi yang identik supaya perbedaan yang
 * muncul HANYA berasal dari bentuk pembaginya.
 */

p19a(a, fx, tx, n)
int a, fx, tx, n;
{
    long xbase;
    long lna;

    lna = -a;
    xbase = (long)(tx - fx) + lna * n * n / 100;
    return (int)xbase;
}

p19b(a, fx, tx, n)
int a, fx, tx, n;
{
    long xbase;
    long lna;

    lna = -a;
    xbase = (long)(tx - fx) + lna * n * n / 100L;
    return (int)xbase;
}

p19c(a, fx, tx, n)
int a, fx, tx, n;
{
    long xbase;
    long lna;
    long hun;

    lna = -a;
    hun = 100;
    xbase = (long)(tx - fx) + lna * n * n / hun;
    return (int)xbase;
}
