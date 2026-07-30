/* Probe #9 - bentuk apa yang membuat MS C 1.04 MEMAKAI ULANG nilai global yang
 * baru dibandingkan, alih-alih memuatnya ulang dari memori?
 *
 * Pola asli (review @0x3de7):
 *     a1 20 05      mov ax,[hi]
 *     3b 06 ac 03   cmp ax,[nmech]
 *     7c 03         jl  +3
 *     e9 6d fe      jmp top            <- jauh, jadi dua langkah
 *     8b f0         mov si,ax          <- NILAI DIPAKAI ULANG
 *     8a 9c fa 07   mov bl,[si+7fa]    <- AX sibuk, jadi lewat BL
 *
 * Rekonstruksi kami memancarkan sampai "e9 6d fe" persis sama, lalu:
 *     8b 36 20 05   mov si,[hi]        <- DIMUAT ULANG
 *     8a 84 fa 07   mov al,[si+7fa]    <- AX bebas
 *
 * Label `top` sengaja dijauhkan lebih dari 127 byte lewat blok pengisi supaya
 * lompatannya jadi bentuk dua langkah seperti di biner asli.
 *
 * CATATAN: MS C 1.04 TIDAK mendukung #define bersambung backslash
 * ("Error 1: invalid pre-processor command"), jadi pengisinya ditulis manual.
 */

extern int  g, k, bas;
extern char tab[];
extern char tab2[];

/* v1: bentuk rekonstruksi sekarang */
v1()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g >= k)
        goto top;
    s = bas + tab[g] * 0xc0;
    t = tab2[g];
    gg(s, t);
}

/* v2: `else` dengan SATU pernyataan (bukan blok) */
v2()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g >= k)
        goto top;
    else
        s = bas + tab[g] * 0xc0;
    t = tab2[g];
    gg(s, t);
}

/* v3: operan pembanding dibalik */
v3()
{
    int s, t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (k <= g)
        goto top;
    s = bas + tab[g] * 0xc0;
    t = tab2[g];
    gg(s, t);
}

/* v4: hasil tidak ditampung - langsung jadi argumen */
v4()
{
    int t;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g >= k)
        goto top;
    t = tab2[g];
    gg(bas + tab[g] * 0xc0, t);
}

/* v5: konsumen sesederhana mungkin */
v5()
{
    int s;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    if (g >= k)
        goto top;
    s = tab[g];
    gg(s, 0);
}

/* v6: global dibaca ke lokal lebih dulu */
v6()
{
    int s, t, m;
top:
    ff(1); ff(2); ff(3); ff(4);
    ff(5); ff(6); ff(7); ff(8);
    ff(9); ff(10); ff(11); ff(12);
    ff(13); ff(14); ff(15); ff(16);
    ff(17); ff(18); ff(19); ff(20);
    m = g;
    if (m >= k)
        goto top;
    s = bas + tab[m] * 0xc0;
    t = tab2[m];
    gg(s, t);
}
