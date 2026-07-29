/* FUN_1000_312a @ 1000:312a, 134 byte — layar teks bertahap lalu tunggu ENTER/ESC.
 *
 *   setsel() = FUN_1000_3769 ; show() = FUN_1000_381a ; pause() = FUN_1000_31b0
 *   kbflush() = FUN_1000_36ef (sudah direkonstruksi)
 *   keyhit() = FUN_1000_1791 ; getkey() = FUN_1000_1814
 *   Balikan: 1 = ENTER, -1 = ESC.
 *
 * getkey() dibandingkan sebagai CHAR (Ghidra: cVar1), jadi penampungnya char —
 * itu yang memunculkan pemotongan ke 8 bit di biner.
 */

extern char t1[];           /* @0x1a2a */
extern char t2[];           /* @0x1a42 */
extern char t3[];           /* @0x1a5a */
extern char t4[];           /* @0x1a72 */

credits()
{
    char c;

    setsel(t1, 2);
    pause(100);
    show(t2, 2);
    pause(100);
    show(t3, 2);
    pause(100);
    show(t4, 1);
    kbflush();
    for (;;) {
        while (keyhit() == 0)     /* hasil TIDAK ditampung: aslinya
                                     "call 1791; test ax,ax; je ulang" */
            ;
        c = getkey();
        if (c == '\r')            /* langsung return, BUKAN break: aslinya
                                     "mov ax,1; ret" tepat di dalam cabang */
            return 1;
        if (c == '\033')
            return -1;
    }
}
