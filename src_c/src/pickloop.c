/* FUN_1000_2e90 @ 1000:2e90, 334 byte — loop pemilihan part oleh pemain.
 *
 * Mengocok kandidat, lalu berulang: bersihkan keyboard, gambar, dan panggil
 * pemilih (3c4f) untuk slot yang sedang aktif. Kalau pilihan berubah, catat
 * jawaban + sprite-nya dan tandai `changed`. Slot aktif maju melingkar.
 * Keluar dengan ESC (-1) atau ENTER.
 *
 *   nmech @0x3ac, seed @0x72a, cur @0x2e6, base @0x73a, idtab[] @0x2ea
 *   shuffle()=3909, kbflush()=36ef (sudah direkonstruksi), redraw()=5936,
 *   review()=3c4f, waitkey()=5911 (sudah direkonstruksi), place()=4e3e
 *
 * SLOT dari disassembly: bp+0ah, 0ch, 0eh; bingkai 10h (5 slot temp di bp+0..8).
 */

extern int  nmech;          /* @0x3ac */
extern int  seed;           /* @0x72a */
extern int  cur;            /* @0x2e6 */
extern int  base;           /* @0x73a */
extern char idtab[];        /* @0x2ea */

pickloop(a, n, tab, d, e, sel, f, ans, tt, g, h, k)
int   a;
char  n;
int  *tab;
int   d, e;
int  *sel;
int   f;
int  *ans;
int  *tt;
int   g, h, k;
{
    int r, changed, v;

    nmech = shuffle(seed, a, tab, n, f);
    changed = 0;
    for (;;) {
        kbflush();
        redraw();
        do {
            r = review(a, tab[cur * 3], tab[cur * 3 + 1], d, e, sel[cur], cur * 6);
            if (r != 0xffff) {
                v = r & 0x7fff;
                if (sel[cur] != v) {
                    changed = 1;
                    sel[cur] = v;
                    ans[cur] = idtab[v];
                    tt[cur] = *(char *)(base + ans[cur] * 0xc);
                }
                cur = cur + 1;
                if (n <= cur)
                    cur = 0;
            }
        } while (r >= 0);
        if (r == 0xffff)
            return -1;
        if (waitkey() == 0x1b) {
            r = 0xffff;
            break;
        }
        if (waitkey() != 0x0d)
            break;
    }
    if (changed && r != 0xffff)
        place(0x1a8, base, seed, h, k, n, ans, g, 0, 0);
    return r;
}

/* ⏳ BELUM COCOK — 339 byte vs 334 (percobaan ke-1).
 * Belum didiagnosis; langkah berikut: kejar divergensi pertama seperti biasa.
 */
