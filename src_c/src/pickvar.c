/* FUN_1000_42ca @ 1000:42ca, 1.730 byte — PILIH VARIAN part secara interaktif.
 *
 * ⚠ DRAF — belum cocok. Lihat catatan di ujung berkas.
 *
 * ⚠⚠ JANGAN MENULIS FUNGSI INI DARI PSEUDO-C GHIDRA. Ghidra melaporkan 9 blok
 * tak-terjangkau DAN memancarkan `if (param_7 + 0x141 != param_7)` — syarat
 * yang SELALU BENAR, jadi mustahil ada di sumber. Itu pola yang sama dengan
 * bug `load` (0x53ff+134): kompiler memancarkan instruksi yang MERUSAK FLAG
 * sehingga lompatan sesudahnya selalu diambil. Kerjakan dari disassembly, dan
 * curigai ada blok yang di biner asli memang TIDAK PERNAH TERCAPAI — jangan
 * "diperbaiki" supaya masuk akal.
 *
 *   rnd()=5a5b  load()=53ff  blit()=672f  printf()=6a48 (MC.LIB)
 *   recbase @0x73c ; lvl @0x734 ; tw @0x7f0
 *
 * PETA SLOT (bingkai 0x52 = 82): 36 slot terpakai, yang TIDAK dipakai adalah
 *   bp+00, 08, 14, 22, 4e.
 * Yang sudah dikenali dari kepala fungsi:
 *   bp+44h = rb (salinan recbase)   48h = cnt (pencacah percobaan acak)
 *   4ch = rp (penunjuk record)
 * Argumen: bp+56h=fh, 58h=buf, 5ah=x, 5ch=y, 5eh=list, 60h=n, 62h=idx, 64h=flag
 */

struct rec {
    char id;                /* +0 */
    char row;               /* +1 */
    char w;                 /* +2 */
    char h;                 /* +3 */
    char dx;                /* +4 BERTANDA */
    char dy;                /* +5 BERTANDA */
    char rest[6];
};                          /* = 0xc byte */

extern struct rec *recbase; /* @0x73c */
extern int lvl;             /* @0x734 */
extern int tw;              /* @0x7f0 */

