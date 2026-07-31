/* FUN_1000_278e @ 1000:278e (149 byte) — gambar satu part dari skrip.
 *
 * Baca SATU byte dari kursor skrip sebagai nomor part relatif, ambil
 * record-nya, lalu blit spritenya pada (x + dx, y + dy).
 *
 * ⚠ DUA pola byte yang BERBEDA dalam satu fungsi:
 *   - nomor part dibaca TANPA pemulihan tanda (cuma `xor ah,ah`)
 *   - geser dx/dy dipulihkan tandanya dengan ambang 0xC8, bukan 0x80
 *
 * ⚠ Menunggu `ticks` (0x2E4) turun ke <= 0 lalu menyetelnya 1 -- gelung
 * tunggu kosong `while (ticks > 0) ;`
 *
 *   blit()=672f
 *
 * ✅ COCOK byte-per-byte (149/149).
 *
 * ⭐ TIGA PERUBAHAN yang membawanya dari 14% ke cocok penuh:
 * 1. Pakai PENUNJUK `struct rec *` (rp = recs + idx) alih-alih int + cast.
 *    Versi int+cast menuntut temp berlebih -> bingkai 0x14, bukan 0x10.
 *    Ini melengkapi aturan akses record: untuk penunjuk yang DISIMPAN ke
 *    lokal dan dipakai berkali-kali, bentuk struct-lah yang benar; bentuk
 *    penunjuk-char hanya untuk akses sekali pakai.
 * 2. POST-INCREMENT dalam satu ekspresi: `*scrptr++`, bukan `*scrptr;` lalu
 *    `scrptr++;`. Aslinya `inc [scrptr]` datang SEBELUM `mov al,[si]`.
 * 3. `scrptr` dideklarasikan `char *`, BUKAN `int` yang dicor `*(char *)`.
 *    Itulah 1 byte terakhir: tipe penunjuk asli dimuat LANGSUNG ke SI
 *    (`mov si,[3AEh]`, 4 byte), sedangkan bentuk cor lewat AX dulu
 *    (`mov ax,[3AEh]` + `mov si,ax`, 5 byte). Lihat README §CAST PENUNJUK.
 *    Aman untuk DGROUP: gendata.py memancarkan tiap simbol BUKAN-larik
 *    sebagai `int` apa pun tipe yang tertulis di deklarasi extern.
 */

/* Field di offset 6 dibaca sebagai KATA (`push word ptr [si+6]`), sisanya
   byte. 12 byte per record, sama seperti di pickvar. */
struct rec {
    char id, row, w, h, dx, dy;
    int  spr;
    int  rest[2];
};

extern char *scrptr;            /* @0x3ae  kursor baca skrip */
/* ⚠ 0x2E4 SUDAH bernama `ticks` di berkas lain -- JANGAN beri nama kedua. */
extern int  ticks;              /* @0x2e4 */

f278e(x, y, base, recs)
int  x, y, base;
struct rec *recs;
{
    struct rec *rp;
    int idx;
    int dx, dy;

    /* Aslinya `inc [scrptr]` datang SEBELUM `mov al,[si]` -- itu pola
       POST-INCREMENT dalam satu ekspresi, bukan dua pernyataan. */
    idx = base + *scrptr++;
    rp = recs + idx;
    dx = rp->dx;
    dx = (dx >= 0xc8) ? dx - 0x100 : dx;
    dy = rp->dy;
    dy = (dy >= 0xc8) ? dy - 0x100 : dy;
    while (ticks > 0)
        ;
    ticks = 1;
    blit(rp->spr, x + dx, y + dy, rp->w, rp->h);
}
