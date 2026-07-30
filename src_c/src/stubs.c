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
main() { return 0; }

drawitem() { return 0; }
fmtnum() { return 0; }
pickvar() { return 0; }    /* @0x42ca, 1.730 byte -- belum direkonstruksi */
waitn() { return 0; }      /* @0x2b11 -- BUKAN pause() @0x31b0 */
tone3() { return 0; }      /* @0x5b73 -- di dalam rentang snd2 yang
                              belum dirakit; sementara stub */
rdkey() { return 0; }
refresh() { return 0; }
sndoff() { return 0; }
sndon() { return 0; }

/* Simbol DATA yang tidak bisa lewat gdata.c:
 *   sndbuf -- alamat aslinya 0x670e, DI LUAR DGROUP (itu segmen kode).
 *             Di sini cuma penampung supaya link jalan.
 *   menu   -- tabel entri menu @0x1c28; dipakai goalmenu.c. Disediakan di sini
 *             karena deklarasinya bertipe struct sehingga belum dipanen gendata.
 */
char sndbuf[16];
char menu[360];
