/* FUN_1000_4e3e @ 1000:4e3e, 503 byte — susun tabel slot contraption dan muat
 * semua sprite-nya.
 *
 * Tiga fase:
 *  1. Untuk tiap jawaban ans[i] >= 0: salin record part dari `rectab` ke tabel
 *     slot `dt`, muat data sprite-nya ke penyangga `p`, lalu IKUTI RANTAI —
 *     kalau record berikutnya masih part yang sama (id sama, dan row sama atau
 *     row+100 sama), record itu juga disalin. `flag[i]` mencatat slot awal.
 *  2. Tutup tabel dengan satu slot nol.
 *  3. Untuk tiap slot yang tercatat di `flag[]`: cari padanannya di tabel objek
 *     (`objtab`, global 0x73e) berdasar id+row, muat sprite reaksinya ke
 *     penyangga `q`, dan simpan penunjuknya di field +8. Kalau tak ketemu,
 *     field +8 dinolkan.
 *
 *   objfh @0x72e, objtab @0x73e ; load()=53ff, printf()=6a48
 *   Balikan: jumlah slot terpakai MINUS satu.
 *
 * Tabel slot 12 byte: 6 byte pertama disalin apa adanya dari record part,
 * +6 = penunjuk data sprite, +8 = penunjuk data sprite reaksi. Tabel slot game
 * ada di DGROUP 0x1a8 — cocok dengan `drawslot` yang membaca field +6-nya
 * lewat alamat 0x1ae (= 0x1a8 + 6).
 *
 * PETA SLOT (bingkai 26h; temp bp+0,2,4; 16 lokal bp+6..24h berurutan):
 *   6=dt  8=dp  0ah=sp  0ch=k  0eh=i  10h=cnt 12h=di 14h=sidx
 *   16h=p 18h=q 1ah=t1  1ch=id 1eh=row 20h=found 22h=j 24h=t2
 * `sp` dipakai DUA peran: penunjuk record sumber (fase 1) dan penyusur objtab
 * (fase 3). `i` juga dipakai ulang di fase 3 untuk menampung flag[j].
 *
 * Kedua uji keluar loop memakai bentuk "jcc pendek ke badan; jmp jauh" bukan
 * karena `else`, tapi karena target keluarnya >127 byte (0x4f3a) sehingga
 * lompatan bersyarat pendek tak sampai.
 */

struct slot {
    char id;                /* +0  */
    char row;               /* +1  */
    char w;                 /* +2  */
    char h;                 /* +3  */
    char dx;                /* +4  */
    char dy;                /* +5  */
    int  spr;               /* +6  penunjuk data sprite */
    int  spr2;              /* +8  penunjuk data sprite reaksi */
    char pad10[2];          /* +10..11 */
};

extern int objfh;           /* @0x72e */
extern int objtab;          /* @0x73e */

