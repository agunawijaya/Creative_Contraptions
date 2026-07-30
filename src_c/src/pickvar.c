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
    int  cnt, rp2, rb, rp, unused1, unused2, unused3, unused4, unused5;

    rb = (int)recbase;
    if (lvl == 2)
        tw = 9;
    else
        tw = 0x12;
    if (n <= 0)
        return 0;
    if (idx < 0) {
        if (flag != 0) {
            cnt = 0;
            do {
                do {
                    idx = rnd(n);
                    cnt++;
                    rp = (int)recbase + list[idx] * 0xc;
                } while (((struct rec *)rp)->row > 100);
            } while (((struct rec *)rp)->id < 0x80 && cnt < 0x73);
        }
        else {
            do {
                do {
                    idx = rnd(n);
                    rp = (int)recbase + list[idx] * 0xc;
                } while (((struct rec *)rp)->row > 100);
            } while (((struct rec *)rp)->id >= 0x80);
        }
    }
    return idx;
}

/* ⏳ DRAF — 53 byte pertama COCOK, badan utama (~1.600 byte) belum ditulis.
 *
 * SUDAH TERVERIFIKASI (bukan dugaan):
 *   - bingkai `sub sp,52h` TEPAT
 *   - `rb` di bp+44h TEPAT
 *   - byte 0..53 cocok: pembuka, cabang lvl/tw, dan `if (n <= 0) return 0;`
 *
 * Cara mendapatkannya: `char pad0[26]` di depan + lima lokal tak terpakai di
 * belakang. Itu DIUKUR lewat aturan 8i (kompilasi, lihat selisih sub sp dan
 * posisi slot, sesuaikan), bukan diteorikan. Jangan mengubah jumlah pad tanpa
 * mengukur ulang -- seluruh 36 slot bergeser.
 *
 * BELUM ditulis: 0x4350 ke atas. Divergensi pertama sekarang di +54, yaitu
 * cabang `if (idx < 0)` dan dua loop rnd di bawahnya.
 *
 * PERINGATAN yang paling penting untuk siapa pun yang melanjutkan: pseudo-C
 * Ghidra untuk fungsi ini TIDAK BISA DIPERCAYA (9 blok tak-terjangkau, dan
 * satu syarat yang selalu benar). Kerjakan dari disassembly. Peta slot yang
 * masih kosong: bp+02..2Ch belum diketahui perannya sama sekali.
 */
