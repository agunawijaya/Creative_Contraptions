/* FUN_1000_531d @ 1000:531d, 226 byte — muat DIREKTORI arsip (GRAPH/MECHS/MISC).
 *
 * Buka berkas, lalu baca record 12-byte satu per satu sampai id==0 atau 0x77 record.
 * Kalau `all` nol, hanya record yang id-nya cocok dengan tabel `tab` yang disimpan
 * (pembandingan dua arah: id penuh, atau id tanpa bit tinggi / 0x7f).
 *
 *   lseek() = FUN_1000_6e8b ; read() = FUN_1000_6d31 ; printf() = FUN_1000_6a48
 *   Balikan: -1 kalau gagal, jumlah record kalau berhasil.
 *
 * TATA LETAK SLOT dari biner (bingkai 10h):
 *   bp+2 id, bp+4 idx, bp+6 ?, bp+8 j, bp+0ah ok, bp+0ch p, bp+0eh cnt
 *
 * TIGA HAL YANG SEMPAT SALAH — semuanya karena percaya bentuk Ghidra:
 *  1. Hasil lseek TIDAK pernah disimpan, hanya diuji ("inc ax; jne").
 *     Ghidra menampilkannya sebagai "local_a = iVar3 + 1" padahal tak ada store.
 *  2. Loop dalam punya pencacah SENDIRI (bp+8), bukan memakai ulang cnt.
 *     Ghidra menggabungkan keduanya jadi satu local_a.
 *  3. Parameter `rec` dimajukan LANGSUNG (add [bp+16h],0ch), bukan lewat
 *     salinan lokal.
 */

loadarc(fh, rec, all, tab, n)
int   fh;
char *rec;
int   all;
int  *tab;               /* diindeks [j*3+2], bukan aritmetika alamat:
                            bentuk indeks membuat kompiler memakai ULANG
                            skala indeks alih-alih menghitung ulang */
int   n;
{
    int idx, id, j, ok;      /* idx@bp+4, id@bp+6, j@bp+8, ok@bp+0ah */
    char *p;                 /* p@bp+0ch */
    int m;                   /* m@bp+0eh = id & 0x7f (nilai ter-mask) */

    p = rec;
    if (lseek(fh, 0L, 0) + 1 == 0) {
        printf(0x1e52);
        return -1;
    }
    idx = 0;
    while (idx < 0x78) {
        if (read(fh, rec, 0xc) != 0xc) {
            printf(0x1e63);
            return -1;
        }
        id = *rec;
        if (id == 0)
            return idx;
        if (all == 0) {
            ok = 0;
            for (j = 0; j < n; j++) {
                m = id & 0x7f;
                if (m == tab[j * 3 + 2] || id == tab[j * 3 + 2]) {
                    ok = 1;
                    break;
                }
            }
        }
        else
            ok = 1;
        if (ok == 1) {
            rec = rec + 0xc;
            idx = idx + 1;
        }
    }
}

/* ✅ COCOK BYTE-PER-BYTE (226 byte). Tiga hal yang menutupnya:
 *  1. `lseek(fh, 0L, 0)` — TIGA argumen, bukan empat. Offsetnya `long`, jadi
 *     didorong sebagai DUA kata yang masing-masing di-nol-kan sendiri:
 *     "xor bx,bx / push bx / xor bx,bx / push bx / xor cx,cx / push cx".
 *     Bentuk `lseek(fh, 0, 0, 0)` memakai ulang satu register (5 byte, kurang 4).
 *  2. `while (idx < 0x78)`, BUKAN `for(;;)` + `if (idx > 0x77) return m;`.
 *     Aslinya melompat jauh ke SATU epilog di ujung tanpa memuat nilai balik —
 *     artinya loop biasa yang jatuh-tembus, bukan `return` dengan nilai.
 *  3. Cabang `all != 0` hanya `ok = 1;` — TIDAK ada `m = id;`.
 */
