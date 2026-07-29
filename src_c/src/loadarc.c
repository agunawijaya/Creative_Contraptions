/* FUN_1000_531d @ 1000:531d, 226 byte — muat DIREKTORI arsip (GRAPH/MECHS/MISC).
 *
 * Buka berkas, lalu baca record 12-byte satu per satu sampai id==0 atau 0x77 record.
 * Kalau `all` nol, hanya record yang id-nya cocok dengan tabel `tab` yang disimpan
 * (pembandingan dua arah: id penuh, atau id tanpa bit tinggi / 0x7f).
 *
 *   fopen_() = FUN_1000_6e8b ; fread_() = FUN_1000_6d31 ; err() = FUN_1000_6a48
 *   Balikan: -1 kalau gagal, jumlah record kalau berhasil.
 *
 * TATA LETAK SLOT dari biner (bingkai 10h):
 *   bp+2 id, bp+4 idx, bp+6 ?, bp+8 j, bp+0ah ok, bp+0ch p, bp+0eh cnt
 *
 * TIGA HAL YANG SEMPAT SALAH — semuanya karena percaya bentuk Ghidra:
 *  1. Hasil fopen_ TIDAK pernah disimpan, hanya diuji ("inc ax; jne").
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
char *tab;
int   n;
{
    int id, idx, j, ok;      /* slot: id@bp+2, idx@bp+4, j@bp+8, ok@bp+0ah */
    char *p;                 /* p@bp+0ch */
    int cnt;                 /* cnt@bp+0eh */

    p = rec;
    if (fopen_(fh, 0, 0, 0) + 1 == 0) {
        err(0x1e52);
        return -1;
    }
    idx = 0;
    for (;;) {
        if (idx > 0x77)
            return cnt;
        if (fread_(fh, rec, 0xc) != 0xc) {
            err(0x1e63);
            return -1;
        }
        id = *rec;
        if (id == 0)
            return idx;
        if (all == 0) {
            ok = 0;
            for (j = 0; j < n; j++) {
                cnt = *(int *)(tab + j * 6 + 4);
                if ((id & 0x7f) == cnt || id == cnt) {
                    ok = 1;
                    break;
                }
            }
        }
        else {
            ok = 1;
            cnt = id;
        }
        if (ok == 1) {
            rec = rec + 0xc;
            idx = idx + 1;
        }
    }
}

/* ⏳ BELUM COCOK — 223 byte vs 226 (3 KURANG), bingkai 0eh vs 10h.
 * Struktur & tata letak slot lain sudah cocok. Kurang SATU slot: biner memakai
 * bp+6 untuk sesuatu yang belum teridentifikasi (variabel ke-7).
 * Menambahkan lokal yang tidak dipakai TIDAK menolong di sini -- kompiler
 * membuangnya (berbeda dgn probe5/a4 di mana lokal tak-terpakai dialokasikan;
 * agaknya hanya dialokasikan kalau ia satu-satunya lokal).
 * Beda kedua yang tersisa: tiga argumen 0 pada fopen_ -- biner me-nol-kan
 * register ULANG tiap argumen (xor bx/push, xor bx/push, xor cx/push),
 * punya kita memakai ulang satu register (xor bx sekali, push tiga kali).
 * Kedua hal ini kemungkinan satu sebab: tekanan register akibat slot ke-7.
 */
