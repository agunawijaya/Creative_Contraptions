/* FUN_1000_149d @ 1000:149d, 307 byte — isi jawaban benar untuk semua slot.
 *
 * Kocok kandidat dulu, lalu untuk tiap slot i tentukan id yang dicari
 * (acak kalau level 3 dan slot ditandai, kalau tidak dari tabel jawaban),
 * cari id itu di daftar kandidat, dan catat indeks + jawabannya.
 * Terakhir gambar seluruh contraption.
 *
 *   busy @0x840 (1 = sedang mengisi), nmech @0x3ac, lvl3 @0x738, mark[] @0x76a
 *   shuffle()=3909, rnd()=5a5b, place()=4e3e
 *
 * SLOT dari disassembly: bp+2, bp+8, bp+0ah, bp+0eh dipakai; bingkai 12h.
 * Strukturnya sekeluarga dengan autofill (0x5954).
 */

extern int busy;            /* @0x840 */
extern int nmech;           /* @0x3ac */
extern int lvl3;            /* @0x738 */
extern int mark[];          /* @0x76a */

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
    /* EMPAT lokal di biner (bp+2, 8, 0ah, 0eh): hasil shuffle dan rnd
       DITAMPUNG dulu, bukan langsung dipakai. Urutan di biner:
       busy=0; u=shuffle(); busy=1; i=0; nmech=u; */
    /* i@bp+8, j@bp+0ah, found@bp+0eh. Hasil shuffle() TIDAK ditampung lokal:
       biner langsung "a3 [nmech]" tanpa store perantara. */
    char pad[2];        /* satu slot lagi: array selalu dialokasikan */
    int i, j, t, found;

    busy = 0;
    nmech = shuffle(c, s1, tq, n, s2);
    busy = 1;
    i = 0;
    /* "while (i < n)" dgn place() DI LUAR loop (pola sama spt autofill). */
    while (i < n) {
        if (lvl3 == 3 && mark[i] != 0) {
            t = rnd(nmech);
            tt[i] = b[t * 0xc];
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


/* ⏳ BELUM COCOK — 304 byte vs 307, bingkai 10h vs 12h (kurang satu slot).
 * Perjalanan: 294 -> 297 -> 305 -> 304.
 * SUDAH TERBUKTI dari disassembly:
 *   - ada bendera `found`: biner me-nol-kan DUA lokal bersamaan di 1533
 *     ("xor ax,ax; mov [bp+0ah],ax; mov [bp+0eh],ax")
 *   - hasil shuffle() TIDAK ditampung lokal (langsung "a3 [nmech]")
 *   - loop berbentuk "while (i < n)" dgn place() DI LUAR loop
 *   - slot: i@bp+8, j@bp+0ah, found@bp+0eh, dan satu lagi di bp+2
 * SUDAH DICOBA & GAGAL: "char pad[2]" untuk memaksa slot tambahan (tak berubah).
 * Langkah berikut: cari tahu variabel apa yang menempati bp+2 -- karena i@bp+8
 * berarti ada TIGA slot sebelum i (bp+2,4,6), jadi urutan deklarasi kita masih
 * salah, bukan cuma jumlahnya.
 */
