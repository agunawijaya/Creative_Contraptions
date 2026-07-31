/* FUN_1000_171f @ 1000:171f (114 byte) — siapkan layar lalu tulis judulnya.
 *
 * Dipanggil `main` enam kali dengan pola (N, tabel, indeks, a, b) — lihat
 * catatan tanda tangan di main_.c.
 *
 *   setupscr()=1620  f15d0()=15d0 (belum direkonstruksi)  showsc()=2a86
 *   text()=6453
 */

extern int mode;                /* @0x792 */
extern int schi;                /* @0x732 */
extern int sclo;                /* @0x730 */

f171f(kind, tab, idx, a, b)
int  kind;
int *tab;
int  idx, a, b;
{
    /* Bingkai 0x54 padahal hanya satu slot yang dirujuk ([bp+0x52]).
       Sisanya ruang yang tetap dipesan tapi tak pernah disentuh; bagaimana
       ia terbagi antara temp dan lokal mati TIDAK bisa diketahui dari biner
       (tak ada satu pun rujukan). Jadi ukuran pengganjal dipilih supaya
       `t` jatuh tepat di 0x52 dan bingkai jadi 0x54 -- itu yang teramati. */
    char pad[80];
    int  t;

    if (kind == 2 || kind == 1)
        setupscr(1);
    else
        setupscr(0);
    f15d0(a, b);
    if (mode == 4)
        showsc(sclo, schi, 0);
    else {
        t = tab[idx];
        text(t, 0xc8, 0, 1, 1, 2);
    }
}
