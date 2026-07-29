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
    int u, i, j, t;

    busy = 0;
    u = shuffle(c, s1, tq, n, s2);
    busy = 1;
    i = 0;
    nmech = u;
    for (;;) {
        if (n <= i) {
            place(a, b, c, d, e, n, ans, flag);
            return;
        }
        if (lvl3 == 3 && mark[i] != 0) {
            t = rnd(nmech);
            tt[i] = b[t * 0xc];
        }
        else
            tt[i] = tq[i * 3 + 2];
        for (j = 0; j < nmech; j++) {
            if (b[tr[j] * 0xc] == tt[i]) {
                ts[i] = j;
                ans[i] = tr[j];
                flag[i] = -1;
                break;
            }
        }
        i = i + 1;
    }
}

/* ⏳ BELUM COCOK — 297 byte vs 307 (10 KURANG). Perjalanan: 294 -> 297.
 * SUDAH TERBUKTI: biner punya EMPAT lokal (bp+2, 8, 0ah, 0eh) -- hasil
 * shuffle() dan rnd() DITAMPUNG variabel dulu, dan urutannya
 * "busy=0; u=shuffle(); busy=1; i=0; nmech=u;".
 * SISA: masih 10 byte kurang; slot bp+4/6/0ch/10h di biner kemungkinan temp,
 * tapi jumlah temp kita masih lebih sedikit. Langkah berikut: kejar divergensi
 * pertama (sekarang sudah lewat prolog) untuk menemukan ekspresi yang di biner
 * lebih panjang -- kandidat: akses "b[tr[j]*0xc] == tt[i]" yang mungkin
 * memakai bentuk penunjuk/struct, bukan indeks langsung.
 */
