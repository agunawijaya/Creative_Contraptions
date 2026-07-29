/* FUN_1000_4c04 @ 1000:4c04, 208 byte — gambar/isi ulang bilah waktu (mode Mix Up).
 *
 * Selama tx masih di dalam layar: gambar bagian terpakai (warna 2) dan sisanya
 * dikosongkan. Kalau tx sudah lewat kanan (waktu habis): bunyikan nada lalu isi
 * bilah dari kiri ke kanan 8 piksel sekaligus sebagai animasi habis-waktu.
 *
 *   mode @0x792, tx @0x7ee, goal @0x718, sub @0x3b2
 *   snd[] = deskriptor nada di STACK (3 word), alamatnya dipasang ke sndptr
 *   sndoff()=5a74, sndon()=5a76, delay()=2692 (sudah direkonstruksi)
 */

extern int  mode;           /* @0x792 */
extern int  tx;             /* @0x7ee */
extern int  goal;           /* @0x718 */
extern int  sub;            /* @0x3b2 */
extern int  sndmode;        /* @0x722 */
extern int *sndptr;         /* @0x720 */

timedrw()
{
    int i;
    int snd[3];

    if (mode != 4)
        return;                  /* RETURN AWAL, bukan membungkus dgn if(mode==4) --
                                    aslinya "je +5; add sp,0ah; pop bp; ret" */
    {
        if (tx < 0x140 && (goal != 6 || sub != 1)) {
            if (tx >= 0) {
                fillrect(0, 0xa2, tx, 0xa5, 2);
                fillrect(tx, 0xa2, 0x13f, 0xa5, 0);
            }
        }
        else {
            sndoff();
            snd[0] = 500;
            snd[1] = 0x474;
            snd[2] = 0x10;
            sndptr = snd;    /* alamat dimuat DULU (aturan 8d) */
            sndmode = 1;
            sndon();
            for (i = 0; i < 0x140; i = i + 8) {
                fillrect(i, 0xa2, i + 7, 0xa5, 2);
                delay(1);
            }
            sndoff();
            sndptr = snd;
            sndmode = 0;
            sndon();
        }
    }
}

/* ⏳ BELUM COCOK — 206 byte vs 208 (2 KURANG).
 * SUDAH DICOBA & GAGAL: menambah lokal tak terpakai (dihapus kompiler),
 * "i = i + 8" sbg ganti "i += 8" (tak berpengaruh).
 * Kurang tepat 2 byte = satu instruksi kecil; periksa bentuk penugasan
 * snd[] atau uji "goal != 6 || sub != 1".
 */
