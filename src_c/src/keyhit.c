/* FUN_1000_1791 @ 1000:1791, 131 byte — polling keyboard dgn penanganan tombol khusus.
 *
 *   kbhit() = FUN_1000_7443 ; rdkey() = FUN_1000_6853 (0x100 = intip, 0 = buang)
 *   getch() = FUN_1000_735a ; sndflag @0x83c
 *
 * Balikan: 0 = tak ada tombol, 1 = tombol panah / buffer kosong,
 *          selain itu = kode ASCII-nya. 'S'/'s' = saklar suara, ditelan di sini.
 *
 * KUNCI BENTUK: byte rendah TIDAK diambil dengan "k & 0xff" melainkan dengan
 * PENUGASAN KE VARIABEL char (`c = k;`). Cirinya di biner:
 *     mov byte ptr [bp+4], al      <- store 8 bit ke slot char
 *     mov word ptr [bp+2], ax      <- store 16 bit ke slot int
 * Menulis "c = k & 0xff" dengan c bertipe int menghasilkan kode yang lain.
 * Slot: k dideklarasikan pertama (bp+2), c kedua (bp+4).
 */

extern unsigned sndflag;    /* @0x83c */

keyhit()
{
    int k;
    char c;

    for (;;) {
        if (kbhit() == 0)
            return 0;
        k = rdkey(0x100);
        c = k;
        if (k == 0)
            return 1;
        switch (c) {           /* SWITCH, bukan if/else: badan case ditaruh
                                  lebih dulu, dispatch-nya di bawah (jmp 17fb).
                                  Urutan case = urutan badan di biner:
                                  toggle-suara @17c7 sebelum cek-panah @17d2 */
        /* urutan label: rantai pembanding di biner muncul 0 / 0x53 / 0x73,
           yaitu KEBALIKAN urutan sumber */
        case 0x73:
        case 0x53:
            getch();
            sndflag ^= 1;
            continue;      /* continue, bukan break: tiap case melompat BALIK ke awal loop */
        case 0:
            /* Bentuk NEGATIF + && : keempat "cmp/je" menuju SATU target
               "return 1" yang ditaruh SESUDAH blok rdkey. Bentuk positif
               (== .. || ..) membalik uji terakhir jadi "jne" dan menaruh
               return 1 di tengah -> 5 byte lebih pendek. */
            if (k != 0x4b00 && k != 0x4d00 && k != 0x4800 && k != 0x5000) {
                rdkey(0);
                continue;
            }
            return 1;
        }
        return c;              /* di LUAR switch, BUKAN "default:" -- badan
                                  default di biner muncul SESUDAH rantai
                                  pembanding, ciri jatuh-tembus, bukan case */
    }
}


/* ✅ COCOK BYTE-PER-BYTE (131 byte).
 *
 * Catatan di bawah ini adalah RIWAYAT dari masa fungsi ini masih near-miss.
 * Bagian "sudah terbukti" dan "sudah dicoba & gagal" tetap berlaku dan
 * berguna; bagian "sisa" / "langkah berikut" SUDAH SELESAI — abaikan.
 * ---------------------------------------------------------------------
 * (riwayat) BELUM COCOK — 126 byte vs 131 (5 KURANG).
 * Kemajuan besar putaran ini: 137 -> 133 -> 126 (menyeberang dari kepanjangan
 * ke kependekan), dan STRUKTURNYA kini terbukti `switch`, bukan if/else.
 * Yang sudah dipastikan dari biner:
 *   - badan case ditaruh dulu, dispatch "jmp 17fb" di bawah  -> switch
 *   - rantai pembanding muncul 0 / 0x53 / 0x73 = KEBALIKAN urutan sumber
 *   - "return c" ada SESUDAH rantai = jatuh-tembus, bukan "default:"
 *   - keempat cmp tombol panah "je" ke SATU target return 1 yang ditaruh
 *     SESUDAH blok rdkey
 * SUDAH DICOBA & GAGAL: bentuk negatif (k != A && ...) -> tetap 126.
 * Sisa 5 byte kemungkinan di penempatan blok rdkey/continue relatif ke return 1.
 */