pickvar(fh, buf, x, y, list, n, idx, flag)
int  fh, buf, x, y;
int *list;
int  n, idx, flag;
{
    /* TATA LETAK BINGKAI DIUKUR, bukan ditebak. Temp menempati bp+00..07
       (empat slot; dipakai untuk row-100 dsb.), lokal mulai bp+08.
       Pengganjal memakai `char[]` karena array SELALU dialokasikan sedangkan
       `int` tak terpakai kadang dibuang kompiler. */
    /* PENGGANJAL TEMP sudah HABIS: temp nyata kini persis 4 slot
       (bp+00..07). Kalau menambah kode lagi membuat sub sp > 52h,
       berarti ada ekspresi yang menuntut temp berlebih -- perbaiki
       ekspresinya, jangan tambah pengganjal. */
    /* bp+08h TIDAK dipakai di biner, tapi itu TEMP KELIMA (temp menempati
       bp+00..09), bukan lokal. Memberinya pengganjal menggeser SEMUA slot
       2 byte dan membuat bingkai 54h. */
    int  q;             /* 0Ah  = idx + 141h */
    char f1[10];        /* 0Ch..15h */
    int  k2;            /* 16h  salinan kedua list[idx] */
    char f2[2];         /* 18h */
    int  sel;           /* 1Ah  nilai balik, mulai -1 */
    char f3[2];         /* 1Ch */
    int  k;             /* 1Eh  = list[idx] */
    char f4a[8];        /* 20h..27h */
    int  dx2;           /* 28h  geser x record ke-2, BERTANDA */
    int  dy2;           /* 2Ah  geser y record ke-2, BERTANDA */
    char f4b[24];       /* 2Ch..43h */
    int  rb;            /* 44h  salinan recbase */
    int  rp2;           /* 46h  penunjuk record ke-2 (dari salinan rb) */
    int  cnt;           /* 48h  pencacah percobaan acak */
    char f6[2];         /* 4Ah */
    struct rec *rp;     /* 4Ch */
    char f7[4];         /* 4Eh..51h */

    rb = (int)recbase;
    if (lvl == 2)
        tw = 9;
    else
        tw = 0x12;
    if (n <= 0)
        return 0;
    if (idx < 0) {
        /* SATU do-while dengan `||`, bukan dua loop bersarang: kedua syarat
           melompat ke ATAS loop yang sama (jg 430d / jl 430d). Bentuk
           bersarang akan memberi lompatan ke label yang berbeda. */
        if (flag != 0) {
            cnt = 0;
            do {
                idx = rnd(n);
                cnt++;
                rp = recbase + list[idx];
            } while (rp->row > 100 || (rp->id < 0x80 && cnt < 0x73));
        }
        else {
            do {
                idx = rnd(n);
                rp = recbase + list[idx];
            } while (rp->row > 100 || rp->id >= 0x80);
        }
    }
    /* Slot bp+0Ah inilah yang Ghidra rusak jadi
       `if (param_7 + 0x141 != param_7)` -- sebenarnya PENUGASAN biasa. */
    k = list[idx];
    k2 = k;
    q = idx + 0x141;
    sel = -1;
    if (idx + 1 < n) {
        /* Pola "row berselisih 100 = bagian lanjutan", sama seperti drawpair
           dan nvar. Perkaliannya BEDA bentuk di dua sisi -- ikuti biner:
           `0xc * list[idx+1]` (konstanta kiri, operan memori) vs `k * 0xc`. */
        if (((char *)recbase)[0xc * list[idx + 1] + 1] - 100 ==
                ((char *)recbase)[k * 0xc + 1]) {
            /* Pola drawpair: char di MS C 1.04 itu unsigned, jadi tandanya
               dipulihkan lewat TERNARY dengan nilai-apa-adanya di posisi
               FALSE (cabang yang MEMUAT ULANG dari slot). */
            sel = list[idx + 1];
            rp2 = rb + sel * 0xc;
            dx2 = ((char *)rp2)[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = ((char *)rp2)[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            load(fh, recbase, sel, buf);
            blit(buf, x + dx2, y + dy2, ((char *)rp2)[2], ((char *)rp2)[3]);
        }
    }
    return idx;
}

/* ⏳ DRAF — 231 dari 1.730 byte cocok; blok load/blit SUDAH ditulis (436 byte
 * draf) dan bagian-bagiannya terbukti benar.
 *
 * ⭐ TEMUAN PENTING giliran ini: bp+08h itu TEMP KELIMA, bukan lokal.
 * Temp menempati bp+00..09 (5 slot), lokal mulai bp+0Ah. Memberi pengganjal
 * di 08h menggeser SELURUH slot 2 byte dan membuat bingkai 54h. Daftar "slot
 * tidak terpakai" (00 08 14 22 4E) MENYESATKAN: 00 dan 08 itu temp yang
 * kebetulan tak terpakai, bukan lokal kosong.
 *
 * TERVERIFIKASI byte-per-byte (0x42ca..0x43b0) + bagian yang cocok sesudahnya:
 *   - bingkai 52h, seluruh peta slot, kedua loop rnd
 *   - bentuk lompatan `jl +3 / jmp jauh` SEKARANG COCOK (dulu `jge` pendek) --
 *     ini membenarkan keputusan giliran lalu: menulis badan lebih dulu memang
 *     memperbaiki bentuk lompatan dengan sendirinya
 *   - perkalian `mov ax,0Ch / imul word ptr [bx]` COCOK (bentuk char-pointer)
 *   - blok load/blit dengan pemulihan tanda gaya drawpair sudah ditulis
 *
 * SUDAH DICOBA & GAGAL (urutan k/k2, DIULANG sesudah badan membesar):
 *   - `q; sel; k; k2`               -> +193
 *   - `k2 = list[idx]; k = k2;`     -> +220 (dicoba DUA KALI, sebelum dan
 *                                      sesudah badan membesar -- tetap +220)
 *   - `k2 = list[idx]; k = list[idx];` -> +220
 *   - `k = list[idx]; k2 = k;`      -> +231  <- terbaik
 *
 * DIVERGENSI SEKARANG di +231, tinggal DUA sebab:
 *   1. urutan flush: kita [16h] lalu [1Eh]; asli [1Eh] lalu [16h].
 *      Empat urutan sumber sudah diukur, tak ada yang membalikkannya.
 *   2. asli menyimpan temp `[bp+2] = si` (penunjuk &list[idx]) sesudah kedua
 *      store itu; kita malah MEMUAT ULANG global (`mov dx,[73Ch]`) di blok
 *      berikutnya. Artinya asli memakai ulang penunjuk yang sudah dihitung,
 *      kita menghitung ulang dari `recbase`. Ini kemungkinan besar SEBAB
 *      dari (1) juga -- kejar ini dulu, bukan urutan store-nya.
 *
 * BELUM ditulis: 0x4474 ke atas (~1.400 byte).
 */
