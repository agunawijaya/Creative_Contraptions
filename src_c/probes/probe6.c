/* Probe #6 — cari bentuk badan loop moveball yang memakai HANYA SATU slot sementara.
 *
 * Dari probe5: bingkai = 2*(jumlah lokal) + 2*(temp maksimum yang dibutuhkan
 * ekspresi). moveball asli: 3 lokal + 1 temp = 8. Punya kita 3 lokal + 2 temp = 10.
 * Jadi salah satu pernyataan kita menuntut dua temp. Di sini tiap susunan diuji.
 */

extern int balltop, bally, ballx, ballrow;
extern int drawball();

/* m0: bentuk kita sekarang */
m0(x1, y1, x2, y2, n, d)
int x1, y1, x2, y2, n, d;
{
    int dx, i, dy;
    dx = x2 - x1;
    dy = y2 - y1;
    for (i = 1; i < n; i++) {
        balltop = 199 - (x1 + (dx * i) / n);
        bally = y1 + (dy * i) / n;
        ballx = x1 + (dx * i) / n;
        ballrow = bally / 4;
        drawball(d);
    }
}

/* m1: tanpa hoist, selisih dihitung di dalam */
m1(x1, y1, x2, y2, n, d)
int x1, y1, x2, y2, n, d;
{
    int dx, i, dy;
    dx = x2 - x1;
    dy = y2 - y1;
    for (i = 1; i < n; i++) {
        ballx = x1 + (dx * i) / n;
        balltop = 199 - ballx;
        bally = y1 + (dy * i) / n;
        ballrow = bally / 4;
        drawball(d);
    }
}

/* m2: pembagian dipisah dari penjumlahan */
m2(x1, y1, x2, y2, n, d)
int x1, y1, x2, y2, n, d;
{
    int dx, i, dy;
    dx = x2 - x1;
    dy = y2 - y1;
    for (i = 1; i < n; i++) {
        balltop = 199 - x1 - (dx * i) / n;
        bally = y1 + (dy * i) / n;
        ballx = x1 + (dx * i) / n;
        ballrow = bally / 4;
        drawball(d);
    }
}

/* m3: urutan pernyataan seperti Ghidra (balltop, bally, ballx, ballrow) tapi
       ballrow dari ekspresi penuh, bukan membaca global */
m3(x1, y1, x2, y2, n, d)
int x1, y1, x2, y2, n, d;
{
    int dx, i, dy;
    dx = x2 - x1;
    dy = y2 - y1;
    for (i = 1; i < n; i++) {
        balltop = 199 - (x1 + dx * i / n);
        bally = y1 + dy * i / n;
        ballx = x1 + dx * i / n;
        ballrow = (y1 + dy * i / n) / 4;
        drawball(d);
    }
}
