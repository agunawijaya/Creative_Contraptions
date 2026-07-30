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

/* Dideklarasikan char* (bukan struct rec*) supaya akses ber-indeks memuat
   basis LANGSUNG ke register indeks (`mov di,[73Ch]`). Dengan struct rec*
   lalu di-cast, kompiler memuatnya ke DX dulu lalu `mov si,dx` -- 2 byte
   berlebih di TIAP akses. Sisi yang butuh bentuk struct di-cast balik. */
extern char *recbase;       /* @0x73c */
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
    int  dy3;           /* 0Ch  geser y record UTAMA, BERTANDA */
    int  dx3;           /* 0Eh  geser x record UTAMA, BERTANDA */
    char f1[6];         /* 10h..15h */
    int  k2;            /* 16h  salinan kedua list[idx] */
    char f2[2];         /* 18h */
    int  sel;           /* 1Ah  nilai balik, mulai -1 */
    char f3[2];         /* 1Ch */
    int  k;             /* 1Eh  = list[idx] */
    char f4a[6];        /* 20h..25h */
    int  hh;            /* 26h  tinggi record utama */
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
                rp = (struct rec *)(recbase + list[idx] * 0xc);
            } while (rp->row > 100 || (rp->id < 0x80 && cnt < 0x73));
        }
        else {
            do {
                idx = rnd(n);
                rp = (struct rec *)(recbase + list[idx] * 0xc);
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
        if ((0xc * list[idx + 1] + recbase)[1] - 100 ==
                ((struct rec *)recbase)[k].row) {
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
    if (k2 < 0 || k2 > 0x78) {
        printf(0x1de8, k2);
        goto done;
    }
    rp2 = rb + k2 * 0xc;
    dx3 = ((char *)rp2)[4];
    dx3 = (dx3 >= 0x80) ? dx3 - 0x100 : dx3;
    dy3 = ((char *)rp2)[5];
    dy3 = (dy3 >= 0x80) ? dy3 - 0x100 : dy3;
    hh = ((char *)rp2)[3];
done:
    return idx;
}

/* ⏳ DRAF — 543 byte ditulis, 256 byte cocok. Divergensi pertama +231.
 *
 * ⭐ EMPAT bentuk penulisan yang sudah TERBUKTI, semuanya diukur satu per satu.
 * Keempatnya akan dipakai ulang di ~1.200 byte sisanya dan kemungkinan di
 * `main` juga:
 *
 * 1. `recbase` dideklarasikan **char\***, bukan `struct rec *` lalu di-cast.
 *    Dengan cast, kompiler memuat basis ke DX dulu lalu `mov si,dx` -- 2 byte
 *    berlebih di TIAP akses. Sebagai char* ia memuat LANGSUNG ke register
 *    indeks. Sisi yang butuh bentuk struct di-cast BALIK.
 * 2. Sisi kiri char-pointer, sisi kanan struct: campuran ini MEMUTUS CSE atas
 *    `recbase` -- biner memuatnya DUA KALI, bukan sekali lalu dipakai ulang.
 * 3. Bentuk PENUNJUK `(... + basis)[1]`, bukan offset `basis[... + 1]`.
 *    Yang pertama melipat +1 jadi displacement; yang kedua memberi `inc ax`.
 * 4. URUTAN OPERAN: `(0xc * idx + basis)`, bukan `(basis + 0xc * idx)`.
 *    Basis harus dimuat SESUDAH perkalian. Hemat 4 byte.
 *
 * ⭐ bp+08h itu TEMP KELIMA, bukan lokal. Temp menempati bp+00..09, lokal
 * mulai bp+0Ah. Daftar "slot tidak terpakai" (00 08 14 22 4E) MENYESATKAN.
 *
 * DIAGNOSIS SISA (diukur dengan menyejajarkan geseran, bukan ditebak):
 * dengan geseran +3 byte, blok 240..249 cocok INSTRUKSI DEMI INSTRUKSI. Jadi
 * strukturnya benar; yang kurang cuma:
 *   a. `[bp+2] = si` -- asli MENYIMPAN penunjuk &list[idx]; kita tidak.
 *      Inilah sumber geseran 3 byte itu, DAN kemungkinan besar juga sumber
 *      urutan flush [16h]/[1Eh] yang beda di +231.
 *   b. register SI vs DI di akses record (panjang sama, byte beda).
 *
 * Karena (a) menjelaskan dua gejala sekaligus, itu yang harus dikejar: cari
 * di blok BELUM DITULIS (0x44ea ke atas) di mana &list[idx] dipakai lagi --
 * pemakaian ulang itulah yang memaksa kompiler menyimpannya.
 *
 * SUDAH DICOBA & GAGAL (urutan k/k2, diukur DUA KALI):
 *   `q;sel;k;k2` -> +193 | `k2=list[idx];k=k2` -> +220
 *   `k2=list[idx];k=list[idx]` -> +220 | `k=list[idx];k2=k` -> +231 (terbaik)
 *
 * BELUM ditulis: 0x44ea ke atas (~1.200 byte).
 */
