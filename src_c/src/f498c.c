/* FUN_1000_498c @ 1000:498c (165 byte) — gambar pasangan objek "zany".
 *
 * Untuk tiap slot yang terisi (sel[i] >= 0), ambil daftar varian lewat nvar()
 * lalu serahkan ke drawpair(). Slot yang varian-nya nol dilaporkan lewat
 * printf(0x1e08, i) dan dilewati.
 *
 *   nvar()=4094  drawpair()=4a31  printf()=6a48
 *
 * ⏳ NEAR-MISS: 162 dari 165 byte cocok, bingkai 0x74 TEPAT, panjang TEPAT.
 * Tiga byte yang beda (+49, +52, +58) semuanya pilihan REGISTER: aslinya
 * `mov si,[bp+7Ch] / add si,ax / push [si]`, kita memakai BX. Sekelas dengan
 * near-miss `place` (SI vs DI) yang sudah lama terbuka.
 * SUDAH DICOBA & GAGAL: tab[i*3+2] | *(tab+i*3+2) | tab[2+i*3] | tab[3*i+2]
 * -- bentuk indeks TIDAK mempengaruhi pilihan register (yang bentuk penunjuk
 * malah merusak 108 byte).
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
        if (sel[i] < 0)
            continue;
        n = nvar(tab[i * 3 + 2], buf);
        if (n <= 0) {
            printf(0x1e08, i);
            continue;
        }
        drawpair(fh, ytop, tab[i * 3], tab[i * 3 + 1], buf, n,
                 sel[i], sel2[i]);
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
