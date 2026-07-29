/* FUN_1000_36ef @ 1000:36ef, 31 byte — kosongkan buffer keyboard.
 *
 * Baca tombol selama masih ada; berhenti kalau buffer habis ATAU ketemu ESC (0x1b).
 *   getkey()  = FUN_1000_1791
 *   eatkey()  = FUN_1000_1814
 *
 * Fungsi dipanggil TANPA prototype (K&R: semua fungsi dianggap balik int).
 *
 * Target byte:
 *   55  83 ec 02  8b ec        prolog
 *   e8 __ __      call getkey
 *   85 c0  74 0d                test ax,ax / je keluar
 *   e8 __ __      call getkey
 *   3d 1b 00  74 05            cmp ax,1bh / je keluar
 *   e8 __ __      call eatkey
 *   eb ec                       jmp ulang
 *   83 c4 02  5d  c3           epilog
 */

kbflush()
{
    while (getkey() != 0) {
        if (getkey() == 0x1b)
            break;
        eatkey();
    }
}
