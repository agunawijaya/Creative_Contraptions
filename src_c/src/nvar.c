/* FUN_1000_4094 @ 1000:4094, 566 byte — hitung varian mekanisme untuk satu id.
 *
 * Fase 1: susuri direktori record (maks 0x78 entri) dan kumpulkan indeks tiap
 * record yang id-nya (tanpa bit tinggi) sama dengan `want`. Record dengan `row`
 * yang sama dengan sebelumnya dilewati — jadi yang terkumpul adalah VARIAN,
 * bukan bagian. Bit 0x80 pada id memisahkan dua kelompok (grp[0]/grp[1]).
 * Berhenti lebih awal kalau id sudah melewati `want` (direktori terurut) atau
 * kalau sudah 0x32 varian.
 *
 * Fase 2 hanya untuk lvl 1 mode 3 dan kalau kelompok kedua tak kosong:
 * pilih satu varian per kelompok memakai `zsel[]`, lalu — kalau varian itu
 * bagian dari part yang tergambar DUA record (row berselisih 100) — sertakan
 * pasangannya juga. Hasilnya menimpa `list`.
 *
 *   recbase @0x73c, lvl @0x734, mode @0x792, zsel[] @0x836
 *   Balikan: jumlah entri di `list`.
 *
 * PETA SLOT (bingkai 38h; temp bp+0..6):
 *   8=i  0ah=cnt  0ch=(tak dipakai)  0eh=ok  10h=last(char)+11h(pad)
 *   12h=rp  14h=v  16h=acc  18h=grp[2]  1ch=a  1eh=b  20h=(tak dipakai)
 *   22h=r  24h=out[10]
 * Argumen: bp+3ch want, bp+3eh list.
 *
 * Dua slot (0ch dan 20h) memang DILEWATI biner — direproduksi sebagai lokal
 * tak terpakai, sama seperti pola di `fillans`.
 *
 * `out[cnt-1]` dipancarkan sebagai "[bp+si+22h]" dengan si=cnt*2 — kompiler
 * melipat "-1" ke dalam displacement. Jangan bingung dengan lokal di 22h.
 */

struct rec {
    char id;                /* +0  bit 0..6 = jenis, bit 7 = kelompok */
    char row;               /* +1  baris; +100 = bagian lanjutan */
    char rest[10];
};

extern struct rec *recbase; /* @0x73c */
extern int lvl;             /* @0x734 */
extern int mode;            /* @0x792 */
extern int zsel[];          /* @0x836 */

nvar(want, list)
int  want;
int *list;
{
    int i, cnt, unused1, ok;
    char last, pad1;
    struct rec *rp;
    int v, acc;
    int grp[2];
    int a, b, unused2, r;
    int out[10];

    /* ⭐ URUTAN INI TERBALIK dari urutan store di biner. MS C 1.04 mengangkat
       konstanta bersama (0 -> AX, recbase -> BX) lalu memancarkan store-nya
       dalam urutan KEBALIKAN sumber. Biner: [ok]=1, [last]=0ffh, [i]=ax,
       [grp0]=ax, [grp1]=ax, [cnt]=ax, [rp]=bx — jadi sumbernya begini: */
    cnt = 0;
    grp[1] = 0;
    grp[0] = 0;
    i = 0;
    ok = 1;
    last = 0xff;
    rp = recbase;
    /* Rantai `&&` RATA: biner membandingkan langsung dari slot
       ("cmp word ptr [bp+8],78h") dan kedua jalan keluarnya "jcc pendek ke
        badan; jmp jauh" karena 0x414e lebih dari 127 byte di depan. */
    while (i < 0x78 && ok != 0) {
        v = rp->id;
        v = v & 0x7f;
        if (v == want) {
            if (rp->row != last) {
                /* rp->id dibaca ULANG di sini — biner memakai temp bp+0 yang
                   menyimpan nilai TANPA mask dari atas. */
                if ((rp->id & 0x80) == 0)
                    grp[0] = grp[0] + 1;
                else
                    grp[1] = grp[1] + 1;
                /* post-increment: nilai BARU langsung dibandingkan dengan 0x32,
                   jadi kompiler menahannya di AX dan menaruh nilai LAMA di temp
                   bp+0 ("mov [bp],ax / inc ax / mov bx,[bp]"). Bandingkan fase 2
                   yang nilai barunya tak dipakai -> "inc word ptr [cnt]". */
                list[cnt++] = i;
                if (cnt >= 0x32)
                    ok = 0;
                last = rp->row;
            }
        }
        else if ((v & 0x7f) > want || v == 0)
            ok = 0;
        rp = rp + 1;
        i = i + 1;
    }
    if (lvl == 1 && mode == 3 && grp[1] > 0) {
        acc = 0;
        cnt = 0;
        i = 0;
        while (i < 2) {
            b = zsel[i];
            a = grp[i];
            if (b < a)
                r = acc + b;
            else
                r = acc + b % a;
            out[cnt++] = list[r];
            if (r > 0) {
                if (recbase[list[r]].row - 100 == recbase[list[r - 1]].row) {
                    out[cnt - 1] = list[r - 1];
                    out[cnt++] = list[r];
                }
            }
            else if (recbase[list[r + 1]].row - 100 == recbase[list[r]].row)
                out[cnt++] = list[r + 1];
            acc = acc + a;
            i = i + 1;
        }
        i = 0;
        while (i < cnt) {
            list[i] = out[i];
            i = i + 1;
        }
    }
    return cnt;
}

