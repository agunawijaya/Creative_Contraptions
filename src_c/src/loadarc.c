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
int  *tab;               /* diindeks [j*3+2], bukan aritmetika alamat:
                            bentuk indeks membuat kompiler memakai ULANG
                            skala indeks alih-alih menghitung ulang */
int   n;
{
    int idx, id, j, ok;      /* idx@bp+4, id@bp+6, j@bp+8, ok@bp+0ah */
    char *p;                 /* p@bp+0ch */
    int m;                   /* m@bp+0eh = id & 0x7f (nilai ter-mask) */

    p = rec;
    if (fopen_(fh, 0, 0, 0) + 1 == 0) {
        err(0x1e52);
        return -1;
    }
    idx = 0;
    for (;;) {
        if (idx > 0x77)
            return m;
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
                m = id & 0x7f;
                if (m == tab[j * 3 + 2] || id == tab[j * 3 + 2]) {
                    ok = 1;
                    break;
                }
            }
        }
        else {
            ok = 1;
            m = id;
        }
        if (ok == 1) {
            rec = rec + 0xc;
            idx = idx + 1;
        }
    }
}

/* ⏳ BELUM COCOK — 228 byte vs 226. Bingkai & peta slot SUDAH BENAR.
 * Dua beda yang tersisa:
 *  1. tiga argumen 0 pada fopen_: asli me-nol-kan register ULANG tiap argumen
 *     (xor bx/push, xor bx/push, xor cx/push = 9 byte), kita memakai ulang satu
 *     register (xor bx sekali, push tiga kali = 5 byte). Di sini kita 4 byte
 *     lebih PENDEK.
 *  2. cabang "idx > 0x77" -> asli melompat ke keluar bersama (e9 9e 00),
 *     kita memancarkan epilog di tempat (83 c4 10 5d c3).
 * SUDAH DICOBA & GAGAL: menjadikan 0x77 sebagai kondisi while -> 231 byte.
 * Karena (1) membuat kita lebih pendek tapi total lebih panjang, ada ~6 byte
 * kelebihan lain yang tertutup oleh divergensi pertama.
 */
