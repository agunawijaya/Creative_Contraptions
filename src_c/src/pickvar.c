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
    char *rb;           /* 44h  salinan recbase -- char* (bukan int + cor):
                           bentuk penunjuk asli dimuat LANGSUNG ke SI */
    char *rp2;          /* 46h  penunjuk record ke-2 (dari salinan rb) */
    int  cnt;           /* 48h  pencacah percobaan acak */
    int  dv;            /* 4Ah  selisih baris y1-ya, sebelum di-abs */
    struct rec *rp;     /* 4Ch */
    char f7[2];         /* 4Eh */
    int  ok;            /* 50h  boleh dipilih? */

    rb = recbase;
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
    k2 = list[idx];
    k = k2;
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
        /* ⭐ Sisi kanan `list[idx] * 0xc`, BUKAN `k * 0xc` -- walau nilainya
           sama. Dengan `list[idx]` kompiler meng-CSE pemuatannya: nilainya
           tetap di CX (`mov ax,cx`) dan alamat `&list[idx]` jadi temp yang
           di-spill ke [bp+2]. Itu menggeser SELURUH penomoran temp sesudahnya
           ke [bp+4]/[bp+6] seperti aslinya, DAN membebaskan CX sehingga uji
           `idx + 1 < n` memakai DX. Dengan `k`, ketiganya meleset sekaligus.
           Diukur di wilayah sejajar 0x42ca..0x44fd: 528/563 -> 562/563. */
        if ((0xc * list[idx + 1] + recbase)[1] - 100 ==
                (list[idx] * 0xc + recbase)[1]) {
            /* Pola drawpair: char di MS C 1.04 itu unsigned, jadi tandanya
               dipulihkan lewat TERNARY dengan nilai-apa-adanya di posisi
               FALSE (cabang yang MEMUAT ULANG dari slot). */
            sel = list[idx + 1];
            rp2 = rb + sel * 0xc;
            dx2 = rp2[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = rp2[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            load(fh, recbase, sel, buf);
            blit(buf, x + dx2, y + dy2, rp2[2], rp2[3]);
        }
    }
again:
    /* Puncak loop LUAR (0x4474): tiap ganti varian, geometri dihitung ulang. */
    if (k2 < 0 || k2 > 0x78) {
        /* Jalur ini melompat ke 0x475F (blok kotak), BUKAN ke return.
           Fungsi aslinya TIDAK punya epilog di ujung -- semua keluar lewat
           salah satu return di dalam switch. */
        printf(0x1de8, k2);
        goto tail;
    }
    rp2 = rb + k2 * 0xc;
    dx3 = rp2[4];
    dx3 = (dx3 >= 0x80) ? dx3 - 0x100 : dx3;
    dy3 = rp2[5];
    dy3 = (dy3 >= 0x80) ? dy3 - 0x100 : dy3;
    ww = rp2[2];
    hh = rp2[3];
    x1 = x + dx3;
    y1 = y + dy3;
    x2 = x1 + ww;
    y2 = y1 + hh;
    /* `q == idx` SELALU salah (q = idx + 141h). Blok yang dilewati karenanya
       TIDAK PERNAH TERCAPAI di biner asli -- tapi byte-nya ada, jadi tetap
       harus ditulis. Jangan "diperbaiki". */
    /* `idx == q`, BUKAN `q == idx`: aslinya memuat idx ke AX lebih dulu dan
       memakainya ULANG di perbandingan berikutnya (add ax,141h). */
    if (idx == q)
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
            dx2 = rp2[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = rp2[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            fillrect(y + dy2, x + dx2, y + dy2 + rp2[3] - 1,
                     x + dx2 + rp2[2] - 1, 1);
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
            dx2 = rp2[4];
            dx2 = (dx2 >= 0x80) ? dx2 - 0x100 : dx2;
            dy2 = rp2[5];
            dy2 = (dy2 >= 0x80) ? dy2 - 0x100 : dy2;
            load(fh, recbase, sel, buf);
            /* BEDA dengan kembarannya di 0x4455: yang ini MENYIMPAN keempat
               sudutnya ke slot 34/38/3c/40 sebelum memanggil blit. */
            x1 = x + dx2;
            y1 = y + dy2;
            x2 = x1 + rp2[2];
            y2 = y1 + rp2[3];
            blit(buf, x1, y1, rp2[2], rp2[3]);
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
    /* `oy` DULU: aslinya memuat dy3 ([bp+0ch]) sebelum dx3 ([bp+0eh]).
       Muatan mengikuti urutan SUMBER; simpanannya ditata ulang kompiler
       (ox lebih dulu), jadi urutan sumber terbaca dari MUATANNYA. */
    oy = dy3;
    ox = dx3;
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
        if (idx > 0 && (list[idx - 1] * 0xc + recbase)[1] > 100)
            idx--;
        /* `if (--idx < 0)` -- BUKAN `idx--; if (idx < 0)`. Yang kedua
           memakai ulang flag dari DEC (jge, 2 byte lebih pendek); aslinya
           memancarkan `test ax,ax` eksplisit lalu `jns`. */
        if (--idx < 0) {
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
    /* ⭐ `default:` EKSPLISIT walau tak ada case yang `break`. Tanpa ini
       kompiler MENGHAPUS sasaran "keluar switch"; aslinya memancarkannya
       sebagai `jmp inner` di 0x4956 -- 3 byte tepat SESUDAH badan case
       terakhir, sebelum tabel switch. Tak terjangkau, tapi ada di biner.
       Diukur dengan pembandingan ekor berkompensasi geseran (0x4515..akhir):
       104/1143 -> 1137/1143 byte cocok. */
    default:
        break;
    }
    goto inner;
}

/* ⏳ DRAF — SELURUH fungsi sudah tertulis (tidak ada blok yang belum digarap).
 * Panjang 1.726 vs 1.730 asli. TERJAJAR 1.616/1.730 (93%).
 *
 * ⚠ CARA MENGUKUR. Jangan pakai "byte cocok per POSISI" untuk fungsi yang
 * panjangnya belum pas: satu sisipan menggeser sisa berkas dan byte yang
 * sebenarnya benar terhitung salah. Angka posisi fungsi ini cuma 368 padahal
 * yang benar-benar sejajar 1.616. Pakai alat penjajaran:
 *     python src_c/verify/aligncmp.py pickvar
 *     python src_c/verify/aligncmp.py pickvar --sbs 43f1 44 -1   (berdampingan)
 *
 * ⭐ EKOR SUDAH TERBUKTI IDENTIK. Tabel switch (7 entri, nilai 14Bh/34h/
 * 14Dh/36h/0Dh/20h/1Bh) dan pemindainya cocok INSTRUKSI DEMI INSTRUKSI;
 * bedanya cuma displacement karena kode di depannya lebih pendek. Jadi
 * geseran +4 @0x495A itu AKUMULASI, bukan cacat tersendiri -- yang benar-benar
 * salah tinggal DUA titik, bukan tiga.
 *
 * ⏸ DIPARKIR (2026-08-01) -- SATU situs, 2 byte, sebabnya SUDAH DIPAHAMI tapi
 *   levernya belum ada. Syarat membuka lagi ada di ujung catatan ini.
 *
 * ⏳ SISA SATU SITUS: 0x44fd, +2 byte (geseran +2 di 0x4515).
 *   asli : mov [bp+0ch],bx / mov bx,[bp+0ah] / cmp bx,ax ... add ax,141h / cmp ax,bx
 *   kita : cmp ax,[bp+0ah]        ... mov [bp+0ch],bx ... cmp ax,[bp+0ah]
 *   Asli meng-COMMIT simpanan tertunda `dy3` (slot 0Ch, hasil ternary yang
 *   masih di BX) SEBELUM perbandingan, sehingga BX bebas dan `q` masuk
 *   register lalu DIPAKAI ULANG di uji kedua. Kita menahan BX dan memakai
 *   operan memori dua kali. Kelas yang SAMA dengan loadcon 0x5115.
 *   Diukur di prefiks sejajar 0x42ca..0x4600: semua varian di bawah IDENTIK
 *   (806/822), jadi tak satu pun menyentuh situsnya.
 *   DICOBA & GAGAL (2026-07-31, 32 varian lewat sweep.py --cmp):
 *     uji-1  : idx==q | q==idx | idx-q==0 | !(idx!=q) | `if (idx!=q) goto`
 *     uji-2  : idx+141h!=q | q!=idx+141h | q-idx!=141h | idx-q+141h!=0 |
 *              q!=141h+idx | 141h+idx!=q
 *     ternary dy3 : bentuk `if`, arah dibalik
 *     urutan x1/y1/x2/y2 (4 permutasi), urutan ww/hh
 *   Sasaran berikutnya harus PENJADWALAN SIMPANAN, bukan bentuk uji.
 *
 * ⭐ MEKANISMENYA SUDAH TERBUKTI (lihat src_c/README.md "LABEL TELANJANG"):
 *   MC2 meng-commit simpanan tertunda di BATAS BLOK DASAR, dan sebuah label C
 *   telanjang (tanpa `goto` ke sana) sudah cukup membuat batas itu -- nol byte.
 *   Itu yang menutup `place` 501/503 -> 503/503.
 *   Di SINI lever itu TERLALU TUMPUL: label mem-flush KETIGA simpanan tertunda
 *   (dy3/bx, y2/cx, x2/dx), sedangkan asli hanya membuang SATU -- BX, yang
 *   TERTUA -- lalu memakainya untuk `q`:
 *       44fa mov ax,[bp+62]   44fd mov [bp+0ch],bx   4500 mov bx,[bp+0ah]
 *       4503 cmp bx,ax        4505 mov [bp+40h],cx   4508 mov [bp+38h],dx
 *   Delapan posisi label dicoba (sebelum rp2/ww/x1/y1/x2/y2 dan sebelum kedua
 *   uji): tak satu pun memberi spill selektif. `q == idx` memberi byte IDENTIK
 *   dengan `idx == q` di berkas nyata (di reproduksi mini justru BERBEDA).
 *
 * ⏸ SYARAT MEMBUKA LAGI: begitu diketahui aturan SPILL SELEKTIF -- kapan MC2
 *   membuang SATU register tertua untuk mendapat operan-register bagi sebuah
 *   perbandingan, alih-alih memakai operan MEMORI. Itu satu-satunya keputusan
 *   yang memisahkan kita dari asli di situs ini.
 *
 * ⚠ SUDAH DICOBA & GAGAL untuk perbandingan `idx == q` (5 bentuk):
 *   idx==q | q==idx | idx-q==0 | q-idx==0 | !(idx!=q)
 * Semuanya memancarkan `cmp ax,[mem]` (4 byte), sedangkan aslinya
 * `mov bx,[q]` + `cmp bx,ax` (6 byte). Bentuk ekspresi TIDAK bisa memaksa
 * pemuatan ke register; itu keputusan alokasi register kompiler.
 *
 * SISA GESERAN (tinggal tiga titik):
 *   +3 @0x43B8  aslinya memancarkan `mov [bp+2],si` (spill) yang tidak kita
 *               keluarkan. Di kemunculan KEDUA (0x4633) spill yang sama SUDAH
 *               keluar, jadi bedanya tekanan register dari `k`/`k2` di atasnya.
 *   +1 @0x4515  satu byte
 *   +4 @0x495A  ekor/tabel switch
 * Register SI vs BX di 0x4400 tidak menggeser panjang (cuma angka POSISI).
 *
 * ⭐ ATURAN YANG DIDAPAT DI FUNGSI INI (berlaku umum, sudah masuk README):
 * 1. Akses record SELALU bentuk PENUNJUK `(idx * 0xc + recbase)[n]`.
 *    Bentuk offset `((char*)recbase)[idx*0xc+n]` memuat recbase DUA KALI.
 *    Bentuk struct `((struct rec*)recbase)[idx].f` memuat recbase dini ke DX
 *    lalu men-spill-nya. KOREKSI: catatan lama yang bilang "sisi kanan harus
 *    bentuk struct supaya CSE putus" itu KELIRU.
 * 2. Yang membedakan kedua sisi perbandingan cuma URUTAN OPERAN kali:
 *      `0xc * list[i]` -> mov ax,0Ch / imul word ptr [bx]
 *      `k * 0xc`       -> mov ax,cx  / mov dx,0Ch / imul dx
 * 3. `if (--x < 0)` != `x--; if (x < 0)`. Yang kedua memakai ulang flag DEC
 *    (jge); aslinya `test ax,ax` + `jns`, hanya keluar dari bentuk pre-dec.
 * 4. SWITCH JARANG: tabel nilai/label disusun KEBALIKAN urutan sumber.
 *    Pemindai mulai dari entri TERAKHIR (si=18h, sub si,4, jns).
 *    Urutan case di sumber = urutan ALAMAT badannya.
 * 5. `idx == q` bukan `q == idx` -- operan kiri dimuat lebih dulu dan dipakai
 *    ulang di perbandingan berikutnya.
 * 6. Jangan menganggap slot yang belum dikenali itu "filler". Di fungsi ini
 *    LIMA kali berturut tebakan filler ternyata variabel nyata
 *    (36/3A/3E/42, 2C..33, 18/1C/50, 20, 4A).
 * 7. Kalau dua blok terlihat kembar, ukur DUA-DUANYA: 0x4455 dan 0x46A0 sama
 *    persis kelihatannya, tapi yang kedua menyimpan keempat sudut ke slot.
 *    Sebaliknya 0x4713 memang duplikat byte-per-byte dari 0x46CD.
 *
 * ⭐⭐ MISTERI GHIDRA TERPECAHKAN (tetap berlaku). `if (param_7 + 0x141 !=
 * param_7)` berasal dari DUA perbandingan nyata di 0x4500..0x4519. Karena
 * `q = idx + 0x141`, keduanya SELALU salah, jadi blok 0x451A..0x45DC tidak
 * pernah tercapai -- tapi bytenya ADA dan wajib direproduksi. Jangan dihapus.
 *
 * SUDAH DICOBA & GAGAL (diukur dgn metrik PENJAJARAN, bukan posisi):
 *   urutan `k2 = list[idx]; k = k2;`        -> 1.462 (vs 1.495 utk k dulu)
 *   sisi kanan bentuk struct                -> 1.460 (vs 1.495)
 *   fillrect bentuk struct `[k].h`          -> bingkai jadi 54h, tidak boleh
 *   fillrect via rp2 yang sudah ada         -> 1.686 byte, lebih buruk
 *   `x--; if (x < 0)` dan `if (!(x >= 0))`  -> 1.609 (vs 1.614 utk pre-dec)
 *   menulis `list[idx]` dua kali            -> IDENTIK (kompiler meng-CSE)
 */
