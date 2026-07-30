/* FUN_1000_32bb @ 1000:32bb, 103 byte — menu PILIH LEVEL (Apprentice / Master Builder).
 * Dua baris (id 11,12), tabel @0x1b74 (7 entri). Bingkai "sub sp,8" = 3 lokal.
 */

struct mitem {
    char pad[22];
    int  y;
};

extern struct mitem mtablv[];   /* @0x1b74 */
extern int mode_;
extern int level_;
extern int ytop_;

lvlmenu()
{
    int y1, y2, h;

    y1 = ytop_;
    h = load(mode_, level_, 11, y1);
    y2 = y1 + h;
    load(mode_, level_, 12, y2);
    mtablv[0].y = y1;
    mtablv[1].y = y2;
    setsel(mtablv, 7);
    runmenu(mtablv, 7);
}
