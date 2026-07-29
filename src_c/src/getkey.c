/* FUN_1000_1814 @ 1000:1814, 199 byte — baca satu tombol (blocking), sudah
 * disaring dari tombol khusus.
 *
 * Loop luar: tunggu tombol; buang tombol-panah yang tidak dipakai; terjemahkan
 * lewat xlate() (735a). Tombol 'S'/'s' = saklar suara, ditelan lalu ulang.
 * Loop kedua: buang sisa tombol yang masih menumpuk di buffer, kecuali ESC.
 *
 *   avail()=7443, rdkey()=6853 (0x100 intip, 0 buang), xlate()=735a
 *   sndflag @0x83c
 *
 * SLOT dari disassembly: c@bp+2 (char), d@bp+3 (char), k@bp+4 (int).
 * Dua char BERDAMPINGAN 1 byte masing-masing -> dideklarasikan berurutan
 * sebelum int.
 */

extern unsigned sndflag;    /* @0x83c */

getkey()
{
    char c, d;
    int  k;

    for (;;) {
        for (;;) {
            while (avail() == 0)   /* hasil TIDAK ditampung: "test ax,ax; je" */
                ;
            k = rdkey(0x100);
            if (k == 0)          /* diuji SENDIRI dulu: "test ax,ax; mov [k],ax;
                                    je keluar" -- baru sisanya, supaya cuma satu
                                    nilai hidup dan satu slot temp terpakai */
                break;
            if ((k & 0xff) != 0 || k == 0x4b00 || k == 0x4d00 ||
                k == 0x4800 || k == 0x5000)
                break;
            rdkey(0);
        }
        c = xlate();
        if (c != 'S' && c != 's')
            break;
        sndflag ^= 1;
    }
    for (;;) {
        d = c;
        if (d == 0)
            break;
        if (rdkey(0x100) == 0)
            break;
        c = rdkey(0x100);
        if (c == 0) {
            rdkey(0);
            c = d;
        }
        else {
            c = xlate();
            if (c == 'S' || c == 's') {
                sndflag ^= 1;
                c = d;
            }
            else if (c != 0x1b)
                c = d;
        }
    }
    return d;
}

/* ⏳ BELUM COCOK — 218 byte vs 199, bingkai 8 vs 6.
 * SUDAH COCOK & JANGAN DIUBAH:
 *   - "while (avail() == 0);"  (hasil tidak ditampung)
 *   - "if (k == 0) break;" diuji SENDIRI sebelum kondisi sisanya
 *     (228 -> 223 -> 218)
 * MASALAH TERSISA: satu slot temp berlebih -> k jatuh di bp+6, aslinya bp+4.
 * Peta slot asli: c@bp+2 (char), d@bp+3 (char), k@bp+4 (int); dua char
 * BERDAMPINGAN 1 byte, jadi kompiler memang mem-pack char.
 * SUDAH DICOBA & GAGAL:
 *   - array "char cd[2]" + #define        -> bingkai tetap 8
 *   - memecah lagi kondisi kedua jadi dua -> 221 (lebih buruk)
 * Divergensi pertama TIDAK bergerak dari +3 selama dua perbaikan terakhir,
 * jadi masalahnya bukan di titik itu. Langkah berikut: telusuri di mana
 * slot kedua temp dipakai (cari store/reload yang tidak ada di biner),
 * bukan menebak bentuk kondisi lagi.
 */
