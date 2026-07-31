/* FUN_1000_3f0f @ 1000:3f0f, 250 byte — gambar isi tiap slot contraption.
 *
 * Slot yang belum terisi (atau jawabannya negatif) digambar sebagai kotak
 * kosong; yang sudah terisi digambar sprite-nya. Sumber sprite berbeda
 * tergantung apakah ini pemuatan pertama (ans[0] == -1) atau bukan.
 *
 *   nmech @0x3ac, mechfh @0x72a, parttab[] @0x1ae
 *   mkpal()=3909, fillrect()=6869, blit()=672f
 *
 * SLOT dari disassembly: bp+6, 8, 0ah, 0ch, 0eh; bingkai 10h (3 slot temp).
 */

extern int nmech;           /* @0x3ac */
extern int mechfh;            /* @0x72a */
/* Tabel sprite: record 12 byte, hanya word pertama yang dipakai di sini.
   Ditulis sebagai array STRUCT supaya subscript memberi skala 12 SEKALIGUS
   bentuk displacement "mov ax,[si+1aeh]" -- bukan "add ax,OFFSET".

   ⚠ DULU BERNAMA `sprtab` DAN ITU SALAH. `sprtab` sudah dipakai drawpair.c
   untuk tabel di @0x0a. Satu NAMA untuk DUA alamat: LINK memadankan nama, jadi
   rujukan di sini ikut tertaut ke 0x0a dan meleset 0x1a4 byte. Terbukti dari
   EXE hasil link (0x0016) vs biner asli (0x01ae). objcode.py tidak bisa
   melihatnya karena slot relokasi diperlakukan wildcard, dan symcheck
   menganggapnya "akses ber-INDEKS" karena selisihnya < 0x400. */
struct sprent {
    int  w;
    char pad[10];
};
extern struct sprent parttab[];  /* @0x1ae */

drawslot(base, n, tab, sel, ans)
int  base, n;
int *tab;
int *sel;
int *ans;
{
    /* bp+0eh adalah BENDERA 0/1, bukan salinan *ans: biner membandingkan
       "cmp word [si],-1" langsung lalu menyetel bendera di kedua cabang. */
    int i, y, x, spr, flag;   /* i di slot PERTAMA (bp+6), flag TERAKHIR (bp+0eh) */

    if (*ans == -1) {
        flag = 0;
        nmech = mkpal(mechfh, base, tab, n);
    }
    else
        flag = 1;
    for (i = 0; i < n; i++) {
        y = tab[i * 3];
        x = tab[i * 3 + 1];
        /* Cabang GAMBAR-SPRITE ditulis DULU: di biner badannya menempel pada
           ujinya, sedangkan cabang kotak-kosong dilompati (eb 1f). */
        if (sel[i] >= 0 && ans[i] >= 0) {
            if (flag == 0)
                spr = base + sel[i] * 0xc0;
            else
                spr = parttab[ans[i]].w;
            blit(spr, y, x, 0x18, 0x20);
        }
        else
            fillrect(x + 1, y, x + 0x1e, y + 0x17, 3);
    }
}

