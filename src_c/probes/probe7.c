/* Probe #7 — bentuk mana yang membuat MS C 1.04 menghitung ALAMAT elemen
 * tabel SEKALI lalu memakainya ulang (uji + tulis), bukan dua kali?
 *
 * Tiga fungsi menggantung (pickloop, pickpart, getkey) semuanya mentok pada
 * satu slot temp berlebih, dan binernya memperlihatkan pola:
 *     mov si,[tab] ; add si,bx ; ... ; mov [bp],si   <- alamat disimpan ke TEMP
 *     mov [si],ax                                    <- dipakai ulang
 * Di sini tiap bentuk diukur lewat "sub sp" (rumus: 2*lokal + 2*temp).
 */

extern int g, h;
extern int ff();

/* w1: bentuk kita sekarang — uji lalu tulis, dua akses terpisah */
w1(t, i, v)
int *t;
int  i, v;
{
    if (t[i] != v) {
        g = 1;
        t[i] = v;
    }
}

/* w2: penunjuk lokal eksplisit (menambah satu LOKAL, bukan temp) */
w2(t, i, v)
int *t;
int  i, v;
{
    int *p;
    p = &t[i];
    if (*p != v) {
        g = 1;
        *p = v;
    }
}

/* w3: penugasan bersarang — nilai lama diambil sekaligus saat menulis */
w3(t, i, v)
int *t;
int  i, v;
{
    if (t[i] != v) {
        g = 1;
        h = (t[i] = v);
    }
}

/* w4: simpan nilai lama dulu ke variabel, baru bandingkan */
w4(t, i, v)
int *t;
int  i, v;
{
    int old;
    old = t[i];
    if (old != v) {
        g = 1;
        t[i] = v;
    }
}

/* w5: indeks ditampung variabel (mirip pola "offset disimpan ke temp") */
w5(t, i, v)
int *t;
int  i, v;
{
    int k;
    k = i;
    if (t[k] != v) {
        g = 1;
        t[k] = v;
    }
}
