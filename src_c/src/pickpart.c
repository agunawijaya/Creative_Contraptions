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
    /* Peta slot: i@bp+4, cnt@bp+6, j@bp+8, tries@bp+0ah; temp di bp+0/bp+2.
       TIDAK ADA lokal penunjuk record. Alamat "b + tr[j]*0xc" ditulis DUA KALI
       dalam satu ekspresi `||`, dan kompiler meng-CSE-nya sendiri: dihitung
       sekali ke SI, disimpan ke temp bp+0 (store yang bahkan tak pernah
       dibaca), lalu dipakai untuk [si+1] dan [si]. Memakai lokal `char *p`
       menambah slot ke-5 dan bingkai jadi 0eh.

       Yang di-CSE adalah PENUNJUKNYA, jadi ditulis "(b + tr[j]*0xc)[1]" —
       BUKAN "b[tr[j]*0xc + 1]". Bentuk kedua meng-CSE OFFSET-nya lalu
       "inc ax", sehingga akses jadi [si] tanpa displacement dan penunjuk
       dihitung ULANG untuk uji kedua (+12 byte). */
    int i, cnt, j, tries;

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
            } while ((b + tr[j] * 0xc)[1] > 100 || (b + tr[j] * 0xc)[0] < 0x80);
        }
        else {
any:
            /* SATU loop dgn `||`, bukan dua loop bersarang. Perhatikan uji
               kedua TERBALIK dibanding cabang di atas: di sini ">= 0x80"
               ("jge" balik ke undian), di atas "< 0x80" ("jl" balik). */
            do {
                j = rnd(cnt);
            } while ((b + tr[j] * 0xc)[1] > 100 || (b + tr[j] * 0xc)[0] >= 0x80);
        }
        if (sub >= 1 && sub <= 6 && i == n - 1) {
            j = 0;
            while (j < cnt && (b + tr[j] * 0xc)[1] != sub)
                j = j + 1;
        }
        ts[i] = j;
        ans[i] = tr[j];
        tt[i] = b[tr[j] * 0xc];
        i = i + 1;
    }
    place(a, b, c, d, e, n, ans, flag);
}


/* ✅ COCOK BYTE-PER-BYTE (387 byte). Tiga hal yang menutupnya:
 *  1. TIDAK ada lokal penunjuk record -- alamatnya CSE ke temp bp+0.
 *  2. `(b + tr[j]*0xc)[1]`, bukan `b[tr[j]*0xc + 1]` (CSE penunjuk vs offset).
 *  3. SATU do-while dengan `||`, bukan dua loop bersarang; dan uji kedua
 *     TERBALIK antara cabang level-2 (`< 0x80`) dan cabang umum (`>= 0x80`).
 */
