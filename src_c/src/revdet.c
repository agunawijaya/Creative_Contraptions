/* FUN_1000_3020 @ 1000:3020, 155 byte — layar DETAIL mekanisme (mode Review).
 *
 * Menggambar judul+definisi dari tabel DGROUP ber-indeks mekanisme terpilih,
 * lalu sprite contoh, lalu menunggu tombol.
 *   sel @0x51c   = indeks mekanisme yang sedang dilihat
 *   ttl[] @0x14f6, def[] @0x1508 = tabel judul & definisi (indeks x2)
 *   spr[] @0x7fa = nomor sprite per mekanisme ; ybase @0x84a
 *   setsel()=3769, blit()=672f, show()=381a, kbflush()=36ef
 *   keyhit()=1791, getkey()=1814, tone2()=3734 (sudah direkonstruksi)
 *
 * Balikan: -1 = ESC, 0x20 = SPACE (jalankan demo), 0x0d = ENTER (lanjut).
 */

extern int  sel;            /* @0x51c */
extern int  ttl[];          /* @0x14f6 */
extern int  def[];          /* @0x1508 */
extern char spr[];          /* @0x7fa -- char = unsigned di MS C 1.04 */
extern int  ybase;          /* @0x84a */
extern char deftxt[];       /* @0x14d2 */

revdet()
{
    char c;

    setsel(ttl[sel], def[sel]);
    blit(ybase + spr[sel] * 0xc0, 0x30, 0x90, 0x18, 0x20);
    show(deftxt, 3);
    kbflush();
    do {
        while (keyhit() == 0)
            ;
        c = getkey();
        if (c == '\033')
            return -1;
        if (c == ' ') {
            tone2();
            return 0x20;
        }
    } while (c != '\r');
    tone2();
    return 0x0d;
}
