/* FUN_1000_341a @ 1000:341a, 178 byte — MENU UTAMA (pilih 4 mode permainan).
 *
 * Pola identik dengan goalmenu, hanya 4 baris (id 7..10) dan tabel @0x1d48 (11 entri).
 * Bingkai "sub sp,0ch" = 5 lokal: y1..y4 + h. Cocok dengan aturan
 * "hasil panggilan ditampung variabel tersendiri" (lihat ../README.md).
 */

struct mitem {
    char pad[22];
    int  y;
};

extern struct mitem mtabmn[];   /* @0x1d48 */
extern int mode_;               /* @0x846 */
extern int level_;              /* @0x740 */
extern int ytop_;               /* @0x84a */

mainmenu()
{
    int y1, y2, y3, y4, h;

    y1 = ytop_;
    h = load(mode_, level_, 7, y1);
    y2 = y1 + h;
    h = load(mode_, level_, 8, y2);
    y3 = y2 + h;
    h = load(mode_, level_, 9, y3);
    y4 = y3 + h;
    h = load(mode_, level_, 10, y4);
    mtabmn[0].y = y1;
    mtabmn[1].y = y2;
    mtabmn[2].y = y3;
    mtabmn[3].y = y4;
    setsel(mtabmn, 11);
    runmenu(mtabmn, 11);
}
