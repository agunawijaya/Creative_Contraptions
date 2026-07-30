/* FUN_1000_36ef @ 1000:36ef, 31 byte — kosongkan buffer keyboard.
 *
 * Baca tombol selama masih ada; berhenti kalau buffer habis ATAU ketemu ESC (0x1b).
 *   keyhit()  = FUN_1000_1791 (polling, 0 = tak ada tombol)
 *   getkey()  = FUN_1000_1814 (blocking, sudah disaring)
 *
 * CATATAN NAMA: dulu di berkas ini 0x1791 disebut `getkey` dan 0x1814 disebut
 * `eatkey` -- KELIRU, dan sempat membuat `eatkey` jadi stub padahal 0x1814 sudah
 * direkonstruksi sebagai getkey.c.
 *
 * Fungsi dipanggil TANPA prototype (K&R: semua fungsi dianggap balik int).
 *
 * Target byte:
 *   55  83 ec 02  8b ec        prolog
 *   e8 __ __      call keyhit
 *   85 c0  74 0d                test ax,ax / je keluar
 *   e8 __ __      call keyhit
 *   3d 1b 00  74 05            cmp ax,1bh / je keluar
 *   e8 __ __      call getkey
 *   eb ec                       jmp ulang
 *   83 c4 02  5d  c3           epilog
 */

kbflush()
{
    while (keyhit() != 0) {
        if (keyhit() == 0x1b)
            break;
        getkey();
    }
}
