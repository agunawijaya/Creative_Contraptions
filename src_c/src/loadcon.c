/* FUN_1000_5035 @ 1000:5035, 739 byte — LOADER berkas CONTRAP.
 *
 * Buka CONTRAP, baca directory 216 byte, cari semua entri ber-id == `sub`
 * (goal yang sedang dipilih), lalu pilih SATU varian: nomor yang diminta
 * pemanggil, atau acak kalau -1. Pemilihan acak menghindari varian yang sama
 * dengan pemanggilan sebelumnya (lastgoal/lastvar), tapi hanya kalau goal-nya
 * sama DAN memang ada >= 2 varian.
 *
 * Sesudah itu lseek ke offset varian dan baca blob contraption ke DGROUP
 * sepotong demi sepotong. Jumlah byte yang benar-benar terbaca dijumlahkan dan
 * dibandingkan dengan yang seharusnya; kalau tidak cocok, berkasnya dianggap
 * rusak dan fungsi mengembalikan -1.
 *
 * Struktur berkas SUDAH TERVALIDASI di CODE_MAP.md §"Format file CONTRAP"
 * (keenam goal parse dengan checksum cocok), jadi maknanya tidak ditebak.
 *
 *   open()=6b57  read()=6d31  lseek()=6e8b  close()=6fb6  printf()=6a48
 *   (semuanya dari MC.LIB)  rnd()=5a5b
 *
 * ⭐ ENTRI DIRECTORY = { int id; long off; } = 6 BYTE, bukan tiga int.
 * Buktinya di pemanggilan lseek: dua kata didorong sebagai SATU argumen
 * (push [bp+si+0ah] lalu push [bp+si+8]) dan mode-nya `0` di paling akhir —
 * yaitu lseek(fh, off, 0) dengan 3 argumen, sama seperti loadarc.c. Kalau
 * dibaca sebagai tiga int, argumennya jadi empat dan panjangnya meleset.
 *
 * PETA SLOT (bingkai 0x124 = 292): bp+0..4 = 3 TEMP, lalu
 *   bp+6      dir[36]   (216 byte, 6..0ddh)
 *   bp+0deh   i
 *   bp+0e0h,0e2h  TIDAK PERNAH DIREFERENSI
 *   bp+0e4h   fh
 *   bp+0e6h   off       (long, 4 byte)
 *   bp+0eah   gid
 *   bp+0ech   cnt   0eeh=first  0f0h=pick  0f2h=total  0f4h=expect
 *   bp+0f6h..123h  46 BYTE TIDAK PERNAH DIREFERENSI
 * Argumen: bp+128h = want (-1 = pilih acak).
 *
 * 50 byte yang tak pernah direferensi (4 + 46) diselesaikan SECARA EMPIRIS
 * lewat aturan 8i: kompilasi, lihat selisih `sub sp`, tambah lokal. Array
 * dipakai sebagai pengganjal karena `int` tak terpakai kadang dibuang
 * kompiler sedangkan array selalu dialokasikan.
 */

struct pos {
    int a;
    int b;
};                          /* = 4 byte, stride postab */

struct ent {
    int  id;                /* +0 */
    long off;               /* +2 */
};                          /* = 6 byte */

extern int sub;             /* @0x3b2 */
extern int nmax;            /* @0x3b4 */
extern int nmech;           /* @0x3ac */
extern int nzany;           /* @0x4b4 */
extern struct pos postab[]; /* @0x3b6 -- SUDAH bernama di hintmark.c;
                               jangan beri nama kedua, gendata.py akan
                               memancarkan array berukuran NOL. */
extern int recB[];          /* @0x41e */
extern int recC[];          /* @0x4b6 */
extern int state[];         /* @0x4f2 */
extern int ids[];           /* @0x3f2 */
extern int zflag[];         /* @0x796 */
extern int fail[];          /* @0x7be */
extern int nmechb;          /* @0x41a */
extern int nmechc;          /* @0x41c */
extern int zcnt;            /* @0x7e6 */
extern int lastgoal;        /* @0x1e2e */
extern int lastvar;         /* @0x1e30 */

