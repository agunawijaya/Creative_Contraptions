/* Probe #8 — apa yang membuat MS C 1.04 memancarkan back-edge loop SEBAGAI
 * "jmp" TERSENDIRI di ujung switch, bukan melipatnya ke jump default?
 *
 * Pola asli (runmenu @0x36bd):
 *     ... badan case terakhir: mov ax,-1 / add sp,N / pop bp / ret
 *     36bd  e9 76 fe        jmp loop_top      <- INI yang belum bisa ditiru
 *     36c0  <tabel switch>
 *     36d8  <loop pencari>  ... e9 47 fe      jmp loop_top   (default)
 *
 * Rekonstruksi kami memancarkan hanya jump default; jmp di 36bd hilang.
 * Lima varian di bawah masing-masing menguji satu hipotesis.
 */

/* v1: seperti rekonstruksi sekarang — case terakhir `return`, tanpa default */
v1(k, a)
int k, a;
{
    for (;;) {
        switch (k) {
        case 0x38:  a = a - 1; break;
        case 0x32:  a = a + 1; break;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        }
    }
}

/* v2: ada `default:` kosong */
v2(k, a)
int k, a;
{
    for (;;) {
        switch (k) {
        case 0x38:  a = a - 1; break;
        case 0x32:  a = a + 1; break;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        default:    break;
        }
    }
}

/* v3: badan case memakai `continue`, bukan `break` */
v3(k, a)
int k, a;
{
    for (;;) {
        switch (k) {
        case 0x38:  a = a - 1; continue;
        case 0x32:  a = a + 1; continue;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        }
    }
}

/* v4: loop ditulis `while (1)` */
v4(k, a)
int k, a;
{
    while (1) {
        switch (k) {
        case 0x38:  a = a - 1; break;
        case 0x32:  a = a + 1; break;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        }
    }
}

/* v5: loop ditulis `do { } while (1)` */
v5(k, a)
int k, a;
{
    do {
        switch (k) {
        case 0x38:  a = a - 1; break;
        case 0x32:  a = a + 1; break;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        }
    } while (1);
}

/* v6: ada pernyataan kosong sesudah switch, di dalam loop */
v6(k, a)
int k, a;
{
    for (;;) {
        switch (k) {
        case 0x38:  a = a - 1; break;
        case 0x32:  a = a + 1; break;
        case 0x0d:  return a;
        case 0x1b:  return -1;
        }
        ;
    }
}