place(dtab, rectab, fh, buf, buf2, n, ans, flag)
struct slot *dtab;
struct slot *rectab;
int   fh;
int   buf, buf2, n;
int  *ans;
int  *flag;
{
    struct slot *dt;
    struct slot *dp;
    struct slot *sp;
    int k, i, cnt, di, sidx, p, q, t1, id, row, found, j, t2;

    /* URUTAN INI PENTING: biner memuat argumen ke register menurut urutan
       pemakaian di sumber (ax=dtab, bx=buf, cx=buf2, dx=0). Menukar `p` dan
       `q` membuat bx/cx/dx tertukar walau nilai akhirnya sama. */
    dt = dtab;
    p = buf;
    q = buf2;
    cnt = 0;
    i = 0;
    while (i < n) {
        flag[i] = cnt;
        di = cnt;
        sidx = ans[i];
        if (sidx < 0)
            break;
        do {
            dp = &dt[di];
            sp = &rectab[sidx];
            /* enam penugasan TERPISAH: biner memuat "mov al,[si+k]" lalu
               "mov [bx+k],al" satu per satu, urut naik — bukan loop. */
            dp->id = sp->id;
            dp->row = sp->row;
            dp->w = sp->w;
            dp->h = sp->h;
            dp->dx = sp->dx;
            dp->dy = sp->dy;
            dp->spr = p;
            t1 = load(fh, rectab, sidx, p);
            p = p + t1;
            cnt = cnt + 1;
            sidx = sidx + 1;
            di = di + 1;
        } while (sp->id == rectab[sidx].id &&
                 (sp->row == rectab[sidx].row ||
                  sp->row + 100 == rectab[sidx].row));
        i = i + 1;
    }
    /* fase 2: slot penutup nol */
    dp = &dt[di];
    dp->id = 0;
    dp->row = 0;
    dp->w = 0;
    dp->h = 0;
    dp->dx = 0;
    dp->dy = 0;
    dp->spr = 0;
    dp->spr2 = 0;
    j = 0;
    while (j < n) {
        i = flag[j];
        if (i < 0)
            break;
        dp = &dt[i];
        /* Urutan pemuatan register di biner: ax=dp->id, cx=dp->row, dx=0,
           lalu ax dipakai ULANG untuk objtab. Jadi `sp = objtab` datang
           TERAKHIR, bukan di antara id dan row. */
        id = dp->id;
        row = dp->row;
        found = 0;
        k = 0;
        sp = (struct slot *)objtab;
        /* Cast ke `char *` BUKAN kosmetik: hanya perubahan TIPE yang mematahkan
           CSE nilai. Dengan `sp->id != 0`, kompiler menganggap `sp->id` di sini
           dan di `if` bawah satu temp yang sama, lalu memakai ulang AX
           (spill "mov [bp],ax") — sedangkan biner MEMUAT ULANG "mov al,[si]".
           Bentuk `sp[0].id`, `(*sp).id`, dan `((struct slot *)sp)->id` semuanya
           TETAP di-CSE: teks beda tidak cukup, tipe harus beda. */
        while (*(char *)sp != 0) {
            if (sp->id == id && sp->row == row) {
                /* ⭐ LABEL TELANJANG (tak ada `goto` ke sini di seluruh berkas).
               Ia tidak memancarkan satu byte pun, tapi memaksa MC2 menutup
               blok dasar: semua simpanan tertunda di-COMMIT di sini, SI jadi
               bebas, dan `dp` masuk SI seperti aslinya -- bukan DI. Tanpa
               label ini `sp` masih dianggap menempati SI. 501/503 -> 503/503. */
blk1:
            dp->spr2 = q;
                t2 = load(objfh, objtab, k, q);
                if (t2 != sp->spr)
                    printf(0x1e1e);
                q = q + sp->spr;
                found = 1;
                break;
            }
            sp = sp + 1;
            k = k + 1;
        }
        if (found == 0)
            dp->spr2 = 0;
        j = j + 1;
    }
    return cnt - 1;
}