loadcon(want)
int want;
{
    struct ent dir[36];
    int  i;
    char pad1[4];
    int  fh;
    long off;
    int  gid, cnt, first, pick, total, expect;
    char pad2[46];

    fh = open(0x1e3d, 0x8004);
    if (fh == -1) {
        printf(0x1e45);
        return -1;
    }
    if (read(fh, dir, 0xd8) == -1) {
        printf(0x1e45);
        goto done;
    }
    cnt = 0;
    i = 0;
    while (i < 0x24 && dir[i].id <= sub && dir[i].id != 0) {
        if (dir[i].id == sub) {
            /* BUKAN `cnt++`: itu memberi "inc word ptr [cnt]". Biner memuat
               cnt ke AX, inc, store, lalu menguji nilai BARU yang masih di AX
               -- `dec ax; jne` sebagai bentuk `== 1`. */
            cnt = cnt + 1;
            if (cnt == 1)
                first = i;
        }
        i++;
    }
    /* `goto done`, BUKAN blok bersarang `if (cnt != 0) { ... }`. Bedanya
       kelihatan: bentuk goto memberi "cmp word ptr [cnt],0" dan MEMUAT ULANG
       cnt untuk uji berikutnya; bentuk blok menahannya di AX sehingga uji
       berikutnya jadi "cmp bx,ax". Sesuai temuan probes/probe9.c: `goto`
       tidak memelihara nilai di register. */
    if (cnt == 0)
        goto done;
    if (want > cnt) {
        printf(0x1e45);
        want = -1;
    }
    if (want == -1) {
        /* SATU pernyataan, bukan dua ("call rnd / add ax,[first] /
           mov [pick],ax" -- satu store).
           ⭐ Ketiga syaratnya ada di SATU `while (&& &&)`, BUKAN dua `break`
           di dalam badan. Bentuk `break` membuat kompiler MENUNDA simpanan
           `pick` melewati pemuatan `lastgoal`, sehingga globalnya masuk BX
           (8b 1e, 4 byte) dan bukan AX (a1, 3 byte) -- selisih 1 byte yang
           menggeser seluruh sisa fungsi. Dengan `&&` badan gelungnya kosong,
           simpanan ter-commit lebih dulu dan AX bebas. */
        do {
            pick = rnd(cnt) + first;
        } while (lastgoal == sub && cnt >= 2 && pick == lastvar);
        lastgoal = sub;
        lastvar = pick;
    }
    else
        pick = want + first;
    off = dir[pick].off;
    if (lseek(fh, off, 0) < 0)
        goto done;
    read(fh, &gid, 2);
    if (gid != sub) {
        printf(0x1e45);
        goto done;
    }
    total = read(fh, &nmax, 2);
    total = total + read(fh, postab, nmax << 2);
    total = total + read(fh, &nmech, 2);
    nmechc = nmech;
    /* `* 3 * 2` (3 kata per record x 2 byte), BUKAN `* 6`: biner
       memancarkan "mov bx,3 / imul bx / shl ax,1", sedangkan `* 6`
       memberi "mov bx,6 / imul bx" -- 2 byte lebih pendek. */
    total = total + read(fh, recB, nmech * 3 * 2);
    total = total + read(fh, &nzany, 2);
    total = total + read(fh, recC, nzany * 3 * 2);
    total = total + read(fh, state, (nzany + nmech) * 2);
    /* Konstanta 2 ditulis TERPISAH di depan tiap bagian (ukuran kata pencacah
       masing-masing), bukan digabung jadi `+ 6`. Kompiler melipat dua yang
       pertama jadi "add cx,4" lalu memancarkan yang ketiga sebagai
       "inc cx; inc cx" -- jadi urutannya terbaca langsung dari biner. */
    expect = 2 + nmax * 4 + 2 + nmech * 3 * 2 + 2 + nzany * 3 * 2 +
             (nzany + nmech) * 2;
    /* ⚠ SUDAH DICOBA & GAGAL: menukar jadi `(nmech + nzany) * 2` karena
       fixorder melaporkan beda simbol di +587 (kita nmech, asli nzany).
       Hasilnya GLOBAL 687 -> 682 dan BEDA simbol malah 1 -> 2. Jadi laporan
       beda itu ARTEFAK wilayah yang belum sejajar di sekitar 0x527E, bukan
       kesalahan operan. */
    if (total == expect) {
        /* ⭐ LABEL TELANJANG: ia menutup blok dasar sehingga cache register
           MC2 dibuang di sini. Tanpa itu kompiler meng-CSE `nmech` (karena
           dipakai lagi di sini) dan MEMUATNYA DULUAN di `expect`, sehingga
           `(nzany + nmech)` terpancar sebagai `mov ax,[nmech]/add ax,[nzany]`
           -- byte-nya cocok tapi SIMBOLNYA TERTUKAR dengan asli. Dengan label
           ini `nzany` dimuat lebih dulu dan `nmech` DIMUAT ULANG di sini,
           persis biner asli. Tidak memancarkan satu byte pun. */
blk1:
        nmechb = nmech;
        /* Urutan TERBALIK dari urutan simpanan di biner (i lalu zcnt): untuk
           penugasan nol berturut yang berbagi satu register, simpanannya
           dipancarkan kebalikan urutan sumber. */
        zcnt = 0;
        i = 0;
        for (; i < nzany; i++)
            zflag[i] = 0;
        for (i = 0; i < nmech; i++) {
            fail[i] = 0;
            ids[i] = recB[i * 3 + 2];
        }
        close(fh);
        return 1;
    }
done:
    close(fh);
    return -1;
}

