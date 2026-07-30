/* FUN_1000_10fd @ 1000:10fd, 259 byte — PILIH SLOT YANG DIKOSONGKAN untuk soal.
 *
 * Menandai maksimal `lim+1` slot dengan 1, tapi tidak boleh BERSEBELAHAN:
 * sebelum menandai slot c+1 diperiksa dulu tetangganya (c dan c+2) masih 0.
 * Setiap tabrakan menaikkan pencacah gagal `arr[0]`; kalau sudah 0x19 kali
 * gagal, pemilihan disudahi supaya tidak berputar selamanya di papan padat.
 *
 * Sesudah itu tanda-tanda tadi dibagi ke DUA daftar keluaran menurut isi
 * `tab[i]`: yang -1 masuk `outa`, sisanya `outb`.
 *
 * Kembar dengan setzany() (0x1200) — sumbernya memang diduplikasi, persis
 * seperti show()/setsel(). Bedanya cuma di pembuka dan satu syarat tambahan.
 *
 *   rnd() = FUN_1000_5a5b (assembly: LCG, ambil kata tinggi DX sesudah mul)
 *
 * ⭐ arr[0] BUKAN elemen ke-0 dari daftar slot melainkan PENCACAH GAGAL, dan
 * slot ke-i disimpan di arr[i+1]. Itu sebabnya biner mengakses
 * "[bp+si+0ah]" (arr[c+1]), "[bp+si+0ch]" (arr[c+2]) dan "[bp+si+8]" (arr[c])
 * dari SATU register si = 2*c: ketiganya elemen array yang sama, bergeser satu.
 *
 * PETA SLOT (bingkai 0x46): bp+0..4 = 3 TEMP, lalu
 *   bp+6=lim  8=arr[26] (8..3bh)  3ch=c  3eh=cnt  40h=i  42h=na  44h=nb
 * Argumen: bp+4ah=n, 4ch=tab, 4eh=easy, 50h=outa, 52h=outb.
 *
 * URUTAN PENUGASAN AWAL dibaca TERBALIK dari urutan store (lihat README):
 *   store "i, arr[0]"  -> sumber "arr[0] = 0;" lalu for(i = 0; ...)
 *   store "i, na, nb"  -> sumber "nb = 0; na = 0;" lalu for(i = 0; ...)
 */

setmark(n, tab, easy, outa, outb)
int  n;
int *tab;
int  easy;
int *outa;
int *outb;
{
    int lim;
    int arr[26];
    int c, cnt, i, na, nb;

    if (easy == 1)
        lim = rnd(1) + 1;
    else
        lim = rnd(1) + 3;
    arr[0] = 0;
    for (i = 0; i < n; i++)
        arr[i + 1] = 0;
    cnt = 0;
    while (cnt <= lim && arr[0] < 0x19 && n - 3 > 3) {
        c = rnd(n - 3) + 1;
        if (arr[c + 1] == 0) {
            if (arr[c + 2] == 0 && arr[c] == 0) {
                cnt++;
                arr[c + 1] = 1;
            }
            else
                arr[0]++;
        }
    }
    nb = 0;
    na = 0;
    for (i = 0; i < n; i++) {
        if (tab[i] == -1)
            outa[na++] = arr[i + 1];
        else
            outb[nb++] = arr[i + 1];
    }
    return cnt;
}
