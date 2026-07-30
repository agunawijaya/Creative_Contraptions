/* FUN_1000_3b83 @ 1000:3b83, 204 byte — gambar STRIP PALET 9 mekanisme di bilah bawah.
 *
 * sel == -1 berarti "pilih tengah": kursor ditaruh di nmech/2.
 * Strip menampilkan 9 slot dari lo..lo+8; slot di luar rentang digambar kosong.
 *   nmech @0x3ac, cur @0x51c, lo @0x51e, hi @0x520
 *   spr[] @0x7fa = nomor sprite per mekanisme (char, unsigned di MS C 1.04)
 *   blit()=672f, fillrect()=6869
 * Slot digambar dari KANAN ke kiri: x = 0x110 - i*0x20.
 */

extern int  nmech;          /* @0x3ac */
extern int  cur;            /* @0x51c */
extern int  lo;             /* @0x51e */
extern int  hi;             /* @0x520 */
extern char spr[];          /* @0x7fa */

drawpal(sel, base)
int sel, base;
{
    int i, x, addr;         /* t BUKAN variabel: slot bp+0 itu sementara-kompiler */

    if (sel == -1) {
        cur = nmech / 2;    /* nmech TIDAK ditampung: asli langsung idiv */
        lo = nmech / 2 - 4;
        hi = cur + 4;
    }
    else {
        cur = sel;
        lo = sel - 4;
        hi = sel + 4;
    }
    for (i = 0; i < 9; i++) {
        if (lo + i >= 0 && lo + i < nmech) {
            addr = base + spr[lo + i] * 0xc0;   /* lo+i DIHITUNG ULANG di sini,
                                                   bukan dipakai dari penampung */
            blit(addr, 0xa8, 0x110 - i * 0x20, 0x18, 0x20);
        }
        else {
            x = 0x110 - i * 0x20;          /* x DITAMPUNG lalu dipakai lagi
                                              sebagai "x + 0x1f" -- bukan
                                              dihitung ulang jadi 0x12f - i*32 */
            fillrect(x, 0xa8, x + 0x1f, 0xbf, 0);
        }
    }
}

/* ✅ COCOK BYTE-PER-BYTE (204 byte).
 *
 * Catatan di bawah ini adalah RIWAYAT dari masa fungsi ini masih near-miss.
 * Bagian "sudah terbukti" dan "sudah dicoba & gagal" tetap berlaku dan
 * berguna; bagian "sisa" / "langkah berikut" SUDAH SELESAI — abaikan.
 * ---------------------------------------------------------------------
 * (riwayat) BELUM COCOK — 192 byte vs 204 (12 KURANG).
 * SUDAH DICOBA & GAGAL:
 *   - nmech dipakai inline tanpa lokal t            -> 186 (makin pendek)
 *   - t > -1 sbg ganti t >= 0                       -> 181 (makin pendek)
 * Arahnya SELALU makin pendek, jadi ada kode di asli yang belum kita tulis.
 * PETUNJUK yang belum ditindaklanjuti: Ghidra menampilkan panggilan fillrect
 * di cabang else dengan ENAM argumen (…,0xbf,0,iVar2) padahal di tempat lain
 * 6869 hanya lima. Kalau memang enam, tiap pemanggilan kurang satu push.
 */