/* ⏳ BELUM COCOK — PANJANG SUDAH TEPAT 739/739, bingkai 0x124 juga tepat.
 *
 * Byte 0..223 dan 624..738 COCOK PERSIS. Seluruh sisa (321 byte, rentang
 * 224..623) adalah SATU kaskade dari satu keputusan register.
 *
 * SEBAB — sudah dipersempit sampai satu instruksi:
 *   asli : add ax,[first] / mov [pick],ax / mov ax,[lastgoal] / cmp ax,[sub]
 *   kita : add ax,[first] / mov bx,[lastgoal] / cmp bx,[sub] / mov [pick],ax
 * Asli MENG-COMMIT store `pick` segera sehingga AX bebas dan pemuatan global
 * berikutnya memakai bentuk akumulator `a1` (3 byte). Kita MENUNDA store-nya,
 * jadi AX terpakai dan pemuatannya jatuh ke `8b 1e` lewat BX (4 byte).
 *
 * HIPOTESIS YANG SUDAH DIGUGURKAN LEWAT PROBE (probes/probe11..13.c).
 * Ketiga probe mereproduksi bentuk sumber ini dan SEMUA VARIAN-nya
 * memancarkan perilaku yang BENAR (store di-commit segera). Jadi yang berikut
 * TERBUKTI BUKAN pemicunya — jangan diulang:
 *   probe11 (6 varian) : bentuk penugasan `pick = rnd(cnt) + first`,
 *                        urutan operan penjumlahan, hasil panggilan ditampung
 *                        variabel sendiri, `first` disalin ke lokal lain,
 *                        syarat pertama memakai lokal, pick dipakai sesudah loop
 *   probe12 (2 varian) : UKURAN BINGKAI / lebar displacement (bp+0ah vs bp+0deh)
 *   probe13 (2 varian) : konteks `if (want == -1) { ... } else pick = ...`
 * Sebelumnya juga digugurkan langsung di fungsi ini (ketiganya memberi byte
 * SAMA PERSIS): `if (...) break` dengan `||`, dengan dua `if` terpisah, dan
 * `do {} while (&& && )`.
 *
 * Yang SUDAH terbukti benar — jangan diubah:
 *   - entri directory { int id; long off; } = 6 byte -> lseek 3 argumen
 *   - `goto done` ke ekor bersama (memutus CSE `cnt`, menutup +169)
 *   - `cnt = cnt + 1; if (cnt == 1)` bukan `cnt++` (menutup +147)
 *   - urutan "cnt = 0; i = 0;" (menutup +81/+85)
 *   - `pick = rnd(cnt) + first;` SATU pernyataan (menutup +220)
 *   - `nmech * 3 * 2`, bukan `* 6` (imul 3 + shl, menutup +443)
 *   - konstanta di `expect` ditulis `2 + ... + 2 + ... + 2 + ...`, bukan `+ 6`
 *     (kompiler melipat dua yang pertama jadi "add cx,4", yang ketiga jadi
 *      "inc cx; inc cx") -- inilah yang menutup 6 byte terakhir
 *
 * BISECT SUDAH DIJALANKAN (~15 kompilasi) — DAN HASILNYA TIDAK SAH.
 * Semua varian potong yang berperilaku BENAR ternyata punya `pick` di bp+0ech,
 * sedangkan yang SALAH punya `pick` di bp+0f0h. Sebabnya: memotong ekor
 * membuat `total`/`expect` (dan/atau `pad1`) mati sehingga kompiler
 * MEMBUANGNYA dan seluruh tata letak bingkai bergeser 4 byte. Jadi varian
 * "benar" itu bukan kontrol yang sebanding — jangan percayai daftar di bawah
 * sebagai bukti bahwa blok-blok itu tidak bersalah:
 *     open+read+loop pencarian+if(cnt==0)+if(want>cnt)+if/else+off/lseek
 *     +read(&gid) semuanya "benar" TAPI dengan bingkai yang salah.
 *
 * ⚠ PELAJARAN UMUM (berlaku untuk bisect fungsi apa pun): memotong kode
 * MENGUBAH ALOKASI LOKAL karena kompiler membuang lokal yang jadi mati.
 * Sebelum menyimpulkan apa pun dari varian potong, PERIKSA DULU bahwa slot
 * bp-nya masih sama dengan fungsi utuh. Cara aman: ganti blok yang dibuang
 * dengan pemakaian palsu atas lokal yang sama, bukan menghapusnya.
 *
 * LANGKAH BERIKUT: ulangi bisect dengan slot DIPERTAHANKAN — mis. ganti tiap
 * blok yang dibuang dengan `total = expect = gid = 0;` supaya semua lokal
 * tetap hidup dan bingkai tetap 0x124. Baru varian-variannya sebanding.
 */
