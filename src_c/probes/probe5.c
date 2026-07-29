/* Probe #5 — TURUNKAN ATURAN UKURAN BINGKAI MS C 1.04.
 *
 * Tiga fungsi menggantung (drawball, moveball, loadarc) semuanya mentok pada
 * hal yang sama: bingkai meleset satu slot. Alih-alih menebak dari fungsi
 * sungguhan yang banyak variabel bebasnya, di sini tiap faktor divariasikan
 * SATU per satu lalu "sub sp" yang dihasilkan diukur.
 *
 * Faktor yang diuji: jumlah lokal, lokal terpakai vs tidak, kedalaman
 * ekspresi bersarang, jumlah argumen panggilan, penampungan hasil panggilan.
 */

extern int g, h, k;
extern int ff();

/* --- kelompok A: jumlah lokal --- */
a0() { g = 1; }
a1() { int x;          x = 1; g = x; }
a2() { int x, y;       x = 1; y = 2; g = x + y; }
a3() { int x, y, z;    x = 1; y = 2; z = 3; g = x + y + z; }
a4() { int x;          g = 1; }                  /* lokal TIDAK dipakai */
a5() { int x, y;       g = 1; }                  /* dua lokal tak dipakai */

/* --- kelompok B: kedalaman ekspresi --- */
b0() { g = h + k; }
b1() { g = h + k * 2; }
b2() { g = (h + k) * (h - k); }
b3() { g = 199 - (h + (k * g) / 3); }            /* pola moveball */

/* --- kelompok C: panggilan --- */
c0() { ff(); }
c1() { ff(1); }
c3() { ff(1, 2, 3); }
c3z() { ff(0, 0, 0); }                            /* pola loadarc */
c4() { ff(1, 2, 3, 4); }

/* --- kelompok D: hasil panggilan --- */
d0() { g = ff(); }
d1() { int x; x = ff(); g = x; }
d2() { g = ff() + 1; }
d3() { if (ff() + 1 == 0) g = 1; }                /* pola loadarc */

/* --- kelompok E: campuran --- */
e0() { int x; x = ff(0, 0, 0); g = x; }
e1() { int x, y; x = ff(0, 0, 0); y = h + k; g = x + y; }
