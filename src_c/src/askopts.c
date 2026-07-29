/* FUN_1000_31da @ 1000:31da, 225 byte — dua pertanyaan Y/N berurutan.
 *
 * Pertanyaan 1 (tabel @0x1ad2): set `cur` lalu gambar pilihan.
 * Pertanyaan 2 (tabel @0x1af6): set `sndflag` (saklar suara).
 * ESC di salah satunya membatalkan (balikan -1); selesai -> balikan 1.
 *
 *   drawtab()=3769, show()=381a, kbflush()=36ef (sudah direkonstruksi)
 *   keyhit()=1791, getkey()=1814, tone2()=3734 (sudah direkonstruksi)
 *   put()=65e0 ; cur @0x522, ctx @0x524, sndflag @0x83c
 *
 * BENTUK: tiap pertanyaan = loop tak-berujung berisi `switch`, dan case yang
 * cocok MELOMPAT KELUAR loop (goto), bukan `break` -- sebab `break` di dalam
 * switch hanya keluar dari switch lalu mengulang loop. Di biner terlihat
 * sebagai "jmp" ke kode sesudah rantai dispatch, sementara default jatuh ke
 * "jmp" balik ke awal loop.
 * Urutan case Y,y,N,n,ESC -> rantai pembanding di tabel muncul TERBALIK
 * (1bh, 6eh, 4eh, 79h, 59h), sesuai aturan urutan case.
 */

extern int  cur;            /* @0x522 */
extern int  ctx;            /* @0x524 */
extern int  sndflag;        /* @0x83c */
extern char t1[];           /* @0x1ad2 */
extern char t2[];           /* @0x1af6 */

askopts()
{
    char pad[2];         /* bingkai asli 4, kita 2. Lokal int tak-terpakai
                            DIBUANG kompiler di sini; array selalu dialokasikan. */

    drawtab(t1, 3);
    kbflush();
    for (;;) {
        while (keyhit() == 0)
            ;
        switch (getkey()) {
        case 'Y':
        case 'y':
            cur = 1;
            goto q2;
        case 'N':
        case 'n':
            cur = 0;
            goto q2;
        case 0x1b:
            return -1;
        default:
            break;          /* default EKSPLISIT: memunculkan lompatan balik
                               (eb da) sebelum tabel, seperti di biner */
        }
    }
q2:
    tone2();
    put(cur, ctx);
    show(t2, 2);
    kbflush();
    for (;;) {
        while (keyhit() == 0)
            ;
        switch (getkey()) {
        case 'Y':
        case 'y':
            sndflag = 1;
            goto done;
        case 'N':
        case 'n':
            sndflag = 0;
            goto done;
        case 0x1b:
            return -1;
        default:
            break;          /* default EKSPLISIT: memunculkan lompatan balik
                               (eb da) sebelum tabel, seperti di biner */
        }
    }
done:
    tone2();
    return 1;
}
