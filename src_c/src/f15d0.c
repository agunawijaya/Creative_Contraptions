/* FUN_1000_15d0 @ 1000:15d0 (80 byte) — tulis label huruf A, B, C, ...
 *
 * Dipanggil f171f. Tabel `tab` berisi PASANGAN koordinat per label
 * (dua int per entri), dan labelnya sendiri dibangkitkan dari indeks:
 * 'A' + i. Hurufnya disimpan sebagai KATA ke sebuah int lalu ALAMATNYA
 * dioper ke text() -- byte tinggi yang nol sekaligus jadi penutup string.
 *
 *   text()=6453
 */

f15d0(cnt, tab)
int  cnt;
int *tab;
{
    /* Bingkai 0x0A: TANPA pengganjal. Enam byte di bawah [bp+6] adalah ruang
       TEMP yang dipesan kompiler sendiri -- menambah pengganjal di sini
       justru membuat bingkai 0x10. Kebalikan dari f171f, yang butuh
       pengganjal. Jadi cek dulu dengan mengompilasi tanpa pengganjal. */
    int  i;
    int  s;

    for (i = 0; i < cnt; i++) {
        s = i + 'A';
        text(&s, tab[i * 2 + 1], tab[i * 2], 1, 1, 3);
    }
}
