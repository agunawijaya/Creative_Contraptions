/* stubs.c — DEFINISI SEMENTARA untuk fungsi yang belum direkonstruksi.
 *
 * Tujuannya SATU: membuat LINK berhasil supaya kerangka .EXE pertama ada dan
 * tata letak DGROUP hasil link bisa dibandingkan dengan biner asli. Isi fungsi
 * sengaja kosong -- program hasil link BELUM berjalan benar, dan tiap stub di
 * sini adalah hutang yang harus diganti rekonstruksi sungguhan.
 *
 * Dibangkitkan dari selisih EXTDEF vs PUBDEF (src_c/verify/symbols.py).
 *
 * Sejak 2026-07-30 sebagian besar primitif assembly SUDAH NYATA (dirakit
 * dengan MASM 1.27 dari berkas di src_c/asm) sehingga stub-nya dihapus: blit,
 * draw, fillrect, line, prep, put, putmsk, rnd, text, shftl, shftr,
 * sndsave, sndrest, vbwait, vbend.
 *
 * BUKAN semua yang belum ada perlu stub: rutin di wilayah >=0x69d7 berasal
 * dari MC.LIB dan cukup dipanggil dengan NAMA PUSTAKANYA. Cek dulu dengan
 * `python src_c/verify/libmatch.py` sebelum menambah stub baru. Enam stub
 * sudah dihapus karena itu: err->printf, fopen_->lseek, fread_->read,
 * avail->kbhit, togsnd/xlate->getch.
 * Kalau sebuah fungsi sudah direkonstruksi, HAPUS stub-nya dari daftar ini.
 */

/* main @0x0082, 4.219 byte — fungsi TERBESAR dan belum direkonstruksi.
 * Stub-nya wajib ada, kalau tidak MC.LIB(_MAIN) melaporkan "unresolved". */
/* main() kini ada di main_.c (draf 126 byte dari 4.219). */

/* Fungsi yang DIPANGGIL main tapi belum direkonstruksi -- stub supaya LINK
   jalan. Hapus satu per satu saat fungsinya ditulis. */
setup() { return 0; }      /* @0x5f90 */
animvm() { return 0; }     /* @0x18db -- VM animasi, 3.040 byte */

/* Simbol DATA yang tidak bisa lewat gdata.c:
 *   sndbuf -- alamat aslinya 0x670e, DI LUAR DGROUP (itu segmen kode).
 *             Di sini cuma penampung supaya link jalan.
 *   menu   -- tabel entri menu @0x1c28; dipakai goalmenu.c. Disediakan di sini
 *             karena deklarasinya bertipe struct sehingga belum dipanen gendata.
 */
char sndbuf[16];
char menu[360];
