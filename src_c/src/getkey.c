/* FUN_1000_1814 @ 1000:1814, 199 byte — baca satu tombol (blocking), sudah
 * disaring dari tombol khusus.
 *
 * Bagian 1: tunggu tombol, buang tombol-panah yang tidak dipakai, terjemahkan
 * lewat getch(). 'S'/'s' = saklar suara: ditelan lalu kembali menunggu.
 * Bagian 2: habiskan sisa tombol yang masih menumpuk di buffer; hanya ESC yang
 * boleh menggantikan tombol yang sudah didapat.
 *
 *   kbhit()=7443, rdkey()=6853 (0x100 intip, 0 buang), getch()=735a
 *   sndflag @0x83c
 *
 * SLOT dari disassembly: c@bp+2 (char), d@bp+3 (char), k@bp+4 (int); bingkai 6
 * (satu slot temp di bp+0). Dua char BERDAMPINGAN 1 byte masing-masing —
 * kompiler MEMANG mem-pack char, jadi urutan deklarasi c, d, k.
 *
 * ⭐ SEMUA percabangan pakai GOTO, bukan for(;;). Buktinya: tidak ada satu pun
 * instruksi back-edge loop. Tiap jalur melompat EKSPLISIT ke 0x181a atau
 * 0x1875, dan label akhir kedua `switch` berimpit dengan label loop. Bentuk
 * for(;;) bersarang memberi 218 byte dengan bingkai 8 (satu temp berlebih).
 */

extern unsigned sndflag;    /* @0x83c */

getkey()
{
    char c, d;
    int  k;

top:
    while (kbhit() == 0)   /* hasil TIDAK ditampung: "test ax,ax; je" */
        ;
    k = rdkey(0x100);
    /* SATU rantai `&&` berisi ENAM suku yang MEMBUNGKUS blok buang-tombol.
       Tiap detail biner terjelaskan olehnya:
         test ax,ax / mov [bp+4],ax / je got   <- suku 1 (k != 0); store k
                                                  disisipkan kompiler di sini
         and ax,0xff / jne got                 <- suku 2 pakai AX yang MASIH
                                                  hidup dari rdkey
         mov ax,[bp+4]                         <- muat ulang WAJIB: "and"
                                                  sudah merusak AX
         cmp/je got x3                         <- suku 3..5
         cmp ax,5000h / jne badan / jmp got    <- suku TERAKHIR `&&`
       Kalau suku 1 dipisah jadi `if (k == 0) goto got;`, kompiler memuat ulang
       k sebelum "and" (197 byte). Kalau seluruhnya ditulis `||` yang melompat
       ke `got`, suku terakhir jadi "je got" saja dan hasilnya 202 byte. */
    if (k != 0 && (k & 0xff) == 0) {
        if (k == 0x4b00 || k == 0x4d00 || k == 0x4800 || k == 0x5000)
            goto got;
        else {
            rdkey(0);
            goto top;
        }
    }

got:
    /* SWITCH: badan (saklar suara) dipancarkan SEBELUM rantai pembanding, dan
       rantainya muncul 0x53 lalu 0x73 = kebalikan urutan sumber. */
    c = getch();
    switch (c) {
    case 0x73:
    case 0x53:
        sndflag ^= 1;
        goto top;
    }

loop2:
    if (c == 0)
        goto out;
    if (rdkey(0x100) == 0)
        goto out;
    k = rdkey(0x100);
    if ((k & 0xff) == 0) {   /* diuji lewat `k & 0xff`, BUKAN lewat char */
        rdkey(0);
        goto loop2;
    }
    /* Badan di biner: "c = d" lebih dulu (0x18b0), lalu saklar suara (0x18b8);
       rantainya 0x53 / 0x73 / 0x1b -> urutan sumber 0x1b, 0x73, 0x53.
       Label akhir switch = 0x1875 = puncak loop2, jadi `break` di sini sama
       dengan kembali ke loop2 dan tak ada `jmp` tambahan. */
    switch (d = getch()) {
    case 0x1b:
        c = d;
        break;
    case 0x73:
    case 0x53:
        sndflag ^= 1;
        break;
    }
    goto loop2;

out:
    return c;
}

/* ✅ COCOK BYTE-PER-BYTE (199 byte). Empat hal yang menutupnya:
 *  1. Semua percabangan pakai GOTO, bukan for(;;) bersarang — tak ada satu pun
 *     instruksi back-edge loop di biner (218 -> 199, bingkai 8 -> 6).
 *  2. Suku 1-2 satu rantai `&&` (`k != 0 && (k & 0xff) == 0`) supaya "and"
 *     memakai AX yang masih hidup dari rdkey; kalau dipisah jadi `if` sendiri,
 *     kompiler memuat ulang k lebih dulu.
 *  3. Uji tombol-panah jadi `if` BERSARANG tersendiri, supaya k dimuat SEKALI
 *     ke AX ("mov ax,[bp+4]" + 4x "cmp ax,imm" = 15 byte). Kalau digabung rata
 *     ke rantai yang sama, kompiler membandingkan langsung dari slot
 *     ("cmp word ptr [bp+4],imm" 4x = 20 byte).
 *  4. `else` EKSPLISIT pada uji tombol-panah — ini byte terakhirnya.
 */
