/* Probe #14 - bisect loadcon menunjuk ke DEKLARASI, bukan ke aliran kode.
 * probe11..13 (10 varian) semuanya benar; bedanya loadcon punya lokal `long`
 * dan array struct yang memuat `long`. MS C 1.04 memakai DX:AX untuk `long`,
 * jadi kehadirannya bisa mengubah alokasi register di seluruh fungsi.
 */

extern int gA, gB, lastvar;

struct ent { int id; long off; };

/* z1: tanpa long, tanpa struct (pembanding) */
z1()
{
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* z2: ada lokal `long` yang TIDAK dipakai */
z2()
{
    long off;
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* z3: ada array struct yang memuat long */
z3()
{
    struct ent dir[36];
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* z4: array int biasa ukuran sama (216 byte) */
z4()
{
    int dir[108];
    int cnt, first, pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}
