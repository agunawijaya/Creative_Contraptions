/* FUN_1000_149d @ 1000:149d, 307 byte — isi jawaban benar untuk semua slot.
 *
 * Kocok kandidat dulu, lalu untuk tiap slot i tentukan id yang dicari
 * (acak kalau level 3 dan slot ditandai, kalau tidak dari tabel jawaban),
 * cari id itu di daftar kandidat, dan catat indeks + jawabannya.
 * Terakhir gambar seluruh contraption.
 *
 *   busy @0x840 (1 = sedang mengisi), nmech @0x3ac, lvl3 @0x738, markf[] @0x76a
 *   mkpal()=3909, rnd()=5a5b, place()=4e3e
 *
 * SLOT dari disassembly: bp+2, bp+8, bp+0ah, bp+0eh dipakai; bingkai 12h.
 * Strukturnya sekeluarga dengan autofill (0x5954).
 */

extern int busy;            /* @0x840 */
extern int nmech;           /* @0x3ac */
extern int lvl3;            /* @0x738 */
extern int markf[];          /* @0x76a */

fillans(a, b, c, d, e, n, ans, flag, tq, tr, ts, tt, s1, s2)
int   a;
char *b;
int   c, d, e, n;
int  *ans;
int  *flag;
int  *tq;
char *tr;
int  *ts;
int  *tt;
int   s1, s2;
{
    /* EMPAT lokal di biner (bp+2, 8, 0ah, 0eh): hasil mkpal dan rnd
       DITAMPUNG dulu, bukan langsung dipakai. Urutan di biner:
       busy=0; u=mkpal(); busy=1; i=0; nmech=u; */
    /* i@bp+8, j@bp+0ah, found@bp+0eh. Hasil mkpal() TIDAK ditampung lokal:
       biner langsung "a3 [nmech]" tanpa store perantara. */
    int i, j, t, found, unused;   /* t & unused: slot bp+0ch dan bp+10h
                                    memang DILEWATI biner (bingkai 12h) */

    busy = 0;
    nmech = mkpal(c, s1, tq, n, s2);
    busy = 1;
    i = 0;
    /* "while (i < n)" dgn place() DI LUAR loop (pola sama spt autofill). */
    while (i < n) {
        if (lvl3 == 3 && markf[i] != 0) {
            tt[i] = b[rnd(nmech) * 0xc];
        }
        else
            tt[i] = tq[i * 3 + 2];
        found = 0;
        for (j = 0; j < nmech; j++) {
            if (b[tr[j] * 0xc] == tt[i]) {
                ts[i] = j;
                ans[i] = tr[j];
                flag[i] = -1;
                found = 1;
                break;
            }
        }
        i = i + 1;
    }
    place(a, b, c, d, e, n, ans, flag);
}


/* ✅ COCOK BYTE-PER-BYTE (307 byte). Dua hal yang menutupnya:
 *  1. Hasil `rnd()` TIDAK ditampung lokal: `tt[i] = b[rnd(nmech) * 0xc];`.
 *  2. Ada lokal KELIMA yang tak pernah dipakai (slot bp+10h dilewati biner),
 *     jadi bingkainya 12h bukan 10h. `int unused;` di ujung daftar deklarasi.
 */
