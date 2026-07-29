/* FUN_1000_4cd4 @ 1000:4cd4, 301 byte — pindahkan penanda huruf bantuan
 * (hanya mode Mix Up, level Master Builder).
 *
 * Tiap kali pewaktu habis (atau bilah waktu tepat di batas), penanda huruf
 * dipindah ke posisi acak baru: huruf lama dihapus dengan menggambar ulang
 * warna 3, huruf baru digambar dengan warna 2 atau 0 tergantung sisa waktu.
 *
 *   mode @0x792, lvl @0x734, timer @0x7f2, tx @0x7ee, best @0x82e,
 *   cur2 @0x7f8, lvl6 @0x7f6, nmax @0x3b4, range @0x830, mflag @0x834
 *   postab[] @0x3b6 = pasangan (a,b) per posisi, stride 4 byte
 *   rnd()=5a5b, step()=5d98, text()=6453, pickmax()=4e01 (sudah direkonstruksi)
 *
 * SLOT dari disassembly: bp+4,6,8,0ah,0ch,0eh,10h; bingkai 12h (2 slot temp).
 * `buf` dipakai sebagai string 2 karakter (huruf + NUL) lewat &buf.
 */

extern int mode;            /* @0x792 */
extern int lvl;             /* @0x734 */
extern int timer;           /* @0x7f2 */
extern int tx;              /* @0x7ee */
extern int best;            /* @0x82e */
extern int cur2;            /* @0x7f8 */
extern int lvl6;            /* @0x7f6 */
extern int nmax;            /* @0x3b4 */
extern int range;           /* @0x830 */
extern int mflag;           /* @0x834 */

struct pos {
    int a;
    int b;
};
extern struct pos postab[];  /* @0x3b6 */

hintmark()
{
    /* TUJUH slot, sesuai biner: prev@bp+4, nb@6, na@8, ob@0ah, oa@0ch,
       buf@0eh, col@10h. Jumlah acak TIDAK ditampung variabel -- kompiler
       menahannya di register, jadi ujinya ditulis lewat cur2 yang sudah
       disimpan (r2-1 == cur2+1). */
    int prev, na, nb, oa, ob, buf, col;

    /* SATU if dengan "||" lalu return: menghasilkan SATU epilog yang dipakai
       kedua uji (jne -> epilog, je -> badan). Bentuk "&&" membungkus badan
       memberi "je +3; jmp jauh"; dua return awal memberi epilog GANDA. */
    if (mode != 4 || lvl != 2)
        return;
    {
        if (timer <= 0 || tx == best) {   /* cmp 0/jle, bukan cmp 1/jl */
            prev = cur2;
            timer = 0x3c;
            if (lvl6 > 0)
                lvl6 = lvl6 - 1;
            cur2 = lvl6 + rnd(3) + rnd(3) - 2;
            if (cur2 < 0 || cur2 >= nmax)   /* uji tanda langsung (jl),
                                               bukan inc+cmp 1 */
                cur2 = lvl6;
            na = postab[cur2].a;
            nb = postab[cur2].b;
            oa = postab[prev].a;
            ob = postab[prev].b;
            step();
            if (prev <= nmax) {
                buf = prev + 0x41;
                text(&buf, ob, oa, 1, 1, 3);
            }
            col = 2;
            if (tx >= range)   /* tx di KIRI: cmp ax,[range] lalu jl */
                col = 0;
            if (tx == best) {
                col = 0;
                pickmax();
            }
            buf = cur2 + 0x41;
            text(&buf, nb, na, 1, 1, col);
            if (col == 0)
                mflag = 1;
            else
                mflag = 0;
        }
    }
}

/* ⏳ BELUM COCOK — 319 byte vs 301, bingkai 14h vs 12h (satu slot berlebih).
 * Perjalanan: 323 -> 319 (mengurangi lokal dari 10 jadi 8).
 * SUDAH TERBUKTI:
 *   - bentuk gabungan "if (mode == 4 && lvl == 2)" BENAR; menulisnya sebagai
 *     dua "return" awal memberi epilog GANDA (lebih panjang)
 *   - biner hanya punya TUJUH slot lokal (bp+4,6,8,0ah,0ch,0eh,10h);
 *     kita masih delapan
 *   - postab sebagai array STRUCT (stride 4) sudah benar
 * Langkah berikut: telusuri bp+4..10h di disassembly untuk memastikan variabel
 * mana yang menempatinya, lalu buang satu lokal kita yang sebenarnya register
 * (kandidat: `prev`, atau salah satu dari na/nb/oa/ob).
 */
