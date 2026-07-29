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
            if (k == 0 || (k & 0xff) != 0 || k == 0x4b00 || k == 0x4d00 ||
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

/* ⏳ BELUM COCOK — 223 byte vs 199 (24 KELEBIHAN), bingkai 8 vs 6.
 * SUDAH COCOK: pembukaan sampai +3, dan pola "while (avail() == 0);"
 * (hasil TIDAK ditampung variabel).
 * MASALAH: k jatuh di bp+6, aslinya bp+4 -> kita punya SATU slot temp lebih
 * banyak. Peta slot asli: c@bp+2 (char), d@bp+3 (char), k@bp+4 (int) --
 * dua char BERDAMPINGAN 1 byte.
 * SUDAH DICOBA & GAGAL: mengganti "char c, d;" dengan array "char cd[2]"
 * + #define -> tetap bingkai 8.
 * Dugaan: kondisi panjang "k == 0 || (k & 0xff) != 0 || k == 0x4b00 || ..."
 * menuntut dua temp. Aslinya: "test ax,ax; mov [k],ax; je keluar; and ax,0ffh"
 * -- yaitu k diuji nol DULU sebagai pernyataan terpisah, baru sisanya,
 * sehingga hanya satu nilai hidup. Coba pecah kondisinya jadi dua if.
 */
