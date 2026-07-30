/* Probe #13 - lanjutan probe11/12. Keduanya GAGAL mereproduksi: bentuk sumber
 * dan ukuran bingkai sama-sama bukan pemicunya. Sisa beda antara probe dan
 * loadcon: di loadcon do-while itu DIBUNGKUS `if (want == -1) { ... } else
 * pick = want + first;` -- cabang else juga menugasi `pick`.
 */

extern int gA, gB, lastvar;

/* y1: dengan cabang else yang juga menugasi pick */
y1(want)
int want;
{
    int cnt, first, pick;

    if (want == -1) {
        do {
            pick = rnd(cnt) + first;
        } while (gA == gB && cnt >= 2 && pick == lastvar);
        gA = cnt;
        lastvar = pick;
    }
    else
        pick = want + first;
    return pick;
}

/* y2: tanpa cabang else */
y2(want)
int want;
{
    int cnt, first, pick;

    if (want == -1) {
        do {
            pick = rnd(cnt) + first;
        } while (gA == gB && cnt >= 2 && pick == lastvar);
        gA = cnt;
        lastvar = pick;
    }

    return pick;
}
