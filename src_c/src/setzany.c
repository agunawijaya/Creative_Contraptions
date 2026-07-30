/* FUN_1000_1200 @ 1000:1200, 282 byte — versi ZANY OBJECTS dari setmark().
 *
 * KEMBAR dengan setmark() (0x10fd): 94 byte ekornya identik byte-per-byte.
 * Sumbernya memang diduplikasi di 1985, bukan memanggil satu sama lain —
 * persis seperti pasangan show()/setsel(). Tiga bedanya:
 *
 *   1. pembuka: mengocok dua nomor objek zany (zsel[0], zsel[1]) lebih dulu,
 *      dan batas `lim` selalu rnd(1)+3 (tidak ada cabang mudah/sulit);
 *   2. syarat tambahan `tab[c] == 1` — slot hanya boleh dikosongkan kalau
 *      isinya memang objek zany;
 *   3. sisanya sama.
 *
 *   rnd() = FUN_1000_5a5b ; zsel[] @0x836 (dipakai juga nvar.c)
 *
 * PETA SLOT (bingkai 0x46) sama dengan setmark(): bp+0..4 = 3 TEMP, lalu
 *   bp+6=lim  8=arr[26]  3ch=c  3eh=cnt  40h=i  42h=na  44h=nb
 * Argumen: bp+4ah=n, 4ch=tab, 4eh=TIDAK DIPAKAI, 50h=outa, 52h=outb.
 *
 * Biner MEMAKAI ULANG 2*c yang sudah di AX untuk `tab[c]` ("add si,ax"),
 * lalu MENGHITUNG ULANG-nya untuk arr[c+2] — jadi jangan menampung indeksnya
 * di variabel; tulis apa adanya.
 */

extern int zsel[];          /* @0x836 */

setzany(n, tab, unused, outa, outb)
int  n;
int *tab;
int  unused;
int *outa;
int *outb;
{
    int lim;
    int arr[26];
    int c, cnt, i, na, nb;

    zsel[0] = rnd(0xf);
    zsel[1] = rnd(0xf);
    lim = rnd(1) + 3;
    arr[0] = 0;
    for (i = 0; i < n; i++)
        arr[i + 1] = 0;
    cnt = 0;
    while (cnt <= lim && arr[0] < 0x19 && n - 3 > 3) {
        c = rnd(n - 3) + 1;
        if (arr[c + 1] == 0 && tab[c] == 1) {
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
