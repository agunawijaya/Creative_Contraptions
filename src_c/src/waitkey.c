/* FUN_1000_58c9 @ 1000:58c9, 72 byte — tunggu tombol keputusan.
 *
 *   getkey() = FUN_1000_1814
 *   failed @0x842 = penanda contraption gagal
 *   Balikan: 0x20 = ENTER saat belum gagal, 0 = SPACE, -1 = ESC.
 *
 * DUA CIRI BENTUK YANG MENENTUKAN:
 * 1. `switch (getkey())`, BUKAN rantai if/else-if. Cirinya di biner: badan tiap
 *    case ditaruh LEBIH DULU, lalu "jmp" ke rantai pembanding di BAWAH
 *    ("cmp ax,0dh / je ..."). Rantai if/else menempatkan uji di depan.
 * 2. Hasil getkey() TIDAK ditampung variabel — nilainya tetap di AX. Memberinya
 *    nama lokal menambah slot bingkai (sub sp,6 bukan 4) dan mengubah tiap
 *    pembandingan jadi akses memori (83 7e 04 .. bukan 3d ..).
 *    Ini PENGECUALIAN dari aturan 8: yang di-switch tidak ditampung.
 * 3. URUTAN case = urutan badan case di biner. Rantai pembandingnya muncul
 *    TERBALIK dari urutan sumber. Di sini badan pertama adalah 'return 0'
 *    (case 0x20), jadi 0x20 harus ditulis PALING ATAS.
 *
 * `done` di-nol-kan dan tak pernah diubah; keluar hanya lewat return. Uji loop
 * ada di bawah -> do..while.
 */

extern int failed;          /* @0x842 */

waitkey()
{
    int done;

    done = 0;
    do {
        switch (getkey()) {
        case 0x20:
            return 0;
        case 0x1b:
            return -1;
        case 0x0d:
            if (failed == 0)
                return 0x20;
            break;
        }
    } while (done == 0);
}
