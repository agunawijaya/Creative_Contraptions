/* Probe #10 - lanjutan probe9. Hipotesis: yang memelihara nilai global di AX
 * bukan `if (cond) goto L;` melainkan `if (!cond) { blok } goto L;` -- badan
 * blok adalah cabang TRUE sehingga tidak ada titik gabung yang membatalkan
 * tabel nilai kompiler, dan lompatan-salahnya DIRANTAI ke `jmp L` yang menyusul
 * (jadi tetap keluar sebagai "jl +3 / jmp jauh", bukan lompat pendek).
 */

extern int  g, k, bas;
extern char tab[];
extern char tab2[];

/* w1: if positif berblok, langsung diikuti goto */
w1()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g < k) {
        s = bas + tab[g] * 0xc0;
        t = tab2[g];
        gg(s, t);
    }
    goto top;
}

/* w2: dua uji bersarang, keduanya berblok */
w2()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g >= 0) {
        if (g < 0x32) {
            s = bas + tab[g] * 0xc0;
            t = tab2[g];
            gg(s, t);
        }
    }
    goto top;
}

/* w3: sama seperti w1 tapi ada pernyataan lain sebelum goto (pembanding:
   apakah perantaian lompatan bergantung pada goto yang langsung menyusul) */
w3()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g < k) {
        s = bas + tab[g] * 0xc0;
        t = tab2[g];
        gg(s, t);
    }
    hh();
    goto top;
}
