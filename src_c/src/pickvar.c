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
    char f0[2];         /* 08h  tak dipakai di biner */
    int  q;             /* 0Ah  = idx + 141h */
    char f1[10];        /* 0Ch..15h */
    int  k2;            /* 16h  salinan kedua list[idx] */
    char f2[2];         /* 18h */
    int  sel;           /* 1Ah  nilai balik, mulai -1 */
    char f3[2];         /* 1Ch */
    int  k;             /* 1Eh  = list[idx] */
    char f4[36];        /* 20h..43h */
    int  rb;            /* 44h  salinan recbase */
    char f5[2];         /* 46h */
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
                ((char *)recbase)[k * 0xc + 1])
            sel = 0;
    }
    return idx;
}

/* ⏳ DRAF — 231 dari 1.730 byte COCOK.
 *
 * TERVERIFIKASI byte-per-byte (0x42ca..0x43b0):
 *   - bingkai 52h dan SELURUH peta slot (lihat deklarasi, semuanya diukur)
 *   - pembuka, cabang lvl/tw, `if (n <= 0) return 0;`
 *   - KEDUA loop rnd (masing-masing SATU do-while dengan `||`)
 *   - `k = list[idx]; k2 = k; q = idx + 141h; sel = -1;`
 *   - uji `idx + 1 < n` (memakai DX, cocok)
 *
 * ⭐ PENGGANJAL TEMP SUDAH HABIS. Teknik ini yang membuat fungsi sebesar ini
 * bisa digarap bertahap: jumlah temp TUMBUH seiring badan ditulis, jadi selama
 * badan belum lengkap bingkai kurang dan SEMUA slot bergeser sehingga tak ada
 * divergensi yang bisa dibaca. `char tpad[]` menutup selisih itu dan
 * dikecilkan tiap kali menambah kode (6 -> 4 -> 0). Sekarang temp nyata persis
 * 4 slot. Kalau penambahan berikutnya membuat sub sp > 52h, itu tanda ada
 * ekspresi yang menuntut temp berlebih -- perbaiki ekspresinya, JANGAN
 * menambah pengganjal lagi.
 *
 * SUDAH DICOBA & GAGAL (urutan penugasan k/k2/q, semuanya diukur):
 *   - `q; sel; k; k2`        -> divergensi MUNDUR ke +193
 *   - `k2 = list[idx]; k = k2;`      -> +220 (store k2 keburu di-flush
 *                                       SEBELUM uji idx+1<n)
 *   - `k2 = list[idx]; k = list[idx];` -> +220 juga
 *   - `k = list[idx]; k2 = k;`       -> +231  <- TERBAIK, dipakai sekarang
 *
 * DIVERGENSI SEKARANG di +231, dan sisa bedanya TIGA hal terpisah:
 *   1. urutan flush: kita [16h] lalu [1Eh]; asli [1Eh] lalu [16h].
 *      Keempat urutan sumber di atas sudah dicoba; belum ada yang memberi
 *      urutan asli. Kemungkinan dipengaruhi kode SESUDAHNYA yang belum ditulis.
 *   2. asli menyimpan temp `[bp+2] = si` sesudah kedua store itu; kita belum.
 *   3. asli memakai bentuk "jl +3 / jmp jauh" karena badan `if` > 127 byte;
 *      kita masih "jge" pendek. Ini akan hilang sendiri begitu badannya
 *      ditulis -- JANGAN dikejar sekarang.
 *
 * Karena (3) menunjukkan bedanya akan berubah sendiri, langkah paling efisien
 * berikutnya BUKAN mengejar (1) melainkan menulis badan `if` dari 0x43f6.
 *
 * BELUM ditulis: 0x43f6 ke atas (~1.500 byte).
 */
