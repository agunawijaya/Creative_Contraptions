/* FUN_1000_3322 @ 1000:3322, 248 byte — layar PILIH GOAL (tema).
 *
 * Menggambar 6 baris menu berurutan ke bawah: tiap baris digambar oleh drawitem(),
 * yang MENGEMBALIKAN tinggi baris itu, lalu tinggi tsb ditambahkan untuk mendapat
 * posisi Y baris berikutnya. Baris ke-7 (id 18) digambar tapi Y-nya tidak dipakai lagi.
 * Setelah itu Y tiap baris disimpan ke tabel menu supaya rutin sorot/pilih tahu
 * di mana tiap baris berada.
 *
 * Alamat global (DGROUP) di biner asli:
 *   0x846 = mode_    (mode permainan yang dipilih)
 *   0x740 = level_   (Apprentice / Master Builder)
 *   0x84a = ytop_    (Y baris pertama)
 *   0x1c28 = menu[]  (tabel entri menu, stride 24 byte, field Y di offset 22)
 *
 * Di sini alamatnya tidak perlu tepat: semuanya jadi slot relokasi yang diisi linker.
 * Yang harus cocok adalah BENTUK kodenya.
 *
 * GAYA: K&R (MS C 1.04 pra-ANSI).
 */

struct mitem {
    char pad[22];       /* isi entri lain yang tidak disentuh fungsi ini */
    int  y;
};

extern struct mitem menu[];
extern int mode_;
extern int level_;
extern int ytop_;

/* CATATAN BENTUK PENULISAN (dibuktikan lewat src/probe3.c):
 * hasil drawitem() HARUS ditampung variabel tersendiri `h` lalu dijumlahkan
 * terpisah. Menulis "y2 = y1 + drawitem(...)" menghasilkan kode yang BEDA:
 * kompiler tidak membuat slot sementara dan memakai register yang lain
 * (mov ax,0eh alih-alih mov cx,0eh). `h` dideklarasikan TERAKHIR — itu yang
 * menempatkannya di slot bp+0eh seperti biner asli. */

goalmenu()
{
    int y1, y2, y3, y4, y5, y6, h;

    y1 = ytop_;
    h = drawitem(mode_, level_, 13, y1);
    y2 = y1 + h;
    h = drawitem(mode_, level_, 14, y2);
    y3 = y2 + h;
    h = drawitem(mode_, level_, 15, y3);
    y4 = y3 + h;
    h = drawitem(mode_, level_, 16, y4);
    y5 = y4 + h;
    h = drawitem(mode_, level_, 17, y5);
    y6 = y5 + h;
    h = drawitem(mode_, level_, 18, y6);
    menu[0].y = y1;
    menu[1].y = y2;
    menu[2].y = y3;
    menu[3].y = y4;
    menu[4].y = y5;
    menu[5].y = y6;
    setsel(menu, 15);
    runmenu(menu, 15);
}
