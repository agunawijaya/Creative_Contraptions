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
extern int ta;              /* @0x7ec */
extern int tb;              /* @0x7ea */
extern int mode;            /* @0x792 */
extern int tx;              /* @0x7ee */

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
    int  oy;            /* 10h */
    int  ox;            /* 12h */
    char f1[2];         /* 14h  tak dipakai di biner */
    int  k2;            /* 16h  salinan kedua list[idx] */
    int  i;             /* 18h  pencacah kedip luar */
    int  sel;           /* 1Ah  nilai balik, mulai -1 */
    int  j;             /* 1Ch  pencacah tunda dalam */
    int  k;             /* 1Eh  = list[idx] */
    int  c;             /* 20h  tombol yang ditekan */
    char f4a[2];        /* 22h */
    int  ww;            /* 24h  lebar record utama */
    int  hh;            /* 26h  tinggi record utama */
    int  dx2;           /* 28h  geser x record ke-2, BERTANDA */
    int  dy2;           /* 2Ah  geser y record ke-2, BERTANDA */
    int  bx0;           /* 2Ch  kotak gabungan: kiri */
    int  by0;           /* 2Eh  atas */
    int  bw;            /* 30h  lebar */
    int  bh;            /* 32h  tinggi */
    int  x1;            /* 34h  = x + dx3 */
    int  xa;            /* 36h  set KEDUA, dipakai blok 46CD/471B */
    int  x2;            /* 38h  = x1 + ww */
    int  xb;            /* 3Ah */
    int  y1;            /* 3Ch  = y + dy3 */
    int  ya;            /* 3Eh */
    int  y2;            /* 40h  = y1 + hh */
    int  yb;            /* 42h */
    int  rb;            /* 44h  salinan recbase */
    int  rp2;           /* 46h  penunjuk record ke-2 (dari salinan rb) */
    int  cnt;           /* 48h  pencacah percobaan acak */
    int  dv;            /* 4Ah  selisih baris y1-ya, sebelum di-abs */
    struct rec *rp;     /* 4Ch */
    char f7[2];         /* 4Eh */
    int  ok;            /* 50h  boleh dipilih? */

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
        /* ⚠ KOREKSI catatan lama: sisi kanan BUKAN bentuk struct. KEDUANYA
           bentuk penunjuk char; yang membedakan cuma URUTAN OPERAN kali:
             kiri  `0xc * list[idx+1]` -> mov ax,0Ch / imul word ptr [bx]
             kanan `k * 0xc`           -> mov ax,cx  / mov dx,0Ch / imul dx
           Bentuk struct di sisi kanan memaksa recbase dimuat lebih awal ke DX
           lalu di-spill ke bingkai (+6 byte). Dengan dua-duanya penunjuk,
           recbase memang dimuat DUA KALI (DI lalu SI) seperti aslinya. */
        if ((0xc * list[idx + 1] + recbase)[1] - 100 ==
                (k * 0xc + recbase)[1]) {
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
again:
    /* Puncak loop LUAR (0x4474): tiap ganti varian, geometri dihitung ulang. */
    if (k2 < 0 || k2 > 0x78) {
        printf(0x1de8, k2);
        goto done;
    }
    rp2 = rb + k2 * 0xc;
    dx3 = ((char *)rp2)[4];
    dx3 = (dx3 >= 0x80) ? dx3 - 0x100 : dx3;
    dy3 = ((char *)rp2)[5];
    dy3 = (dy3 >= 0x80) ? dy3 - 0x100 : dy3;
    ww = ((char *)rp2)[2];
    hh = ((char *)rp2)[3];
    x1 = x + dx3;
    y1 = y + dy3;
    x2 = x1 + ww;
    y2 = y1 + hh;
    /* `q == idx` SELALU salah (q = idx + 141h). Blok yang dilewati karenanya
       TIDAK PERNAH TERCAPAI di biner asli -- tapi byte-nya ada, jadi tetap
       harus ditulis. Jangan "diperbaiki". */
    if (q == idx)
        goto part2;
    /* BLOK MATI: `idx + 141h != q` selalu salah karena q diset = idx + 141h.
       Byte-nya ada di biner (0x451A..0x45DC) jadi tetap ditulis apa adanya. */
    if (idx + 0x141 != q) {
        /* Bentuk PENUNJUK (aturan 3), BUKAN offset ((char*)recbase)[k*0xc+3]:
           yang offset memaksa recbase dimuat DUA KALI (+15 byte). Bentuk
           struct `[k].h` memberi instruksi yang benar tapi menuntut temp
           kelima -- bingkai jadi 54h, jadi tidak bisa dipakai. */
        fillrect(y + oy, x + ox,
                 y + oy + (k * 0xc + recbase)[3] - 1,
                 x + ox + (k * 0xc + recbase)[2] - 1, 1);
        if (sel != -1) {
            rp2 = rb + sel * 0xc;
            dx2 = ((char *)rp2)[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = ((char *)rp2)[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            fillrect(y + dy2, x + dx2, y + dy2 + ((char *)rp2)[3] - 1,
                     x + dx2 + ((char *)rp2)[2] - 1, 1);
        }
    }
    /* Pola yang SAMA berulang di 0x45DD, tapi `q = idx` (bukan idx+141h). */
    q = idx;
    sel = -1;
    if (idx + 1 < n) {
        if ((0xc * list[idx + 1] + recbase)[1] - 100 ==
                (list[idx] * 0xc + recbase)[1]) {
            /* Blok load/blit IDENTIK dengan yang di 0x43F6 -- bentuk yang
               sudah terbukti dipakai ulang tanpa perubahan. */
            sel = list[idx + 1];
            rp2 = rb + sel * 0xc;
            dx2 = ((char *)rp2)[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = ((char *)rp2)[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            load(fh, recbase, sel, buf);
            /* BEDA dengan kembarannya di 0x4455: yang ini MENYIMPAN keempat
               sudutnya ke slot 34/38/3c/40 sebelum memanggil blit. */
            x1 = x + dx2;
            y1 = y + dy2;
            x2 = x1 + ((char *)rp2)[2];
            y2 = y1 + ((char *)rp2)[3];
            blit(buf, x1, y1, ((char *)rp2)[2], ((char *)rp2)[3]);
        }
    }
    /* 0x46CD -- di LUAR kedua if; kedua kegagalan syarat melompat ke sini. */
    load(fh, recbase, k2, buf);
    xa = x + dx3;
    ya = y + dy3;
    xb = xa + ww;
    yb = ya + hh;
    blit(buf, xa, ya, ww, hh);
    goto tail;
part2:
    /* 0x4713 -- badannya DUPLIKAT PERSIS blok 0x46CD (68 byte, byte demi
       byte). Sumbernya karena itu juga harus identik. */
    if (k != k2) {
        load(fh, recbase, k2, buf);
        xa = x + dx3;
        ya = y + dy3;
        xb = xa + ww;
        yb = ya + hh;
        blit(buf, xa, ya, ww, hh);
    }
tail:
    /* 0x475F -- kotak gabungan. Kalau kedua bagian berjauhan (>= 50 baris),
       pakai kotak bagian KEDUA saja; kalau berdekatan, gabungkan keduanya. */
    dv = y1 - ya;
    if ((dv < 0 ? -dv : dv) >= 0x32) {
        bx0 = xa;
        by0 = ya;
        bw = xb - xa;
        bh = yb - ya;
    }
    else {
        bx0 = (x1 <= xa) ? x1 : xa;
        by0 = (y1 <= ya) ? y1 : ya;
        bw = ((x2 > xb) ? x2 : xb) - bx0;
        bh = ((y2 > yb) ? y2 : yb) - by0;
    }
    /* 0x47D2 -- kedipkan kotak gabungan dua kali; tiap kedip menunggu 12 kali
       retrace kecuali ditekan tombol. `timebar` hanya jalan kalau tb habis. */
inner:
    /* Puncak loop DALAM (0x47D2). */
    tb = ta;
    /* Kedipnya BUKAN sekali jalan: seluruhnya badan do-while yang berputar
       sampai ada tombol atau `ok` padam (lompatan 0x485C balik ke 0x47D8). */
    do {
        for (i = 0; i < 2; i++) {
            drawrect(bx0, by0, bw, bh, 3);
            hintmark();
            for (j = 0; j < 0xc; j++) {
                if (keyhit())
                    break;
                ta = tb;
                if (ta <= 0)
                    timebar();
                vbend();
                vbwait();
            }
        }
        ok = 1;
        if (mode == 4 && tx <= 0)
            ok = 0;
        ta = tb;
        if (ta <= 0)
            timebar();
    } while (keyhit() == 0 && ok != 0);
    /* Keluar TANPA `mov sp,bp` -- epilognya `add sp,52h; pop bp; ret`. */
    if (mode == 4 && tx <= 0)
        return 0xfe;
    c = getkey();
    if (c == 0)
        c = getkey() + 0x100;
    k = k2;
    ox = dx3;
    oy = dy3;
    /* SWITCH JARANG (tabel nilai/label di 0x4959..0x4974, pemindai di 0x4975).
       ⭐ Tabelnya disusun KEBALIKAN urutan sumber: entri terakhir di tabel
       diuji lebih dulu. Urutan case di sumber = urutan alamat badannya. */
    switch (c) {
    case 0x36:
    case 0x14d:
        /* maju satu varian */
        if (sel != -1)
            idx++;
        idx++;
        if (idx >= n)
            idx = 0;
        k2 = list[idx];
        goto again;
    case 0x34:
    case 0x14b:
        /* mundur satu varian; baris > 100 berarti potongan lanjutan, lewati */
        if (idx > 0 && ((struct rec *)recbase)[list[idx - 1]].row > 100)
            idx--;
        idx--;
        if (idx < 0) {
            idx = n - 1;
            if ((list[idx] * 0xc + recbase)[1] > 100)
                idx--;
        }
        k2 = list[idx];
        goto again;
    case 0xd:
        return idx;
    case 0x20:
        return idx | 0x8000;
    case 0x1b:
        return -1;
    }
    goto inner;
done:
    return idx;
}

/* ⏳ DRAF — 543 byte ditulis, 256 cocok. Divergensi pertama +231.
 *
 * ⭐⭐ MISTERI GHIDRA TERPECAHKAN. `if (param_7 + 0x141 != param_7)` berasal
 * dari DUA perbandingan nyata di 0x4500..0x4519:
 *       mov bx,[bp+0Ah] ; cmp bx,ax ; jne .. ; jmp 4713   -> if (q == idx) goto L4713;
 *       add ax,141h     ; cmp ax,bx ; jne .. ; jmp 45DD   -> if (idx+141h != q) {...}
 * Karena `q = idx + 141h` (diset di 0x439C), syarat pertama SELALU salah dan
 * kedua SELALU salah -- jadi blok 0x451A..0x45DC (~200 byte) TIDAK PERNAH
 * TERCAPAI di biner asli. Ghidra melipat keduanya jadi satu syarat mustahil.
 *
 * ⚠ Blok mati itu TETAP HARUS DIREPRODUKSI byte-per-byte. Jangan "diperbaiki"
 * dan jangan dihapus -- byte-nya ada di biner. Ini bukti kedua (sesudah bug
 * `load`) bahwa biner ini memuat kode yang tak pernah jalan.
 *
 * ⭐ EMPAT bentuk penulisan akses record yang sudah TERBUKTI (pakai ulang di
 * sisa fungsi dan kemungkinan di `main`):
 * 1. `recbase` dideklarasikan char*, BUKAN struct rec* lalu di-cast (cast
 *    memaksa lewat DX: `mov dx,[73Ch] / mov si,dx` = 2 byte berlebih/akses).
 * 2. sisi kiri char-pointer + sisi kanan struct = MEMUTUS CSE atas recbase.
 * 3. bentuk PENUNJUK `(... + basis)[1]`, bukan offset `basis[... + 1]`.
 * 4. urutan operan `(0xc*idx + basis)` -- basis dimuat SESUDAH perkalian.
 *
 * ⭐ bp+08h itu TEMP KELIMA, bukan lokal (temp = bp+00..09, lokal dari 0Ah).
 * Daftar "slot tidak terpakai" (00 08 14 22 4E) MENYESATKAN.
 *
 * DIAGNOSIS SISA di +231, diukur dengan menyejajarkan geseran: dengan geseran
 * +3 byte, blok 240..249 cocok INSTRUKSI DEMI INSTRUKSI. Strukturnya benar;
 * yang kurang cuma `[bp+2] = si`.
 * ⚠ [bp+2] itu SLOT TEMP yang dipakai ulang (store di 43B5, 4547, 45C3, 4633;
 * push di 4553, 45CF), dan yang di 43B5 MATI. Jadi mengejarnya lewat bentuk
 * ekspresi kemungkinan sia-sia: sudah dicoba menulis `list[idx]` DUA KALI
 * (aturan runfill "menulis ulang memesan temp") -- hasilnya IDENTIK, kompiler
 * tetap meng-CSE-nya. Kemungkinan besar alokasi temp baru berubah setelah
 * blok 0x451A..0x4713 ditulis.
 *
 * SUDAH DICOBA & GAGAL (urutan k/k2, diukur DUA KALI):
 *   `q;sel;k;k2` -> +193 | `k2=list[idx];k=k2` -> +220
 *   `k2=list[idx];k=list[idx]` -> +220 | `k=list[idx];k2=k` -> +231 (terbaik)
 *   `k=list[idx];k2=list[idx]` -> IDENTIK dengan yang terbaik (di-CSE)
 *
 * BELUM ditulis: 0x44ea ke atas (~1.200 byte), termasuk blok mati di
 * 0x451A..0x45DC.
 */
