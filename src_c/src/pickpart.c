/* FUN_1000_131a @ 1000:131a, 387 byte — pilih part acak untuk tiap slot.
 *
 * Untuk tiap slot i: undi kandidat sampai dapat yang memenuhi syarat
 * (tinggi <= 100, dan jenisnya sesuai). Di level 2 dengan penanda khusus,
 * syaratnya dibalik; kalau 150 kali undian gagal, jatuh ke jalur umum
 * lewat `goto`. Slot terakhir pada sub-mode 1..6 dipaksa memakai mekanisme
 * yang sesuai sub-mode.
 *
 *   lvl2 @0x736, sub @0x3b2, mark[] @0x742
 *   nvar()=4094, rnd()=5a5b, place()=4e3e
 *
 * SLOT dari disassembly: bp+4, bp+6, bp+8, bp+0ah dipakai; bingkai 12
 * (2 slot temp di bp+0/bp+2).
 */

extern int lvl2;            /* @0x736 */
extern int sub;             /* @0x3b2 */
extern int mark[];          /* @0x742 */

pickpart(a, b, c, d, e, n, ans, flag, tq, tr, ts, tt)
int   a;
char *b;
int   c, d, e, n;
int  *ans;
int   flag;
int  *tq;
int  *tr;
int  *ts;
int  *tt;
{
    int i, j, cnt, tries;   /* i di slot PERTAMA (bp+4) sesuai biner */
    char *p;

    i = 0;
    /* "while (i < n)" dgn i di AX (mov ax,[i]; cmp ax,[n]), dan place()
       DI LUAR loop -- bukan "if (n <= i) { place(); return; }" di dalamnya. */
    while (i < n) {
        cnt = nvar(tq[i * 3 + 2], tr);
        if (lvl2 == 2 && mark[i] != 0) {
            tries = 0;
            do {
                j = rnd(cnt);
                tries = tries + 1;
                if (tries == 0x96)
                    goto any;
                p = b + tr[j] * 0xc;
            } while (p[1] > 100 || p[0] < 0x80);
        }
        else {
any:
            do {
                do {
                    j = rnd(cnt);
                    p = b + tr[j] * 0xc;
                } while (p[1] > 100);
            } while (p[0] > 0x7f);
        }
        if (sub > 0 && sub < 7 && i == n - 1) {
            j = 0;
            while (j < cnt && b[tr[j] * 0xc + 1] != sub)
                j = j + 1;
        }
        ts[i] = j;
        ans[i] = tr[j];
        tt[i] = b[tr[j] * 0xc];
        i = i + 1;
    }
    place(a, b, c, d, e, n, ans, flag);
}

/* ⏳ BELUM COCOK — 392 byte vs 387, bingkai 0eh vs 0ch.
 * SUDAH COCOK & JANGAN DIUBAH:
 *   - "while (i < n)" dgn place() DI LUAR loop; i dideklarasikan PERTAMA (bp+4)
 *   - tq/tr/ts/tt/ans sebagai int* diindeks [i] / [i*3+2]
 *   - `p` MEMANG variabel (menghapusnya -> 411 byte)
 *
 * TEMUAN KUNCI: biner hanya memakai EMPAT slot lokal (bp+4, 6, 8, 0ah);
 * kita memakai LIMA (i, j, cnt, tries, p). Jadi salah satu dari j/cnt/tries
 * BUKAN variabel di sumber aslinya -- kemungkinan `cnt` (hasil nvar) yang
 * dibaca ulang dari tempat lain, atau `tries` yang disusun beda.
 * SUDAH DICOBA & GAGAL:
 *   - menghapus p, hitung ulang b[tr[j]*0xc]        -> 411
 *   - memakai p di kondisi pencarian (operator koma) -> 395
 * Langkah berikut: telusuri bp+6/bp+8/bp+0ah di disassembly untuk memastikan
 * variabel mana yang menempatinya, seperti yang dilakukan pada autofill.
 */
