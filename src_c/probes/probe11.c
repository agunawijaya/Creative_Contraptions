/* Probe #11 — apa yang memaksa MS C 1.04 MENG-COMMIT store yang tertunda?
 *
 * Pola asli (loadcon @0x5111):
 *     add ax,[first]
 *     mov [pick],ax          <- store DI-COMMIT segera
 *     mov ax,[lastgoal]      <- bentuk akumulator a1, 3 byte (AX bebas)
 *     cmp ax,[sub]
 *
 * Rekonstruksi kami:
 *     add ax,[first]
 *     mov bx,[lastgoal]      <- 8b 1e, 4 byte (AX masih menahan nilai pending)
 *     cmp bx,[sub]
 *     mov [pick],ax          <- store DITUNDA sampai sini
 *
 * Panjang fungsi sudah tepat 739; ini satu-satunya sebab sisa 321 byte beda,
 * yang semuanya cuma pergeseran register hasil pilihan ini.
 */

extern int gA, gB, cnt, lastvar;

/* w1: bentuk rekonstruksi sekarang — hasil panggilan + lokal, lalu uji global */
w1(first)
int first;
{
    int pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* w2: operan penjumlahan dibalik */
w2(first)
int first;
{
    int pick;

    do {
        pick = first + rnd(cnt);
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* w3: `first` dibaca ke lokal lain lebih dulu */
w3(first)
int first;
{
    int pick, base;

    base = first;
    do {
        pick = rnd(cnt) + base;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* w4: hasil panggilan ditampung sendiri (aturan 8), lalu dijumlahkan */
w4(first)
int first;
{
    int pick, r;

    do {
        r = rnd(cnt);
        pick = r + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* w5: syarat pertama memakai LOKAL, bukan global — apakah pemilihan register
   bergantung pada jenis operan uji berikutnya? */
w5(first)
int first;
{
    int pick;

    do {
        pick = rnd(cnt) + first;
    } while (first == gB && cnt >= 2 && pick == lastvar);
    return pick;
}

/* w6: `pick` dipakai SESUDAH loop lewat pemanggilan, bukan sekadar return */
w6(first)
int first;
{
    int pick;

    do {
        pick = rnd(cnt) + first;
    } while (gA == gB && cnt >= 2 && pick == lastvar);
    ff(pick);
    return pick;
}
