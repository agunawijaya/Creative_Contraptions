/* Probe #3 — mencari bentuk penulisan yang menghasilkan pola asli 3322:
 *   - "sub sp,0x10" (satu slot lokal LEBIH banyak dari yang kita duga)
 *   - "mov [bp+0xe], ax" = hasil panggilan disimpan ke slot sementara,
 *     ditunda sampai tepat sebelum panggilan berikutnya, lalu TIDAK pernah dibaca
 *
 * v1: y = y + f(...)            <- bentuk yang sudah dicoba, TIDAK menghasilkan slot itu
 * v2: h = f(...); y = y + h;    <- hasil ditampung variabel tersendiri
 * v3: y = f(...) + y;           <- urutan operand dibalik
 */

extern int mode_;
extern int level_;
extern int ytop_;

v1()
{
    int y1, y2, y3;
    y1 = ytop_;
    y2 = y1 + drawitem(mode_, level_, 13, y1);
    y3 = y2 + drawitem(mode_, level_, 14, y2);
    return y3;
}

v2()
{
    int y1, y2, y3, h;
    y1 = ytop_;
    h = drawitem(mode_, level_, 13, y1);
    y2 = y1 + h;
    h = drawitem(mode_, level_, 14, y2);
    y3 = y2 + h;
    return y3;
}

v3()
{
    int y1, y2, y3;
    y1 = ytop_;
    y2 = drawitem(mode_, level_, 13, y1) + y1;
    y3 = drawitem(mode_, level_, 14, y2) + y2;
    return y3;
}
