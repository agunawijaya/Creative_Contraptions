/* FUN_1000_53ff @ 1000:53ff, 262 byte — muat satu record aset dari arsip,
 * lalu dekode RLE-nya ke `dst`.
 *
 * Direktori arsip = array record 0xc byte: ukuran ter-kompresi di +6 (int),
 * offset berkas di +8 (long). Fungsi ini: cek ukuran <= 1500, seek, baca ke
 * penyangga lokal 1500 byte, lalu unrle() ke tujuan.
 *
 *   lseek()=6e8b, read()=6d31, printf()=6a48 (semua dari MC.LIB)
 *   unrle() = FUN_1000_666a (sudah direkonstruksi)
 *   Balikan: -1 kalau gagal, hasil unrle() kalau berhasil.
 *
 * ⭐ FUNGSI INI PENUH ARITMETIKA `long` — MS C 1.04 memang punya long
 * (lihat README). Cirinya:
 *   - int -> long: "xor cx,cx / test ax,ax / jns +1 / dec cx" (perluasan tanda)
 *   - banding long vs konstanta: panggil CXM/CXC helper "call 751c" (CXC33)
 *   - banding long vs long: "cmp <high>; jne +3; cmp <low>" lalu je/jne
 *   - argumen long didorong DUA kata (kata rendah di alamat rendah)
 *
 * ⚠ ARTEFAK KOMPILER di 0x5483: perbandingan `p == -1L` memancarkan
 *   "cmp ax,0ffffh / jne +3 / add ax,9449h" — instruksi `add` itu MERUSAK flag
 *   sehingga `jne` sesudahnya SELALU diambil, dan blok "printf(0x1e9c)" di
 *   0x548e jadi TIDAK PERNAH TERCAPAI. Ghidra melaporkannya sebagai
 *   "Removing unreachable block (ram,0x0001548e)". Jadi cek gagal-seek di game
 *   asli memang tidak pernah jalan. Bug ini HARUS direproduksi apa adanya —
 *   jangan "diperbaiki".
 *
 * PETA SLOT (bingkai 5f0h, temp di bp+0/bp+2; lokal berurutan):
 *   bp+4  n    (long) ukuran; DIPAKAI ULANG untuk hasil unrle di akhir
 *   bp+8  off  (long) offset berkas
 *   bp+0ch p   (long) hasil lseek
 *   bp+10h got (long) hasil read
 *   bp+14h buf[1500]
 * Argumen: bp+5f4h fh, 5f6h base, 5f8h id, 5fah dst.
 */

struct hdr {
    char pad0[6];           /* +0..5 */
    int  size;              /* +6  ukuran ter-kompresi */
    long off;               /* +8  offset di dalam berkas */
};                          /* = 0xc byte */

load(fh, base, id, dst)
int   fh;
struct hdr *base;
int   id;
char *dst;
{
    long n, off, p, got;
    char buf[1500];

    /* Displacement 8-bit "[bx+6]" -> subscript array struct, bukan
       "*(int *)(base + id*0xc + 6)". Dihitung DUA KALI (imul 0ch + add base
       muncul dua kali di biner), jadi memang dua ekspresi terpisah. */
    n = base[id].size;
    if (n > 1500) {
        printf(0x1e74, fh, id);
        return -1;
    }
    off = base[id].off;
    p = lseek(fh, off, 0);
    if (p == -1L) {
        printf(0x1e9c);
        return -1;
    }
    got = read(fh, buf, n);
    /* `else` EKSPLISIT — tanpa itu `return n` di bawah memakai AX yang masih
       hidup; dengan `else` kompiler menutup blok lalu MEMUAT ULANG
       ("mov ax,[bp+4]") sebelum epilog. Itu 3 byte terakhir yang menyamakan
       panjang jadi 262. */
    if (got != n) {
        printf(0x1ead);
        return -1;
    }
    else
        n = unrle(buf, dst, n);
    return n;
}
