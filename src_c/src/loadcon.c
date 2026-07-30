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
        do {
            /* SATU pernyataan, bukan dua. Aturan 8 ("hasil panggilan ditampung
               variabel tersendiri") TIDAK berlaku di sini: biner memancarkan
               "call rnd / add ax,[first] / mov [pick],ax" -- satu store, bukan
               dua, dan AX tetap bebas untuk uji berikutnya. */
            pick = rnd(cnt) + first;
            if (lastgoal != sub)
                break;
            if (cnt < 2)
                break;
        } while (pick == lastvar);
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
    total = total + read(fh, recB, nmech * 6);
    total = total + read(fh, &nzany, 2);
    total = total + read(fh, recC, nzany * 6);
    total = total + read(fh, state, (nzany + nmech) * 2);
    expect = nmax * 4 + nmech * 6 + 6 + nzany * 6 + (nzany + nmech) * 2;
    if (total == expect) {
        nmechb = nmech;
        i = 0;
        zcnt = 0;
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

/* ⏳ BELUM COCOK — 729 dari 739 byte, bingkai 0x124 SUDAH TEPAT.
 *
 * Byte 0..223 COCOK PERSIS. Divergensi pertama di +224 lalu MENGKASKADE
 * sampai akhir (412 byte beda, tapi hanya SATU sebab).
 *
 * SEBABNYA SUDAH DIPERSEMPIT, bukan diduga:
 *   asli : add ax,[first] / mov [pick],ax / mov ax,[lastgoal] / cmp ax,[sub]
 *   kita : add ax,[first] / mov bx,[lastgoal] / cmp bx,[sub] / mov [pick],ax
 * Asli MENG-COMMIT store `pick` segera sehingga AX bebas dan pemuatan global
 * berikutnya memakai bentuk akumulator `a1` (3 byte). Kami MENUNDA store-nya,
 * jadi AX masih terpakai dan pemuatannya jatuh ke `8b 1e` (4 byte) lewat BX.
 * Semua beda sesudahnya adalah akibat pergeseran register ini.
 *
 * SUDAH DICOBA & GAGAL (ketiganya menghasilkan byte yang SAMA PERSIS,
 * jadi bentuk loop BUKAN pemicunya):
 *   1. do { pick = rnd(cnt) + first; if (lastgoal != sub || cnt < 2) break; }
 *      while (pick == lastvar);
 *   2. sama, tapi `||` dipecah jadi dua `if (...) break;`
 *   3. do { pick = rnd(cnt) + first; }
 *      while (lastgoal == sub && cnt >= 2 && pick == lastvar);
 *
 * Yang SUDAH terbukti benar dan jangan diubah lagi:
 *   - `pick = rnd(cnt) + first;` SATU pernyataan (dua pernyataan memberi DUA
 *     store: satu di +220 dan satu tertunda di +236)
 *   - struktur `goto done` ke ekor bersama, bukan blok bersarang -- itu yang
 *     memberi "cmp word ptr [cnt],0" dan memutus CSE `cnt` (menutup +169)
 *   - `cnt = cnt + 1; if (cnt == 1)` bukan `cnt++` (menutup +147)
 *   - urutan "cnt = 0; i = 0;" (store terbalik, menutup +81/+85)
 *   - entri directory { int id; long off; } = 6 byte, lseek 3 argumen
 *
 * LANGKAH BERIKUT yang belum dicoba: cari apa yang memaksa kompiler
 * meng-commit store tertunda. Tulis PROBE kecil (lihat README §"Teknik: pakai
 * PROBE") berisi `v = f(x) + g;` diikuti uji atas global, dengan beberapa
 * varian bentuk penugasan -- JANGAN iterasi fungsi 739 byte ini lagi.
 */
