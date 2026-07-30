/* Probe #15 - probe14 menggugurkan `long`/struct. Sisa beda antara probe dan
 * loadcon: loadcon punya LABEL `done:` dan beberapa `goto done` -- label adalah
 * batas basic-block, dan MC2 bisa mengalokasikan register lebih konservatif di
 * fungsi yang memuat label.
 */

extern int gA, gB, lastvar, fh;

/* q1: TANPA label/goto (pembanding, diharapkan benar) */
q1(want)
int want;
{
    int cnt, first, pick;

    pick = 0;
    if (want == -1) {
        do {
            pick = rnd(cnt) + first;
        } while (gA == gB && cnt >= 2 && pick == lastvar);
    }
    return pick;
}

/* q2: ADA label `done:` dan satu `goto done` sebelum do-while */
q2(want)
int want;
{
    int cnt, first, pick;

    pick = 0;
    if (fh == -1)
        goto done;
    if (want == -1) {
        do {
            pick = rnd(cnt) + first;
        } while (gA == gB && cnt >= 2 && pick == lastvar);
    }
done:
    return pick;
}

/* q3: label ada tapi TIDAK ada goto sebelum do-while (label di akhir saja) */
q3(want)
int want;
{
    int cnt, first, pick;

    pick = 0;
    if (want == -1) {
        do {
            pick = rnd(cnt) + first;
        } while (gA == gB && cnt >= 2 && pick == lastvar);
        goto done;
    }
done:
    return pick;
}
