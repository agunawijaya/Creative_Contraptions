/* Probe #16 — PENGHALANG UTAMA: apa yang menentukan pilihan register SI vs BX
 * untuk penunjuk sementara?
 *
 * Kasus nyata (f498c @0x498c, meleset 3 byte):
 *     asli : mov si,[bp+7Ch] / add si,ax / push [si]
 *     kita : mov bx,[bp+7Ch] / add bx,ax / push [bx]
 *
 * HIPOTESIS (dari pelajaran f278e): bentuk STRUCT memakai SI, bentuk
 * larik-int memakai BX. Di f498c tabelnya diakses bertiga-tiga
 * (imul 3 lalu shl 1 = *6, offset +4) -- itu persis `struct {int a,b,c;}`
 * dengan anggota KETIGA.
 *
 * v1: larik int, indeks hitung tangan   (bentuk kita sekarang)
 * v2: struct 3 int, anggota ketiga      (hipotesis)
 * v3: struct 3 int lewat penunjuk lokal
 */

struct three { int a, b, c; };

v1(tab, i, buf)
int *tab;
int  i;
int *buf;
{
    return nvar(tab[i * 3 + 2], buf);
}

v2(tab, i, buf)
struct three *tab;
int  i;
int *buf;
{
    return nvar(tab[i].c, buf);
}

v3(tab, i, buf)
struct three *tab;
int  i;
int *buf;
{
    struct three *p;

    p = tab + i;
    return nvar(p->c, buf);
}
