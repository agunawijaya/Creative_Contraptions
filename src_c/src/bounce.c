/* FUN_1000_2504 @ 1000:2504, 398 byte — ANIMASI BOLA MEMANTUL di layar judul.
 *
 * Enam kali berturut-turut bola dilempar ke tepi layar yang berganti-ganti
 * searah jarum jam (fase 0=kiri, 1=bawah, 2=kanan, 3=atas), masing-masing ke
 * titik acak di sepanjang tepi itu. Berhenti kalau ada tombol ditekan.
 *
 * ⚠ KOREKSI KOMENTAR (2026-08-01, dari jalur port -- BYTE-nya tidak berubah).
 * Urutan tepi di atas ditulis saat nama `ballx`/`bally` masih dikira harfiah.
 * `setball()` membuktikan sebaliknya: `balltop = 199 - x` berarti argumen
 * pertama koordinat TEGAK, jadi ballx @0x260 = Y layar dan bally @0x25e = X.
 * Dengan itu `tx` sebenarnya Y-tujuan dan `ty` X-tujuan, sehingga:
 *     fase 0: tx=8      -> tepi ATAS      fase 1: ty=0x137 -> tepi KANAN
 *     fase 2: tx=0x97   -> tepi BAWAH     fase 3: ty=0     -> tepi KIRI
 * Tetap searah jarum jam, hanya titik mulainya bukan yang tertulis.
 *
 * Fungsi ini DIVERIFIKASI dengan menirunya di port (port/cc/core/vm.py
 * `_bounce`): layar judul jadi 675/675 frame byte-identik dgn VRAM emulator.
 * Undiannya juga terukur -- seed 0xa6b8 saat masuk, 32 `shuffle()` + 1
 * `rnd()` -> 0x3c11, cocok dgn @0x71a di emulator.
 *
 * Jumlah langkah dihitung dari jarak, tapi bukan jarak Euclid: dipakai
 * hampiran "oktagonal" (maks + separuh min) lalu dibagi 4 — dan pembagiannya
 * memang DUA KALI /2 di biner, bukan satu /4.
 *
 * Kalau prevtop atau prevx masih 0x140 (= 320, penanda "belum ada bola di
 * layar"), animasi dilewati: cukup kocok ulang palet lalu keluar.
 *
 *   shuffle()=2b34  keyhit()=1791  rnd()=5a5b  moveball()=29b0  putmsk()=6524
 *
 * ⭐ SWITCH RAPAT: nilai 0..3 berurutan, jadi kompiler memakai tabel INDEKS
 * (bukan tabel (nilai,label) seperti runmenu/review):
 *     mov si,ax / cmp si,4 / jae default / shl si,1 / jmp cs:[si+tabel]
 * Tabelnya 4 kata di 0x259d, isinya alamat badan case urut 0,1,2,3.
 *
 * PETA SLOT (bingkai 0x18): bp+0..2 = 2 TEMP, lalu
 *   bp+4=i  6=TAK DIPAKAI  8=ph  0ah=tx  0ch=bxc  0eh=ty  10h=byc
 *   12h=a  14h=b  16h=d
 * Argumen: bp+1ch=spr.
 * `byc` diisi tapi tak pernah dibaca — memang begitu di biner asli.
 *
 * URUTAN PENUGASAN AWAL dibaca TERBALIK dari urutan store: store "i, ph"
 * berarti sumbernya "ph = 0;" lalu "i = 0;". Sama untuk "byc, bxc" ->
 * sumbernya "bxc = ballx;" lalu "byc = bally;".
 */

extern int  prevtop;        /* @0x262 */
extern int  prevx;          /* @0x266 */
extern int  bally;          /* @0x25e */
extern int  ballx;          /* @0x260 */
extern int  page2;          /* @0x2e2 */
extern int  sndmode;        /* @0x722 */
extern int *sndptr;         /* @0x720 */
extern int  sndnull[];      /* @0x724 */

bounce(spr)
int spr;
{
    int i, unused, ph, tx, bxc, ty, byc, a, b, d;

    shuffle();
    if (prevtop == 0x140 || prevx == 0x140) {
        shuffle();
        return;
    }
    ph = 0;
    i = 0;
    while (i < 6 && keyhit() == 0) {
        switch (ph) {
        case 0:
            tx = 8;
            ty = rnd(0x10e) + 0x14;
            break;
        case 1:
            ty = 0x137;
            tx = rnd(0x6f) + 0x1c;
            break;
        case 2:
            tx = 0x97;
            ty = rnd(0x10e) + 0x14;
            break;
        case 3:
            tx = rnd(0x6f) + 0x1c;
            ty = 0;
            break;
        }
        ph++;
        if (ph > 3)
            ph = 0;
        bxc = ballx;
        byc = bally;
        a = byc - ty;
        a = (a < 0) ? -a : a;
        b = bxc - tx;
        b = (b < 0) ? -b : b;
        a = ((a > b) ? a : b) + ((a <= b) ? a : b) / 2;
        a = a / 2;
        d = a / 2;
        if (d > 0xb4)
            d = 0x96;
        /* URUTAN INI PENTING. Biner memuat nilai yang butuh register lebih
           dulu (ax=500, bx=d*8+500) dan MENUNDA store-nya sampai sesudah
           push argumen, sementara store immediate dipancarkan di tempat.
           Menaruh "sndnull[2] = 8" di depan membuat sndnull[0] tidak lagi
           lewat AX, sehingga store-nya jadi bentuk umum 4 byte (89 06)
           bukan bentuk akumulator 3 byte (a3) -- persis 1 byte kelebihan. */
        sndnull[0] = 500;
        sndnull[1] = d * 8 + 500;
        sndnull[2] = 8;
        sndptr = sndnull;
        sndmode = 1;
        moveball(0, ballx, bally, tx, ty, d, 0);
        i++;
    }
    putmsk(spr, page2);
}
