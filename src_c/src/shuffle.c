/* FUN_1000_2b34 @ 1000:2b34, 67 byte — animasi kocok: 32 kali pilih acak lalu gambar.
 *
 *   rnd()   = FUN_1000_5a5b (assembly)
 *   vbwait()  = FUN_1000_5d98
 *   put()   = FUN_1000_65e0
 *   curopt @0x522, ctx @0x524
 * Setelah loop, gambar sekali lagi dengan nilai tetap (curopt) — hasil akhir.
 */

extern int curopt;             /* @0x522 */
extern int ctx;             /* @0x524 */

shuffle()
{
    int k, i;

    for (i = 0; i < 0x20; i++) {
        k = rnd(2);
        vbwait();
        put(k, ctx);
    }
    put(curopt, ctx);
}
