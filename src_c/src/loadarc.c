/* FUN_1000_531d @ 1000:531d, 226 byte — muat DIREKTORI arsip (GRAPH/MECHS/MISC).
 *
 * Buka berkas, lalu baca record 12-byte satu per satu sampai id==0 atau 0x77 record.
 * Kalau `all` nol, hanya record yang id-nya cocok dengan tabel `tab` yang disimpan
 * (pembandingan dua arah: id penuh, atau id tanpa bit tinggi / 0x7f).
 *
 *   fopen_() = FUN_1000_6e8b ; fread_() = FUN_1000_6d31 ; err() = FUN_1000_6a48
 *   Balikan: -1 kalau gagal, jumlah record kalau berhasil.
 */

loadarc(fh, rec, all, tab, n)
int   fh;
char *rec;
int   all;
char *tab;
int   n;
{
    int idx, cnt, id, t, ok, unused;   /* slot ke-7: bingkai asli 10h */
    char *p;            /* SALINAN lokal dari parameter rec (slot bp+0ch) */

    p = rec;
    cnt = fopen_(fh, 0, 0, 0) + 1;   /* hasil TIDAK ditampung variabel antara:
                                        biner langsung "inc ax; jnz" */
    if (cnt == 0) {
        err(0x1e52);
        return -1;
    }
    idx = 0;
    for (;;) {
        if (idx > 0x77)
            return cnt;
        if (fread_(fh, p, 0xc) != 0xc) {
            err(0x1e63);
            return -1;
        }
        id = *p;
        if (id == 0)
            return idx;
        if (all == 0) {
            ok = 0;
            for (cnt = 0; cnt < n; cnt++) {
                t = *(int *)(tab + cnt * 6 + 4);
                if ((id & 0x7f) == t || id == t) {
                    ok = 1;
                    cnt = t;
                    break;
                }
            }
        }
        else {
            ok = 1;
            cnt = id;
        }
        if (ok) {
            p = p + 0xc;
            idx = idx + 1;
        }
    }
}

/* ⏳ BELUM COCOK — 232 byte vs 226 (6 KELEBIHAN).
 * Struktur awal SUDAH cocok sampai +3. Dua beda yang tersisa:
 *  1. bingkai kita 0eh vs asli 10h (satu slot kurang). Menambah lokal
 *     tak-terpakai TIDAK berpengaruh (dihapus kompiler); menambah lokal
 *     yang DIPAKAI (r = fopen_(...)) membuat panjang jadi 238.
 *  2. tiga argumen 0 pada fopen_: kita "xor bx,bx; push bx; push bx; push bx"
 *     (register dipakai ulang), asli "xor bx,bx/push bx" DUA kali lalu
 *     "xor cx,cx/push cx" -- di-nol-kan ULANG tiap argumen, register beda.
 *     Ini biasanya tanda tekanan register berbeda, yaitu akibat (1).
 * Sudah benar & jangan diubah: salinan lokal p dari parameter rec (slot bp+0ch),
 * dan hasil fopen_/fread_ TIDAK ditampung variabel antara.
 */
