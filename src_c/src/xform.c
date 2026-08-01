/* FUN_1000_5e3b @ 1000:5e3b, 107 byte — TRANSFORM koordinat logis -> layar + gambar.
 *
 * Inilah fungsi yang selama ini disebut "belum diturunkan" di CODE_MAP: ia yang
 * mengubah koordinat LOGIS bola (ballx@0x260, bally@0x25e) jadi posisi layar
 * sungguhan, memakai tabel sub-pixel ber-indeks (bally % 4).
 *
 *   tblA @0x2cc, tblB @0x2d4  = masing-masing 4 PENUNJUK, bukan nilai geser.
 *   sx @0x2dc, sy @0x2de      = penunjuk terpilih yang diteruskan ke draw()
 *
 * ⭐ ISI TABELNYA SUDAH DIBACA (2026-08-01) dari DGROUP yang byte-exact:
 *   tblA -> 0x1fb2/0x1fca/0x1fe2/0x1ffa   tblB -> 0x2012/0x202a/0x2042/0x205a
 *   Delapan tabel berjarak 24 byte, menempati 0x1fb2..0x2072 (192 byte).
 *   24 byte = 8 baris x 3 byte = 8 baris x 12 piksel. Dirender, isinya jelas:
 *     tblA = SPRITE BOLA (bulat 8x8 dengan sorotan), 4 salinan
 *     tblB = MASK-nya, 4 salinan
 *   Antar-fase, polanya bergeser SATU PIKSEL ke kanan. Itu trik klasik CGA:
 *   satu byte memuat 4 piksel, jadi penulis menyiapkan 4 salinan ter-geser
 *   supaya bola bisa diposisikan per-piksel tanpa menggeser bit saat runtime.
 *
 * ⚠ PERTANYAAN TERBUKA yang penting untuk jalur PORT: indeks fasenya diambil
 *   dari `bally % 4` (@0x25e). Tapi pra-geser 4 fase di CGA HARUS mendatar --
 *   satu byte = 4 piksel MENDATAR. Jadi entah 0x25e sebenarnya koordinat X
 *   (bukan Y seperti namanya sekarang), atau ada hal lain yang belum dipahami.
 *   Ini sejalan dengan temuan bahwa urutan argumen blit adalah (spr, Y, X, H, W)
 *   dan CONTRAP menyimpan (y, x) -- proyek ini beberapa kali menemukan sumbu
 *   tertukar. BELUM DIVERIFIKASI; jangan dipakai sebagai fakta.
 *   page @0x2e0, page2 @0x2e2 = pasangan halaman gambar
 *   buf1 @0x29c, buf2 @0x2b4  = buffer baris
 *   prep()=6939, blend()=5ea6, putmsk()=6524, draw()=657c   (semuanya assembly)
 */

extern int ballx;           /* @0x260 */
extern int bally;           /* @0x25e */
extern int tblA[];          /* @0x2cc */
extern int tblB[];          /* @0x2d4 */
extern int sx;              /* @0x2dc */
extern int sy;              /* @0x2de */
extern int page;            /* @0x2e0 */
extern int page2;           /* @0x2e2 */
extern char buf1[];         /* @0x29c */
extern char buf2[];         /* @0x2b4 */

xform()
{
    /* TANPA lokal: di fungsi ini bingkai = 4 + 2*jumlah_lokal, jadi
       nol lokal -> sub sp,4 seperti aslinya. (Basis bingkai TIDAK
       selalu 2 -- bandingkan delay() yang basisnya 2.) */
    sx = tblA[bally % 4];
    sy = tblB[bally % 4];
    prep(ballx, bally, page);
    blend(page, page2, buf1, buf2);
    putmsk(buf2, page2);
    draw(page, sy, sx);
}
