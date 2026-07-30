/* FUN_1000_2d11 @ 1000:2d11, 383 byte — LOOP ISI JAWABAN untuk satu contraption.
 *
 * Berputar slot demi slot: untuk slot yang sedang aktif (`slot` @0x51a),
 * nvar() menyusun daftar varian yang boleh dipakai, lalu pickvar() (0x42ca)
 * membiarkan pemain memilih salah satunya. Pilihan disimpan ke tiga tabel
 * sejajar: nomor varian ke `vsel[]`, id record ke `ans[]`, jenis part ke
 * `ids[]`. Sesudah setiap pilihan, slot maju satu dan berputar di n-1.
 *
 * Loop berhenti kalau pickvar() mengembalikan nilai NEGATIF. -1 berarti batal;
 * nilai negatif lain berarti "keluar sementara" dan diperiksa lewat clrbot().
 * Bit 15 pada nilai balik adalah penanda, jadi nomor varian selalu diambil
 * dengan `& 0x7fff`.
 *
 *   kbflush()=36ef  nvar()=4094  pickvar()=42ca  clrbot()=5911
 *   place()=4e3e    printf()=6a48 (MC.LIB)
 *   slot @0x51a ; fh @0x72c ; recbase @0x73c ; mark[] @0x742
 *
 * ⚠ clrbot() SELALU mengembalikan 0x20, jadi cabang 0x1b/0x0d di switch ini
 * tidak pernah tercapai di biner asli. Itu memang begitu — jangan "diperbaiki".
 *
 * PETA SLOT (bingkai 0x7a): bp+0..6 = 4 TEMP, lalu
 *   bp+8=u  0ah=v  0ch=w  0eh=k  10h=list[50] (10h..73h)
 *   74h=a  76h=changed  78h=sel
 * u/v/w cuma menampung nilai argumen dan TIDAK pernah dibaca lagi; store-nya
 * ditunda sampai sesudah push, jadi argumennya didorong dari register.
 * Argumen: bp+7eh=n, 80h=vsel, 82h=ans, 84h=ids, 86h=tab, 88h=flag,
 *          8ah=ctx, 8ch=buf, 8eh=buf2.
 *
 * ⭐ DUA perkalian yang SAMA ditulis BERBEDA di sumber aslinya, dan itu terlihat:
 *     "slot * 3"  -> mov ax,[slot] / mov bx,3 / imul bx      (0x2d24)
 *     "3 * slot"  -> mov ax,3      / imul word ptr [slot]    (0x2d58)
 * Jangan diseragamkan; ikuti biner.
 *
 * ⭐ INDEKS MAJEMUK dipecah: untuk `tab[slot*3 + 2]` kompiler menskala bagian
 * VARIABEL (slot*3) dengan ukuran elemen lalu menambahkan bagian KONSTAN yang
 * sudah diskala (2*2=4) — jadi "imul 3 / shl 1 / add ax,4", bukan
 * "imul 3 / add 2 / shl 1".
 */

struct rec {
    char id;                /* +0 */
    char rest[11];
};                          /* = 0xc byte */

extern struct rec *recbase; /* @0x73c */
extern int slot;            /* @0x51a */
extern int fh;              /* @0x72c */
extern int mark[];          /* @0x742 */

runfill(n, vsel, ans, ids, tab, flag, ctx, buf, buf2)
int  n;
int *vsel;
int *ans;
int *ids;
int *tab;
int  flag;
int  ctx;
int  buf, buf2;
{
    int u, v, w, k;
    int list[50];
    int a, changed, sel;

    changed = 0;
top:
    kbflush();
    sel = 0;
    do {
        w = tab[slot * 3 + 2];
        if ((k = nvar(w, list)) > 0x32)
            printf(0xb24, k);
        u = tab[3 * slot];
        v = tab[3 * slot + 1];
        if ((sel = pickvar(fh, ctx, u, v, list, k,
                           vsel[slot], mark[slot])) != -1) {
            a = sel & 0x7fff;
            if (a != vsel[slot]) {
                changed = 1;
                /* DITULIS ULANG, bukan "= a". Ekspresi yang sama muncul dua
                   kali membuat kompiler meng-CSE-nya dan MEMESAN temp: hasilnya
                   dua spill (nilai ke bp+0, penunjuk ke bp+2) bukan satu.
                   Memakai variabel `a` di sini memberi 380 vs 383 byte. */
                vsel[slot] = sel & 0x7fff;
                ans[slot] = list[sel & 0x7fff];
                ids[slot] = recbase[ans[slot]].id;
            }
            slot++;
            if (slot >= n - 1)
                slot = 0;
        }
    } while (sel >= 0);
    if (sel != -1) {
        switch (clrbot()) {
        case ' ':
            break;
        case 0x0d:
            goto top;
        case 0x1b:
            sel = -1;
            break;
        }
        if (changed == 1 && sel != -1) {
            place(4, recbase, fh, buf, buf2, n, ans, flag);
            changed = 0;
        }
    }
    return sel;
}
