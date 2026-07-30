/* FUN_1000_5954 @ 1000:5954, 263 byte — isi otomatis slot yang sudah gagal 2x.
 *
 * Untuk tiap slot mekanisme i: kalau pencacah gagalnya (@0x7be) sudah > 1,
 * jawaban benarnya dicari di tabel dan langsung dipasang (bantuan setelah
 * pemain salah dua kali). Kalau ada yang dipasang, layar digambar ulang.
 *
 *   nmech @0x3ac ; fail[] @0x7be (pencacah gagal per slot, 2 byte per slot)
 *   place() = FUN_1000_4e3e ; printf() = FUN_1000_6a48
 *
 * Parameter (12) ditulis apa adanya karena semuanya diteruskan ke place().
 */

extern int nmech;           /* @0x3ac */
extern int fail[];          /* @0x7be -- array int biasa: fail[i] -> [si+7beh] */          /* @0x7be */

autofill(a, b, c, d, e, n, ans, flag, tq, tr, ts, tt)
int   a;
char *b;                 /* diindeks langsung b[...]: bentuk *(char *)(b + ...)
                            memaksa perhitungan lewat CX lalu disalin ke SI */
int   c, d, e, n;
int  *ans;               /* diindeks [i] -> kompiler memakai ULANG indeks i*2
                            yang sudah dihitung untuk fail[i]; bentuk
                            *(int *)(ans + i*2) memaksanya menghitung ulang */
int  *flag;
int  *tq;                /* diindeks [i*3+2]: biner menghitung i*3 lalu
                            digeser (x2) lalu +4 -- itu ciri indeks INT, bukan
                            aritmetika byte i*6+4 */
char *tr;                /* array byte */
int  *ts;
int  *tt;
{
    /* Peta slot dari disassembly (bingkai 14h): i@8, j@0ah, found@0eh, any@12h.
       bp+0 dan bp+2 adalah TEMP kompiler (salah satunya menahan i*2 yang
       dipakai ulang sebagai indeks beberapa tabel) -- bukan variabel sumber. */
    int i, j, pad3, found, pad4, any;

    /* Urutan sengaja TERBALIK: kompiler memancarkan store dalam urutan
       kebalikan sumber, jadi tulis any dulu untuk mendapat store i lalu any. */
    any = 0;
    i = 0;
    while (i < n) {          /* uji "i < n" dgn i di AX (mov ax,[i]; cmp ax,[n]),
                                bukan "n <= i" -- dan place() ada DI LUAR loop */
        if (fail[i] >= 2) {      /* uji ">= 2" (cmp ..,2), bukan "> 1" */
            tt[i] = tq[i * 3 + 2];
            found = 0;
            for (j = 0; j < nmech; j++) {
                if (b[tr[j] * 0xc] == tt[i]) {
                    ts[i] = j;
                    ans[i] = tr[j];
                    flag[i] = -1;
                    found = 1;   /* urutan sumber terbalik dari urutan store */
                    any = 1;
                    break;
                }
            }
            if (found == 0)
                printf(0x1ede, tt[i]);   /* DUA argumen -- Ghidra menampilkan tiga */
        }
        i = i + 1;
    }
    if (any == 1)      /* cmp any,1 / jne -- bukan uji nol */
        place(a, b, c, d, e, n, ans, flag);
}

/* ✅ COCOK BYTE-PER-BYTE (263 byte).
 *
 * Catatan di bawah ini adalah RIWAYAT dari masa fungsi ini masih near-miss.
 * Bagian "sudah terbukti" dan "sudah dicoba & gagal" tetap berlaku dan
 * berguna; bagian "sisa" / "langkah berikut" SUDAH SELESAI — abaikan.
 * ---------------------------------------------------------------------
 * (riwayat) BELUM COCOK — 271 byte vs 263, bingkai 10h vs 14h (kurang 2 slot).
 * Sudah cocok: uji loop "i < n" dgn i di AX, place() di luar loop, dan
 * slot i@bp+8.
 * Sisa: `any` kita jatuh di bp+0eh, aslinya di bp+12h -> ada dua slot lagi
 * di antara. Slot yang benar-benar dipakai biner: bp+2, bp+8, bp+0ah,
 * bp+0eh, bp+12h (dari "grep bp +" pada disassembly). Jadi ada variabel di
 * bp+2 yang belum teridentifikasi, dan jarak found->any dua slot, bukan satu.
 * Langkah berikutnya: telusuri pemakaian bp+2 dan bp+0ah di disassembly untuk
 * menentukan variabel apa yang menempatinya, jangan menambah lokal asal-asalan.
 */

/* (riwayat, sudah selesai) 271 byte vs 263. Yang SUDAH terbukti benar:
 *   - bentuk loop "while (i < n)" dgn place() DI LUAR loop
 *   - slot i@bp+8, j@bp+0ah, found@bp+0eh, any@bp+12h (bingkai 14h)
 *   - fail[] adalah array INT biasa: "fail[i]" -> cmp [si+7beh],2
 *   - ujinya ">= 2" (cmp ..,2), bukan "> 1"
 *   - bp+0/bp+2 = TEMP kompiler (salah satunya menahan i*2 yang dipakai ulang),
 *     BUKAN variabel sumber -- menuliskannya sbg variabel k2 menghasilkan
 *     "add ax,imm" alih-alih bentuk displacement "[si+7beh]"
 * Sisa: 8 byte kelebihan, dan urutan store awal (kita any lalu i; asli i lalu
 * any) belum stabil. Langkah berikut: kejar divergensi pertama lagi setelah
 * urutan store awal dibetulkan.
 */
