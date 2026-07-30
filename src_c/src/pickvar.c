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
    char pad0[26];      /* diukur, bukan ditebak: tanpa ini `rb` jatuh di
                           bp+2ch padahal biner memakai bp+44h */
    int  a, b, c, d, e, f, g, h2, i, j, k, m;
    int  x1, y1, x2, y2, w2, h3;
    /* URUTAN EKOR DIUKUR, bukan ditebak (aturan 8i). Biner memakai
       rb@44h, cnt@48h, rp@4Ch -- jadi harus ada slot pengganjal di antaranya. */
    int  t1, t2, rb, t3, cnt, t4;
    struct rec *rp;
    int  t5, t6;

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
    return idx;
}

/* ⏳ DRAF — 193 dari 1.730 byte COCOK. Badan utama belum ditulis.
 *
 * TERVERIFIKASI byte-per-byte (0x42ca..0x438a):
 *   - bingkai `sub sp,52h`, `rb`@bp+44h, `cnt`@bp+48h, `rp`@bp+4Ch
 *   - pembuka, cabang lvl/tw, `if (n <= 0) return 0;`
 *   - KEDUA loop rnd: masing-masing SATU do-while dengan `||`, bukan dua loop
 *     bersarang (kedua syarat melompat ke ATAS loop yang sama):
 *         flag != 0 : while (rp->row > 100 || (rp->id < 80h && cnt < 73h))
 *         flag == 0 : while (rp->row > 100 || rp->id >= 80h)
 *
 * PETA SLOT yang sudah diukur dari disassembly 0x4388 ke atas -- pakai ini,
 * JANGAN menambah lokal di belakang (itu memperbesar bingkai jadi 0x5c):
 *     bp+00,02,04,06  TEMP (dipakai untuk row-100 dsb.)
 *     bp+0Ah  q     = idx + 141h   <- INI yang Ghidra rusak jadi
 *                                     `if (param_7 + 0x141 != param_7)`
 *     bp+16h  k2    = list[idx]  (salinan kedua)
 *     bp+1Ah  sel   = -1  (nilai balik awal)
 *     bp+1Eh  k     = list[idx]
 *     bp+44h  rb    bp+48h  cnt    bp+4Ch  rp
 *
 * LANGKAH BERIKUT: susun ulang deklarasi supaya q/k2/sel/k jatuh di slot di
 * atas (ganti pengganjal, bukan menambah), lalu tulis blok
 * `if (idx + 1 < n) { if (recbase[list[idx+1]].row - 100 == recbase[k].row) ...`
 * yang mulai di 0x43bd. Perkaliannya: `0xc * list[idx+1]` (konstanta di KIRI,
 * operan memori) tapi `k * 0xc` (nilai di kiri) -- ikuti biner, jangan
 * diseragamkan.
 */
