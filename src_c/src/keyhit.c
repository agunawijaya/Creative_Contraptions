/* FUN_1000_1791 @ 1000:1791, 131 byte — polling keyboard dgn penanganan tombol khusus.
 *
 *   avail() = FUN_1000_7443 ; rdkey() = FUN_1000_6853 (0x100 = intip, 0 = buang)
 *   togsnd() = FUN_1000_735a ; sndflag @0x83c
 *
 * Balikan: 0 = tak ada tombol, 1 = tombol panah / buffer kosong,
 *          selain itu = kode ASCII-nya. 'S'/'s' = saklar suara, ditelan di sini.
 *
 * KUNCI BENTUK: byte rendah TIDAK diambil dengan "k & 0xff" melainkan dengan
 * PENUGASAN KE VARIABEL char (`c = k;`). Cirinya di biner:
 *     mov byte ptr [bp+4], al      <- store 8 bit ke slot char
 *     mov word ptr [bp+2], ax      <- store 16 bit ke slot int
 * Menulis "c = k & 0xff" dengan c bertipe int menghasilkan kode yang lain.
 * Slot: k dideklarasikan pertama (bp+2), c kedua (bp+4).
 */

extern unsigned sndflag;    /* @0x83c */

keyhit()
{
    int k;
    char c;

    for (;;) {
        if (avail() == 0)
            return 0;
        k = rdkey(0x100);
        c = k;
        if (k == 0)
            return 1;
        if (c == 0) {
            if (k == 0x4b00 || k == 0x4d00 || k == 0x4800 || k == 0x5000)
                return 1;
            rdkey(0);
        }
        else {
            if (c != 0x53 && c != 0x73)
                return c;
            togsnd();
            sndflag ^= 1;
        }
    }
}

/* ⏳ BELUM COCOK — 137 byte vs 131 (6 kelebihan).
 * Asli memuat k SEKALI ke AX lalu membandingkan register:
 *     17d2  mov ax,[bp+2]
 *     17d5  cmp ax,4b00h / je ...   (3 byte per pembandingan)
 * Punya kita tampaknya membaca ulang dari memori tiap kali (5 byte per
 * pembandingan). Perlu bentuk yang memaksa k dimuat sekali — coba `switch (k)`
 * dengan case 0x4b00/0x4d00/0x4800/0x5000, atau tampung dulu ke variabel lain.
 */
