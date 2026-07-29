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
char *tab;               /* offset BYTE: cur*6 dipakai tiga kali dalam satu
                            pemanggilan, biner menghitungnya SEKALI di register */
int   d, e;
int  *sel;
int   f;
int  *ans;
int  *tt;
int   g, h, k;
{
    int changed, v, r;   /* changed di slot PERTAMA (bp+0ah) sesuai biner */

    nmech = shuffle(seed, a, tab, n, f);
    changed = 0;
    for (;;) {
        kbflush();
        redraw();
        do {
            r = review(a, *(int *)(tab + cur * 6), *(int *)(tab + cur * 6 + 2),
                       d, e, sel[cur], cur * 6);
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

/* ⏳ BELUM COCOK — 329 byte vs 334, bingkai 12h vs 10h (satu slot temp lebih).
 * Perjalanan: 339 -> 329 (menyeberang) setelah tab dijadikan offset BYTE
 * sehingga "cur*6" dipakai bentuk yang sama di ketiga tempat.
 * SUDAH TERBUKTI:
 *   - jumlah lokal BENAR (3: changed@bp+0ah, lalu dua lagi di 0ch/0eh)
 *   - "changed" adalah lokal PERTAMA
 *   - tab diakses dgn offset byte (cur*6), bukan indeks int
 * SISA: satu slot temp. Biner menyimpan penunjuk hasil hitung ke temp lalu
 * MEMAKAINYA ULANG:
 *     2f04  mov si,[sel]; add si,bx ; ... ; mov [bp],si
 *     2f1a  mov [si],ax
 * sedangkan kita menghitung alamat sel[cur] dua kali (sekali untuk uji,
 * sekali untuk penugasan). Kandidat: tulis "if (sel[cur] != v) sel[cur] = v;"
 * dalam bentuk yang menghitung alamatnya sekali -- mis. penugasan bersarang
 * atau menyimpan ke variabel yang menggantikan salah satu lokal lain.
 */
