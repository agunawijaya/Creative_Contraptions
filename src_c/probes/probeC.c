/* probeC.c — kenapa MS C memakai ULANG SI (yang baru mati) vs mengambil BX?
 *
 * Situs acuan main_ 0x0c83 (dipetakan PASTI lewat penanda):
 *   0x0c78 mov si,ax          <- si = j*2, dipakai untuk [bp+si+6f22h]
 *   0x0c83 ASLI mov si,[recbase]   KITA mov bx,[recbase]
 * SI sudah MATI di 0x0c83 (nilainya sudah dipakai di 0x0c7a). Asli memakainya
 * ulang; kita ambil BX baru. Ukuran instruksi SAMA, jadi ini murni alokator.
 */

extern int recbase;
extern int sub;
extern int gj;

/* C1 — buf LOKAL (indeks [bp+si+K]), persis main_. */
pc1(cnt2)
int cnt2;
{
    int j;
    int buf[50];
    for (j = 0; j < cnt2; j++)
        if ((buf[j] * 0xc + (char *)recbase)[1] == sub)
            break;
    return j;
}

/* C2 — buf PARAMETER (penunjuk), bukan larik lokal. */
pc2(cnt2, buf)
int cnt2;
int *buf;
{
    int j;
    for (j = 0; j < cnt2; j++)
        if ((buf[j] * 0xc + (char *)recbase)[1] == sub)
            break;
    return j;
}

/* C3 — buf lokal, TAPI ada nilai lain yang HIDUP melintasi uji. */
pc3(cnt2)
int cnt2;
{
    int j, keep;
    int buf[50];
    keep = cnt2 + 1;
    for (j = 0; j < cnt2; j++)
        if ((buf[j] * 0xc + (char *)recbase)[1] == sub)
            break;
    return j + keep;
}

/* C4 — buf lokal, hasil indeks dipakai LAGI sesudah uji. */
pc4(cnt2)
int cnt2;
{
    int j;
    int buf[50];
    for (j = 0; j < cnt2; j++)
        if ((buf[j] * 0xc + (char *)recbase)[1] == sub)
            break;
    gj = buf[j];
    return j;
}

/* C5 — buf lokal, uji memakai dua field record (penunjuk dipakai DUA kali). */
pc5(cnt2)
int cnt2;
{
    int j;
    int buf[50];
    for (j = 0; j < cnt2; j++)
        if ((buf[j] * 0xc + (char *)recbase)[1] == sub &&
            (buf[j] * 0xc + (char *)recbase)[0] == sub)
            break;
    return j;
}