/* ⏳ BELUM COCOK — 551 byte vs 566, bingkai 3ch vs 38h (2 TEMP kelebihan).
 * Kemajuan putaran ini: 548 -> 551, dan PROLOG kini cocok byte-per-byte.
 *
 * SUDAH TERBUKTI & JANGAN DIUBAH:
 *   - jumlah & urutan LOKAL: i, cnt, unused1, ok, last(char)+pad, rp, v, acc,
 *     grp[2], a, b, unused2, r, out[10]  = 48 byte
 *     (slot 0ch dan 20h memang DILEWATI biner)
 *   - urutan penugasan awal `cnt, grp[1], grp[0], i, ok, last, rp` — TERBALIK
 *     dari urutan store di biner (lihat aturan "STORE konstanta ter-hoist" di
 *     README). Prolog 21 byte pertama cocok persis dengan urutan ini.
 *   - fase 1 memakai `list[cnt++] = i;` (post-increment), BUKAN dua pernyataan.
 *     Bentuk temp muncul karena `cnt` yang BARU langsung dibandingkan dgn 0x32.
 *   - `while (i < 0x78 && ok != 0)` rantai `&&` RATA
 *   - fase 1 `v = rp->id; v = v & 0x7f;` dua pernyataan; nilai tanpa-mask
 *     dipakai ulang dari temp bp+0 untuk uji `rp->id & 0x80`
 *   - `if ((rp->id & 0x80) == 0) grp[0]++ else grp[1]++` (arah ini)
 *   - guard fase 2 `lvl == 1 && mode == 3 && grp[1] > 0` satu rantai
 *
 * SISA MASALAH: 2 temp kelebihan + 15 byte kurang, semuanya di FASE 2.
 * Divergensi pertama sekarang di +286: fase 2 masih memakai bentuk temp untuk
 * `out[cnt++]`, padahal aslinya `inc word ptr [cnt]`. Nilai baru `cnt` memang
 * dipakai lagi di cabang (`out[cnt-1]`), jadi struktur cabang itulah yang perlu
 * diperbaiki — bukan bentuk `cnt++`-nya.
 *
 * SUDAH DICOBA & GAGAL:
 *   - urutan init fase 2 (acc,cnt,i / acc,i,cnt / cnt,acc,i) -> semua 551 byte
 *   - `out[cnt] = list[r]; cnt++;`        -> 536 byte
 *   - `out[cnt] = list[r]; cnt = cnt+1;`  -> 536 byte
 *
 * PEMICUNYA SUDAH DIPERSEMPIT LEWAT PROBE. Probe yang meniru fase 2 PERSIS
 * (lokal sama banyak, if/else untuk `r`, kedua cabang, `out[cnt++]` tiga kali)
 * tapi memakai pembanding SEDERHANA `list[r] - 100 == list[r-1]` menghasilkan
 * "inc word ptr [cnt]" yang BENAR — dan ukurannya tidak berubah walau bingkai
 * dibesarkan (pad[8], pad[20]). Jadi:
 *   - bukan ukuran bingkai
 *   - bukan `out[cnt-1]` di cabang
 *   - bukan if/else untuk `r`
 *   - PEMICUNYA ekspresi bersarang `recbase[list[r]].row`
 * Ekspresi itu butuh temp ekstra, dan tekanan itulah yang mendorong `cnt++`
 * ke bentuk temp. Perbaikan harus di BENTUK ekspresi record, bukan di `cnt++`.
 *
 * SUDAH DICOBA & GAGAL untuk ekspresi itu:
 *   - `(recbase + list[r])->row` (aritmetika penunjuk) -> sama, 551 byte
 *   - bentuk CHAR-POINTER dgn perkalian eksplisit, yang menutup `mkpal`:
 *     `((char *)recbase)[list[r] * 0xc + 1]` (dan `0xc * list[r+1]` untuk yang
 *     di 0x424f) -> 559 byte, bingkai 0x3e.
 *     HASIL BERCAMPUR dan itu informatif: PANJANG MEMBAIK 8 byte (551 -> 559,
 *     target 566) tapi BINGKAI MEMBURUK (0x3c -> 0x3e, target 0x38). Artinya
 *     bentuk ekspresinya kemungkinan BENAR tapi memakan satu temp lagi; yang
 *     harus dicari berikutnya adalah 3 slot yang mesti dilepas di tempat LAIN,
 *     bukan membatalkan bentuk ini.
 *
 * LANGKAH BERIKUT: pecah cabang fase 2. Petunjuk konkret dari biner:
 *   - 0x424f memakai imul TERBALIK ("mov ax,0ch / imul word ptr [si]") — di
 *     sumbernya konstanta di KIRI: `0xc * list[r+1]`; tiga imul lain normal.
 *   - `out[cnt-1]` dipancarkan sebagai "[bp+si+22h]" (kompiler melipat -1 ke
 *     displacement), jadi jangan tambah lokal untuk itu.
 *   - di cabang r>0, `list` tetap di BX sepanjang cabang; punya kita di CX.
 */
