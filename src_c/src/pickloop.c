/* FUN_1000_2e90 @ 1000:2e90, 334 byte — loop pemilihan part oleh pemain.
 *
 * Mengocok kandidat, lalu berulang: bersihkan keyboard, gambar, dan panggil
 * pemilih (3c4f) untuk slot yang sedang aktif. Kalau pilihan berubah, catat
 * jawaban + sprite-nya dan tandai `changed`. Slot aktif maju melingkar.
 * Keluar dengan ESC (-1) atau ENTER.
 *
 *   nmech @0x3ac, mechfh @0x72a, curz @0x2e6, base @0x73a, idtab[] @0x2ea
 *   mkpal()=3909, kbflush()=36ef (sudah direkonstruksi), redraw()=5936,
 *   review()=3c4f, clrbot()=5911 (sudah direkonstruksi), place()=4e3e
 *
 * SLOT dari disassembly: bp+0ah, 0ch, 0eh; bingkai 10h (5 slot temp di bp+0..8).
 */

extern int  nmech;          /* @0x3ac */
extern int  mechfh;           /* @0x72a */
extern int  curz;            /* @0x2e6 */
/* `base` adalah PENUNJUK ke tabel record 0xc byte, bukan int biasa. Buktinya
   "mov si,[73ah] / add si,ax / mov al,[si]" -- dua instruksi, langsung ke SI.
   Bentuk `*(char *)(base + k * 0xc)` memberi "mov cx,[73ah] / add cx,ax /
   mov si,cx" = 2 byte lebih. Lihat "Varian ke-4" di README. */
struct rec {
    char id;                /* +0  */
    char rest[11];          /* +1..0bh */
};                          /* = 0xc byte */

extern struct rec *base;    /* @0x73a */
extern char idtab[];        /* @0x2ea */

pickloop(a, n, tab, d, e, sel, f, ans, tt, g, h, k)
int   a;
char  n;
int  *tab;               /* indeks INT: biner memakai "imul 3" lalu geser (x2),
                            ciri tab[curz*3] -- BUKAN offset byte curz*6 */
int   d, e;
int  *sel;
int   f;
int  *ans;
int  *tt;
int   g, h, k;
{
    int changed, v, r;   /* changed di slot PERTAMA (bp+0ah) sesuai biner */

    nmech = mkpal(mechfh, a, tab, n, f);
    changed = 0;
    /* GOTO, bukan for(;;). Buktinya: setelah `switch` biner TIDAK memancarkan
       apa pun — tak ada `jmp` balik ke atas dan tak ada `break` keluar loop.
       Satu-satunya jalan mengulang adalah badan case 0x0d ("jmp 2eb6"), dan
       label akhir switch berimpit dengan blok pemeriksaan `changed`. Bentuk
       for(;;)+break memancarkan satu `jmp` ekstra di ujung switch (336 byte). */
top:
        kbflush();
        redraw();
        do {
            r = review(a, tab[curz * 3], tab[curz * 3 + 1], d, e, sel[curz]);
            if (r != 0xffff) {
                v = r & 0x7fff;
                if (sel[curz] != v) {
                    changed = 1;
                    sel[curz] = v;
                    ans[curz] = idtab[v];
                    tt[curz] = base[ans[curz]].id;
                }
                curz = curz + 1;
                if (curz >= n)   /* curz di KIRI: biner "cmp ax,bx" dgn ax=curz */
                    curz = 0;
            }
        } while (r >= 0);
        if (r == 0xffff)
            goto fin;       /* lompat ke `return r`, MELEWATI blok place() */
        /* SWITCH (badan case ditaruh dulu, rantai pembanding di bawah).
           Urutan badan di biner: jmp-keluar (0x20), lalu r=1 (0x0d), lalu r=-1 (0x1b).
           rantainya 0x1b / 0x0d / 0x20. Hanya ENTER yang mengulang. */
        switch (clrbot()) {
        case 0x20:
            goto done;
        case 0x0d:
            r = 1;
            goto top;
        case 0x1b:
            r = 0xffff;
            goto done;
        }
done:
    if (changed == 1 && r != 0xffff) {
        place(0x1a8, base, mechfh, h, k, n, ans, g, 0, 0);
        changed = 0;        /* biner benar-benar memancarkan "mov [bp+0ah],0" */
    }
fin:
    return r;
}

/* ✅ COCOK BYTE-PER-BYTE (334 byte). Empat hal yang menutupnya:
 *  1. `review()` cuma ENAM argumen -- `curz * 6` tidak ada (itu temp ekstra).
 *  2. `base` bertipe PENUNJUK struct: `base[ans[curz]].id`.
 *  3. `if (curz >= n)` -- curz di KIRI (biner "cmp ax,bx" dgn ax=curz).
 *  4. Loop luar pakai GOTO, bukan for(;;): setelah `switch` biner tak
 *     memancarkan apa pun, sedangkan for(;;)+break menambah satu `jmp`.
 */
