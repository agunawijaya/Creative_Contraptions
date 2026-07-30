/* FUN_1000_31b0 @ 1000:31b0, 42 byte — jeda `n` bingkai, batal kalau ada tombol.
 *
 *   keyhit() = FUN_1000_1791 (sudah direkonstruksi)
 *   vbend()  = FUN_1000_5da1 — tunggu sampai bit vblank PADAM (retrace selesai)
 *   vbwait() = FUN_1000_5d98 — tunggu sampai bit vblank MENYALA (retrace mulai)
 * Keduanya membaca port CGA 0x3da; dipanggil berpasangan supaya tiap putaran
 * loop = tepat satu bingkai layar. Jadi `n` di sini satuannya bingkai, bukan tik.
 *
 * Bingkai 4 = 2 + 2×1 lokal: hanya `i` di bp+2. Argumen `n` di bp+8.
 *
 * KUNCI BENTUK: cek tombol ada di SYARAT for lewat `&&`, BUKAN sebagai
 * `if (keyhit()) return;` di dalam badan. Bedanya nyata di biner:
 *   - `if (...) return;`  -> epilog DIPANCARKAN ULANG di tempat (add sp,4;
 *     pop bp; ret) lalu dilompati "je +5"  -> 47 byte
 *   - `&&` di syarat       -> "jne" langsung ke epilog BERSAMA di 0x31d5
 * Aslinya punya satu epilog saja dan dua "jump false" (jge dan jne) menuju
 * ke sana — itu tanda tangan operator `&&`.
 */

pause(n)
int n;
{
    int i;

    for (i = 0; i < n && keyhit() == 0; i++) {
        vbend();
        vbwait();
    }
}
