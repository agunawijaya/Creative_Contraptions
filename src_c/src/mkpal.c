/* FUN_1000_3909 @ 1000:3909, 634 byte — BANGUN PALET MEKANISME untuk satu soal.
 *
 * Menyusuri 35 record pertama di `base`, melewati record yang identik dengan
 * pendahulunya (id DAN row sama = bagian lanjutan), lalu untuk tiap record yang
 * lolos: memuat sprite-nya ke buffer dan mencatat nomornya ke `idtab[]`/`spr[]`.
 * Berhenti begitu record berikutnya ber-id 0.
 *
 * Pada pemanggilan PERTAMA (`pass == 0`) daftar dibangun dari nol; pemanggilan
 * berikutnya hanya memuat ulang sprite dan meneruskan hitungan dari `nmech`.
 *
 * Kalau `shufflg == 1`, daftar dikocok lalu di-DEDUP: dua entri dianggap sama
 * kalau id-nya sama, atau kalau KEDUANYA >= 0x8c (objek zany dianggap
 * sekelompok). Entri yang dibuang ditimpa entri terakhir dan `cnt` menyusut.
 * `want` (mekanisme >= 0x8c yang diminta soal) dilindungi: kalau yang mau
 * dibuang justru `want`, ia dipindahkan dulu ke posisi yang dipertahankan.
 *
 *   load()=53ff  rnd()=5a5b
 *   pass @0x71c ; nmech @0x3ac ; lvl3 @0x738 ; base @0x73a ; shufflg @0x794
 *   busy @0x840 ; idtab[] @0x2ea ; spr[] @0x7fa
 *
 * ⭐ NILAI BOOLEAN DIMATERIALISASI. `c1 = (a != b);` dipancarkan sebagai
 *     cmp bx,ax / jne L1 / xor cx,cx / jmp L2 / L1: xor cx,cx / inc cx
 * -- dua cabang yang sama-sama me-nol-kan register, satu lalu `inc`. Kalau
 * melihat pola itu, sumbernya menyimpan HASIL PERBANDINGAN ke variabel int,
 * bukan memakai perbandingan langsung di dalam `if`.
 *
 * PETA SLOT (bingkai 0x20): bp+0..4 = 3 TEMP, lalu
 *   bp+6=i  8=j2  0ah=cnt  0ch=TAK DIPAKAI  0eh=j  10h=id1  12h=id2
 *   14h=r  16h=want  18h=c1  1ah=c2  1ch=ok  1eh=ch
 * Argumen: bp+24h=fh, 26h=buf, 28h=tab, 2ah=n.
 * `r` (bp+14h) diisi tapi tak pernah dibaca — memang begitu di biner asli.
 */

/* base DIPERLAKUKAN SEBAGAI char*, BUKAN struct rec*. Buktinya biner memakai
   SATU register untuk keempat akses record i dan i-1:
       mov si,[base] / add si,ax        (ax = 0xc*i)
       mov al,[si-0ch] ... mov bl,[si] ... mov al,[si-0bh] ... mov bl,[si+1]
   Dengan `base[i].id` / `base[i-1].id` kompiler menghitung DUA alamat terpisah.
   Yang benar adalah CSE PENUNJUK (lihat README): `(base + 0xc*i)[-0xc]`, BUKAN
   CSE offset `base[0xc*i - 0xc]` -- yang kedua tetap menghitung ulang indeks
   dan memberi bingkai 0x22/0x24 alih-alih 0x20. */
extern char *base;          /* @0x73a */
extern int  pass;           /* @0x71c */
extern int  nmech;          /* @0x3ac */
extern int  lvl3;           /* @0x738 */
extern int  shufflg;        /* @0x794 */
extern int  busy;           /* @0x840 */
extern char idtab[];        /* @0x2ea */
extern char spr[];          /* @0x7fa */

mkpal(fh, buf, tab, n)
int  fh;
int  buf;
int *tab;
int  n;
{
    int i, j2, cnt, unused, j, id1, id2, r, want, c1, c2, ok, ch;

    if (pass == 0)
        cnt = 0;
    else
        cnt = nmech;
    want = 0;
    j = 0;
    while (j < n) {
        /* ekspresi DITULIS DUA KALI: itu yang membuat kompiler meng-CSE-nya
           (penunjuk ditahan di temp bp+0) sehingga `want` diisi dari AX tanpa
           menghitung ulang, dan store-nya hanya muncul di cabang break. */
        if (tab[j * 3 + 2] >= 0x8c) {
            want = tab[j * 3 + 2];
            break;
        }
        j++;
    }
    ch = 0;
    for (i = 0; i < 0x23; i++) {
        c1 = ((base + 0xc * i)[0] != (base + 0xc * i)[-0xc]);
        c2 = ((base + 0xc * i)[1] != (base + 0xc * i)[-0xb]);
        ok = (i == 0 || c1 || c2);
        if (ok) {
            for (j = 0; j < n; j++) {
                if (lvl3 != 1 || base[i * 0xc] == tab[j * 3 + 2]) {
                    if (busy != 0)
                        load(fh, base, i, buf);
                    buf = buf + 0xc0;
                    if (pass == 0) {
                        spr[cnt] = ch++;
                        idtab[cnt++] = i;
                    }
                    break;
                }
            }
        }
        if ((base + i * 0xc)[0xc] == 0)
            break;
    }
    if (pass == 0 && shufflg == 1) {
        for (i = 0; i < cnt; i++) {
            r = rnd(cnt);
            id1 = idtab[r];
            idtab[r] = idtab[i];
            idtab[i] = id1;
            /* variabel yang SAMA dipakai lagi (bukan id2). Biner cuma
               memancarkan SATU store ke bp+10h untuk kedua pertukaran:
               store tertunda yang pertama gugur karena ditimpa sebelum
               sempat dipakai. Dua variabel memberi tiga store. */
            id1 = spr[r];
            spr[r] = spr[i];
            spr[i] = id1;
        }
        for (i = 0; i < cnt; i++) {
            id1 = base[idtab[i] * 0xc];
            for (j2 = i + 1; j2 < cnt; j2++) {
                id2 = base[idtab[j2] * 0xc];
                if (id1 == id2 || (id1 >= 0x8c && id2 >= 0x8c)) {
                    if (want != 0 && id2 == want) {
                        idtab[i] = idtab[j2];
                        spr[i] = spr[j2];
                    }
                    /* `cnt` DITURUNKAN LEBIH DULU: store-nya ditunda, jadi
                       nilai barunya masih di AX dan dipakai sebagai indeks
                       (mov si,ax) untuk kedua baris berikutnya. Menaruhnya di
                       akhir memberi "dec word ptr [cnt]" + indeks [si-1]. */
                    cnt = cnt - 1;
                    idtab[j2] = idtab[cnt];
                    spr[j2] = spr[cnt];
                    j2--;
                }
            }
        }
    }
    pass++;
    return cnt;
}
