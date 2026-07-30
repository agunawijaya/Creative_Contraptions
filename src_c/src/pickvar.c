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
        /* DUA BENTUK BERBEDA dengan sengaja: sisi kiri char-pointer
           (`mov ax,0Ch / imul word ptr [bx]`), sisi kanan struct
           (`mov ax,cx / mov dx,0Ch / imul dx`). Campuran ini juga yang
           MEMUTUS CSE atas `recbase` -- biner memuatnya DUA KALI
           ([73Ch] ke DI lalu ke SI), bukan sekali lalu dipakai ulang. */
        if ((0xc * list[idx + 1] + (char *)recbase)[1] - 100 ==
                recbase[k].row) {
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

/* ⏳ DRAF — 231 dari 1.730 byte cocok; draf 433 byte dan blok pembanding
 * kini nyaris identik (sisa 2 byte per akses).
 *
 * ⭐ TEMUAN: bp+08h itu TEMP KELIMA, bukan lokal. Temp menempati bp+00..09,
 * lokal mulai bp+0Ah. Daftar "slot tidak terpakai" (00 08 14 22 4E)
 * MENYESATKAN -- 00 dan 08 itu temp yang kebetulan tak dipakai.
 *
 * TIGA bentuk penulisan yang sudah TERBUKTI benar untuk blok pembanding
 * `recbase[list[idx+1]].row - 100 == recbase[k].row` (diukur satu per satu):
 *   1. sisi kiri CHAR-POINTER, sisi kanan STRUCT. Campuran ini yang memutus
 *      CSE atas `recbase` -- biner memuatnya DUA KALI, bukan sekali.
 *   2. sisi kiri bentuk PENUNJUK `(... + basis)[1]`, BUKAN offset
 *      `basis[... + 1]`. Yang pertama melipat +1 jadi displacement `[si+1]`;
 *      yang kedua memancarkan `inc ax` lalu `[si]`.
 *   3. URUTAN OPERAN dibalik: `(0xc * list[idx+1] + (char *)recbase)`, bukan
 *      `((char *)recbase + 0xc * list[idx+1])`. Basis harus dimuat SESUDAH
 *      perkalian; urutan sebaliknya menghoist pemuatan basis dan menambah
 *      spill. Ini menghemat 4 byte.
 *
 * SISA di blok itu: kita `mov dx,[73Ch] / mov si,dx` (2 instruksi), asli
 * `mov di,[73Ch]` (1). Asli memuat langsung ke register indeks. Cast
 * `(char *)` tampaknya memaksa lewat DX dulu. Belum ketemu bentuk yang
 * menghindarinya TANPA memakai nama extern kedua untuk alamat yang sama --
 * dan itu TIDAK BOLEH (gendata.py akan memancarkan array ukuran nol).
 *
 * SUDAH DICOBA & GAGAL (urutan k/k2, diukur DUA KALI: sebelum dan sesudah
 * badan membesar, hasilnya sama):
 *   `q;sel;k;k2` -> +193 | `k2=list[idx];k=k2` -> +220
 *   `k2=list[idx];k=list[idx]` -> +220 | `k=list[idx];k2=k` -> +231 (terbaik)
 *
 * DIVERGENSI di +231: urutan flush [16h]/[1Eh]. Asli juga menyimpan
 * `[bp+2]=si` (penunjuk &list[idx]) di sana. Dugaan terkuat: sumbernya
 * MEMAKAI ULANG penunjuk itu di blok berikutnya (0x4474 ke atas) yang belum
 * ditulis -- jadi tulis dulu blok itu sebelum mengejar urutan flush lagi.
 *
 * BELUM ditulis: 0x4474 ke atas (~1.400 byte).
 */
