/* FUN_1000_498c @ 1000:498c (165 byte) — gambar pasangan objek "zany".
 *
 * Untuk tiap slot yang terisi (sel[i] >= 0), ambil daftar varian lewat nvar()
 * lalu serahkan ke drawpair(). Slot yang varian-nya nol dilaporkan lewat
 * printf(0x1e08, i) dan dilewati.
 *
 *   nvar()=4094  drawpair()=4a31  printf()=6a48
 *
 * ✅ COCOK BYTE-PER-BYTE (165/165). Tiga byte terakhir (+49, +52, +58) dulu
 * memakai BX di tempat aslinya memakai SI; yang menutupnya adalah PENJAGA
 * POSITIF berblok (`if (sel[i] >= 0) { ... }`) menggantikan dua `continue` --
 * lihat catatan di badan fungsi. Bentuk indeks (`tab[i*3+2]` vs
 * `*(tab+i*3+2)` vs `tab[3*i+2]`) TIDAK berpengaruh sama sekali.
 */

extern int fh;                  /* @0x72c */

f498c(ytop, cnt, tab, sel, sel2)
int  ytop, cnt;
int *tab, *sel, *sel2;
{
    int i;
    int buf[50];
    int n;

    for (i = 0; i < cnt; i++) {
        /* ⭐ PENJAGA POSITIF + `if/else`, BUKAN dua `continue`. Bentuk
           `continue` memberi tiga blok dasar terpisah; alokator lalu memilih
           BX untuk penunjuk `tab` sedangkan asli MEMAKAI ULANG SI (3 byte
           beda, ukuran instruksinya sama). Bentuk bersarang ini menyatukan
           blok dan memulihkan pilihan register. GLOBAL 162 -> 165/165. */
        if (sel[i] >= 0) {
            n = nvar(tab[i * 3 + 2], buf);
            if (n <= 0)
                printf(0x1e08, i);
            else
                drawpair(fh, ytop, tab[i * 3], tab[i * 3 + 1], buf, n,
                         sel[i], sel2[i]);
        }
    }
}

/* ⏳ BELUM COCOK — panjang SUDAH TEPAT 165, GLOBAL 162/165. Sisa TIGA byte,
 * semuanya di satu tempat: 0x49BC..0x49C5.
 *     kita: mov bx,[bp+7Ch] / add bx,ax / push [bx]
 *     asli: mov si,[bp+7Ch] / add si,ax / push [si]
 * Panjangnya IDENTIK; yang beda cuma REGISTER. Aslinya MEMAKAI ULANG SI yang
 * tadi dipakai untuk `sel[i]` (0x49A4), sedangkan kita mengambil BX yang baru
 * bebas sesudah `imul bx`.
 *
 * SUDAH DICOBA & GAGAL (diukur dengan metrik GLOBAL, 2026-07-31):
 *   - `nvar(tab[3 * i + 2], buf)`      -> 162/165, IDENTIK (tak berpengaruh)
 *   - `nvar(*(tab + i * 3 + 2), buf)`  -> 150/165, JAUH lebih buruk
 * Jadi bentuk ekspresi indeksnya BUKAN pengungkitnya. Yang tersisa untuk
 * dicoba: mengubah TEKANAN REGISTER se-blok lewat urutan/struktur pernyataan
 * lain di dalam gelung (aturan tahap 8/12), bukan lewat ekspresi ini.
 */
