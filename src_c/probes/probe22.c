/* PROBE 22 — apakah `imul word ptr [mem]` datang dari SKALA STRUCT?
 * Probe 21 membuktikan `a * 3` biasa selalu memberi `mov bx,3 / imul bx`.
 * Hipotesis: konstanta di AX + operan MEMORI adalah bentuk yang dipakai
 * kompiler untuk skala INDEKS LARIK STRUCT (sizeof/2), bukan untuk perkalian
 * yang ditulis programmernya. */

struct trip { int y, x, id; };

p22a(a, t) int a; struct trip *t; { return t[a].id; }
p22b(a, t) int a; struct trip *t; { return t[a].y; }
p22c(a, t, u) int a; struct trip *t; int *u; { return u[a] != t[a].id; }
