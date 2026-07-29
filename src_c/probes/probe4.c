/* Probe #4 — apakah MS C 1.04 menerjemahkan `switch` bernilai jarang menjadi
 * TABEL (nilai,label) yang dicari mundur, lalu "jmp cs:[si+..]"?
 *
 * Pola yang dicari (dari biner asli @0x2420):
 *     cmp ax, [si+tabel]
 *     jne  lewat
 *     jmp  word ptr cs:[si+tabel+2]
 *   lewat:
 *     sub si, 4
 *     jns ulang
 *     jmp default
 *
 * Kalau cocok, berarti 17 "handler opcode" VM animasi itu bukan fungsi assembly
 * terpisah, melainkan CASE di dalam satu switch milik FUN_1000_18db.
 */

int dispatch(op)
int op;
{
    switch (op) {
    case 0x00: return 10;
    case 0x01: return 11;
    case 0x02: return 12;
    case 0x07: return 17;
    case 0x0c: return 22;
    case 0xff: return 99;
    }
    return 0;
}
