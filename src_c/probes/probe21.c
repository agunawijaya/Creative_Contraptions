/* PROBE 21 — kapan MS C 1.04 memancarkan `mov ax,K / imul word ptr [mem]`?
 * Probe 20 membuktikan bentuk indeks larik dan urutan operan TIDAK cukup.
 * Di sini perkaliannya diisolasi dari konteks indeks. */

extern int g;

p21a(a) int a; { return a * 3; }
p21b(a) int a; { return 3 * a; }
p21c()          { return g * 3; }
p21d(a) int a; { int t; t = a * 3; return t; }
p21e(a) int a; { return a * 3 + 2; }
