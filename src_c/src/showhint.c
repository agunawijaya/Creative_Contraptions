/* FUN_1000_24bb @ 1000:24bb, 73 byte — tampilkan petunjuk (hanya di mode 4 / Mix Up).
 *
 *   mode @0x792, hintshown @0x848
 *   blit()  = FUN_1000_672f  (sprite @0x646 di x=0,y=0x6c, 8x0x68)
 *   text()  = FUN_1000_6453  (string @0xa26 di x=0x7c,y=0, skala 1x1, warna 3)
 */

extern int mode;            /* @0x792 */
extern int hintshown;       /* @0x848 */
extern char hintspr[];      /* @0x646 */
extern char hintstr[];      /* @0xa26 */

showhint()
{
    if (mode == 4) {
        hintshown = 1;
        blit(hintspr, 0, 0x6c, 8, 0x68);
        text(hintstr, 0x7c, 0, 1, 1, 3);
    }
}
