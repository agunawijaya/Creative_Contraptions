/* probeA.c — MENCARI apa yang menentukan WAKTU SIMPANAN ke memori.
 *
 * Gejala yang mau direproduksi (pickvar 0x43a5):
 *   ASLI  mov [bp+0ah],dx      <- simpan SEGERA
 *         mov dx,[bp+62h]      <- MUAT ULANG idx
 *         inc dx / cmp dx,[bp+60h]
 *   KITA  mov cx,[bp+62h] / inc cx / cmp cx,[bp+60h]
 *         mov [bp+0ah],dx      <- simpan DITUNDA
 *
 * Tiap fungsi mengubah SATU faktor. Yang dicari: fungsi mana yang memancarkan
 * simpanan `q` SEBELUM uji `idx + 1 < n`.
 */

extern int n;
extern int list[];

/* A1 — bentuk pickvar apa adanya: q dihitung, lalu sel, lalu uji. */
pa1(idx, out)
int idx;
int out[];
{
    int q, sel, k;
    k = list[idx];
    q = idx + 0x141;
    sel = -1;
    if (idx + 1 < n)
        sel = k;
    out[0] = q;
    out[1] = sel;
}

/* A2 — TANPA `sel` di antara: apakah jarak ke uji yang menentukan? */
pa2(idx, out)
int idx;
int out[];
{
    int q, sel, k;
    k = list[idx];
    q = idx + 0x141;
    if (idx + 1 < n)
        sel = k;
    else
        sel = -1;
    out[0] = q;
    out[1] = sel;
}

/* A3 — `q` dipakai LAGI sesudah uji: apakah pemakaian ulang menahannya? */
pa3(idx, out)
int idx;
int out[];
{
    int q, sel, k;
    k = list[idx];
    q = idx + 0x141;
    sel = -1;
    if (idx + 1 < n)
        sel = q;
    out[0] = q;
    out[1] = sel;
}

/* A4 — uji memakai `q`, bukan `idx`: apakah operan uji yang menentukan? */
pa4(idx, out)
int idx;
int out[];
{
    int q, sel, k;
    k = list[idx];
    q = idx + 0x141;
    sel = -1;
    if (q + 1 < n)
        sel = k;
    out[0] = q;
    out[1] = sel;
}

/* A5 — ada PANGGILAN di antara: batas blok paksa? */
pa5(idx, out)
int idx;
int out[];
{
    int q, sel, k;
    k = list[idx];
    q = idx + 0x141;
    sel = -1;
    if (idx + 1 < n)
        sel = k;
    out[0] = q;
    out[1] = sel;
    return q;
}
