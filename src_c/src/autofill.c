/* FUN_1000_5954 @ 1000:5954, 263 byte — isi otomatis slot yang sudah gagal 2x.
 *
 * Untuk tiap slot mekanisme i: kalau pencacah gagalnya (@0x7be) sudah > 1,
 * jawaban benarnya dicari di tabel dan langsung dipasang (bantuan setelah
 * pemain salah dua kali). Kalau ada yang dipasang, layar digambar ulang.
 *
 *   nmech @0x3ac ; fail[] @0x7be (pencacah gagal per slot, 2 byte per slot)
 *   place() = FUN_1000_4e3e ; err() = FUN_1000_6a48
 *
 * Parameter (12) ditulis apa adanya karena semuanya diteruskan ke place().
 */

extern int nmech;           /* @0x3ac */
extern int fail[];          /* @0x7be */

autofill(a, b, c, d, e, n, ans, flag, tq, tr, ts, tt)
int a, b, c, d, e, n, ans, flag, tq, tr, ts, tt;
{
    int i, j, found, any;

    i = 0;
    any = 0;
    while (i < n) {          /* uji "i < n" dgn i di AX (mov ax,[i]; cmp ax,[n]),
                                bukan "n <= i" -- dan place() ada DI LUAR loop */
        if (fail[i] > 1) {
            *(int *)(tt + i * 2) = *(int *)(tq + i * 6 + 4);
            found = 0;
            for (j = 0; j < nmech; j++) {
                if (*(char *)(b + *(char *)(j + tr) * 0xc) == *(int *)(tt + i * 2)) {
                    *(int *)(ts + i * 2) = j;
                    *(int *)(ans + i * 2) = *(char *)(tr + j);
                    *(int *)(flag + i * 2) = -1;
                    any = 1;
                    found = 1;
                    break;
                }
            }
            if (found == 0)
                err(0x1ede, *(int *)(tt + i * 2), i * 2);
        }
        i = i + 1;
    }
    if (any)
        place(a, b, c, d, e, n, ans, flag);
}

/* ⏳ BELUM COCOK — 271 byte vs 263, bingkai 10h vs 14h (kurang 2 slot).
 * Sudah cocok: uji loop "i < n" dgn i di AX, place() di luar loop, dan
 * slot i@bp+8.
 * Sisa: `any` kita jatuh di bp+0eh, aslinya di bp+12h -> ada dua slot lagi
 * di antara. Slot yang benar-benar dipakai biner: bp+2, bp+8, bp+0ah,
 * bp+0eh, bp+12h (dari "grep bp +" pada disassembly). Jadi ada variabel di
 * bp+2 yang belum teridentifikasi, dan jarak found->any dua slot, bukan satu.
 * Langkah berikutnya: telusuri pemakaian bp+2 dan bp+0ah di disassembly untuk
 * menentukan variabel apa yang menempatinya, jangan menambah lokal asal-asalan.
 */
