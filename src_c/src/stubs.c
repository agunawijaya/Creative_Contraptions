/* stubs.c — DEFINISI SEMENTARA untuk fungsi yang belum direkonstruksi.
 *
 * Tujuannya SATU: membuat LINK berhasil supaya kerangka .EXE pertama ada dan
 * tata letak DGROUP hasil link bisa dibandingkan dengan biner asli. Isi fungsi
 * sengaja kosong -- program hasil link BELUM berjalan benar, dan tiap stub di
 * sini adalah hutang yang harus diganti rekonstruksi sungguhan.
 *
 * Dibangkitkan dari selisih EXTDEF vs PUBDEF (src_c/verify/symbols.py).
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

blit() { return 0; }
draw() { return 0; }
drawitem() { return 0; }
fillrect() { return 0; }
fmtnum() { return 0; }
line() { return 0; }
pickvar() { return 0; }    /* @0x42ca, 1.730 byte -- belum direkonstruksi */
prep() { return 0; }
put() { return 0; }        /* @0x65e0 -- dipakai shuffle/askopts */
putmsk() { return 0; }     /* @0x6524 -- dipakai xform/bounce; rutin BERBEDA,
                              dulu keliru ikut bernama put() sehingga LINK
                              menyatukan dua alamat jadi satu. */
rnd() { return 0; }
waitn() { return 0; }      /* @0x2b11 -- BUKAN pause() @0x31b0 */
rdkey() { return 0; }
refresh() { return 0; }
sndoff() { return 0; }
sndon() { return 0; }
sndrest() { return 0; }
sndsave() { return 0; }
vbwait() { return 0; }
vbend() { return 0; }
text() { return 0; }

/* Primitif geser layar, dipakai review() saat menggulir strip palet.
 * Keduanya assembly tulisan tangan: prolog "push bp; mov bp,sp; push es;
 * push ds" (menyimpan segmen karena menulis ke memori video). */
shftl() { return 0; }       /* @0x5dce */
shftr() { return 0; }       /* @0x6600 */

/* Simbol DATA yang tidak bisa lewat gdata.c:
 *   sndbuf -- alamat aslinya 0x670e, DI LUAR DGROUP (itu segmen kode).
 *             Di sini cuma penampung supaya link jalan.
 *   menu   -- tabel entri menu @0x1c28; dipakai goalmenu.c. Disediakan di sini
 *             karena deklarasinya bertipe struct sehingga belum dipanen gendata.
 */
char sndbuf[16];
char menu[360];