/* ⏳ BELUM COCOK — panjang SUDAH TEPAT 503, tinggal 2 byte di +407/+410.
 *
 * ⚠ DICOBA & GAGAL (2026-07-31, lewat sweep.py 16 varian):
 *   Situs 0x4fd4 (`mov di` vs `mov si` untuk `dp`) TERBUKTI soal LIVE-RANGE,
 *   bukan preferensi register: dalam reproduksi mini, memindahkan pemakaian
 *   terakhir `sp` ke SEBELUM simpanan `dp->spr2` langsung membebaskan SI.
 *   Tapi kedua bentuk yang mencapainya merusak byte lain:
 *     - `t2 = sp->spr;` sebelum simpanan  -> `sp->spr` tak lagi dimuat DUA kali
 *       sesudah panggilan seperti di biner
 *     - dua `if (...) goto next` menggantikan `if (A && B)` -> SI benar, TAPI
 *       kompiler MEMUAT ULANG `sp` di antara kedua `if` (+3 byte, 0x4fc7);
 *       GLOBAL 501 -> 490. Byte cabangnya sendiri identik.
 *   Juga tidak berpengaruh: `register` pada `sp` atau `dp`, urutan deklarasi
 *   `sp`/`dp`, tukar operan syarat, `(*dp).spr2`, `dp[0].spr2`, `for` dengan
 *   koma, `found = 1` dipindah ke atas.
 *
 * SUDAH TERBUKTI & JANGAN DIUBAH:
 *   - bingkai 26h: 3 temp (bp+0,2,4) + 16 lokal (bp+6..24h) dalam urutan
 *     dt, dp, sp, k, i, cnt, di, sidx, p, q, t1, id, row, found, j, t2
 *   - urutan penugasan awal `dt, p, q, cnt, i` (menentukan ax/bx/cx/dx)
 *   - urutan fase-3 `id, row, k, found, sp` — nol dimuat ke DX SEBELUM objtab
 *     dimuat ke AX; `found` disimpan sebelum `k`
 *   - syarat rantai fase-1: `sp->id == rectab[sidx].id && (sp->row ==
 *     rectab[sidx].row || sp->row + 100 == rectab[sidx].row)` — operan term-2
 *     TIDAK boleh dibalik (menentukan ax/bx)
 *   - `while (*(char *)sp != 0)` untuk mematahkan CSE (lihat komentar di atas)
 *
 * SISA 2 BYTE, di +407/+410:
 *     kita: mov di,[bp+8] / mov [di+8],ax     (dp lewat DI)
 *     asli: mov si,[bp+8] / mov [si+8],ax     (dp lewat SI)
 * Aslinya MENIMPA SI — jadi kompiler asli menganggap `sp` sudah tak ada di
 * register di titik itu, dan memuatnya ULANG di 0x4feb. Punya kita menahan `sp`
 * di SI (efek samping cast `char *`) sehingga penunjuk `dp` jatuh ke DI.
 *
 * SUDAH DICOBA & GAGAL (semua 503 byte, tetap 2 beda, kecuali disebut lain):
 *   - `(*dp).spr2 = q`                          -> sama
 *   - tukar term `if (sp->row == row && ...)`   -> 14 beda (lebih buruk)
 *   - `found = 1` dipindah ke atas badan        -> 50 beda
 *   - cast dipindah ke `if` saja                -> tetap 2 beda
 *   - `for(;;)` + `if (sp->id == 0) break`      -> 506 (jmp ekstra)
 *   - dua `if` terpisah + `goto next`           -> 505
 *   - `sp[0].id`, `(*sp).id`, `((struct slot *)sp)->id` di while -> 502 (CSE lagi)
 *   - `while (*(char *)sp)` tanpa `!= 0`        -> 500
 *   - `while (sp->id != 0 && 1)`                -> 510
 *
 *   - `sp` bertipe `char *` dari awal (fase 1 pakai sp[0..5], fase 3 pakai
 *     *sp dan cast struct untuk field +6) -> 504 byte, 386 beda. Ini MERUSAK
 *     fase 1 yang tadinya cocok sempurna, jadi tipe `struct slot *` untuk `sp`
 *     memang benar. Jangan diulang.
 *
 *   - cast DIPINDAH: `while (sp->id != 0)` + `if (*(char *)sp == id ...)`
 *     -> 503 byte, TETAP 2 beda di +407/+410 yang sama. Jadi POSISI cast
 *     tidak berpengaruh; yang menyandera SI adalah `sp` sebagai penunjuk
 *     hidup, bukan letak cast-nya.
 *
 * LANGKAH BERIKUT: cari pemicu lain yang memuat ulang `sp->id` tanpa mengubah
 * tipe aksesnya. Sisa 2 byte ini murni pilihan register, bukan bentuk logika —
 * kelas masalah yang sama dengan `drawpair` dulu (SI vs CX), dan itu akhirnya
 * terpecahkan lewat bentuk akses, bukan lewat menebak.
 */
