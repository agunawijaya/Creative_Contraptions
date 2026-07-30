# src_c/JOURNAL.md — jurnal keputusan rekonstruksi source C

Berkas ini menyimpan yang **tidak** tertangkap di tempat lain: alasan di balik
keputusan, jalan buntu beserta sebabnya, dan pertanyaan yang masih menggantung.

Pembagian tugas antar dokumen — jangan tumpang tindih:

| tempat | isinya |
|---|---|
| `src_c/README.md` | ATURAN kompiler MS C 1.04 yang bisa dipakai ulang |
| `src_c/src/*.c` (komentar ujung) | peta slot + "sudah dicoba & gagal" per fungsi |
| `src_c/verify/*.py` | status faktual (jalankan alatnya, jangan percaya angka di dokumen) |
| **berkas ini** | KEPUTUSAN, alasan, dan pertanyaan terbuka |
| `CLAUDE.md` | orientasi sesi baru + langkah berikutnya |

Transkrip mentah percakapan (arsip lengkap, 9,3 MB, bukan untuk dibaca utuh):
`C:\Users\aguna\.claude\projects\C--Projects-Creative-Contraptions\8c43f1f4-0758-4f80-950a-ee3b34cc342e.jsonl`
Pakai hanya kalau butuh menelusuri satu detail spesifik yang tak ada di dokumen —
misalnya urutan eksak eksperimen. Jangan jadikan sumber status.

---

## 2026-07-30 (lanjutan ke-4) — `0x5035` DIMULAI, belum selesai

Commit `95d9cd7` menyimpan tujuh fungsi sesi ini (55,3%). Sesudah itu saya
mulai `0x5035` (739 B, loader CONTRAP) tapi BERHENTI sebelum menulis sumber.
Yang sudah dipetakan, supaya sesi berikutnya tidak mengulang:

**Peta bingkai (0x124 = 292 byte), dari `grep "bp + "` atas disassembly:**
```
bp+0..5      3 TEMP
bp+6         dir[108]  -- directory 216 byte, dibaca read(fh, dir, 0xd8)
                          diakses [bp+si+6] dengan si = i*6, i < 0x24
                          -> 3 kata per entri: {id, off_lo, off_hi}
bp+0deh      i
bp+0e0h,0e2h TIDAK PERNAH DIREFERENSI
bp+0e4h      fh        (hasil open)
bp+0e6h..0f4h  8 lokal lagi (off, pos, tmp, cnt, first, pick, total, expect)
bp+0f6h..123h  46 BYTE TIDAK PERNAH DIREFERENSI  <-- TEKA-TEKI BELUM TERPECAHKAN
bp+128h      argumen ke-1 (nomor varian; -1 = pilih acak)
```

**46 byte di ujung bingkai (bp+0f6h..123h) BUKAN penghalang — koreksi.**
Saya sempat menulis "jangan tulis sumbernya sebelum ini dijawab". Itu SALAH dan
bertentangan dengan aturan 8i di README: ukuran bingkai justru hal yang paling
murah diukur SECARA EMPIRIS — kompilasi sekali, lihat selisih `sub sp` kita vs
0x124, lalu tambah lokal sebanyak selisih/2. Kandidatnya array yang
dideklarasikan tapi tak terpakai (23 int) atau buffer 46 byte; kalau `int`
tak terpakai dibuang kompiler, pakai `char pad[46]` (array selalu dialokasikan,
lihat §"Batas rumus" di README). **Tulis sumbernya, biarkan kompiler menjawab.**

**Global yang perlu nama sebelum mulai** (belum ada di sumber mana pun):
`0x3b2` (sub/goal terpilih), `0x3b4`, `0x3b6`, `0x41a`, `0x41c`, `0x41e`,
`0x422`, `0x4b4`, `0x4b6`, `0x4f2`, `0x3f2`, `0x796`, `0x7be`, `0x7e6`,
`0x1e2e`, `0x1e30`. Struktur berkasnya sudah TERVALIDASI di `CODE_MAP.md`
§"Format file CONTRAP", jadi maknanya tidak perlu ditebak — tinggal dinamai.

Pustaka MC.LIB yang dipanggil: `open()`=6b57, `read()`=6d31, `lseek()`=6e8b,
`close()`=6fb6, `printf()`=6a48.

## 2026-07-30 (lanjutan ke-3) — user bilang "lanjutkan semuanya sekaligus"

Instruksinya: kerjakan semua front sekaligus. Yang dikerjakan: perbaiki hutang
`put()`, lalu terus menggarap fungsi baru.

| fungsi | ukuran | putaran | hasil |
|---|---|---|---|
| `runfill` (0x2d11) | 383 | 4 | COCOK byte-per-byte |
| `mkpal` (0x3909) | 634 | 5 | COCOK byte-per-byte |

Total sesi (tiga putaran): **7 fungsi, 3.207 byte**. 9.754 → **10.771 byte
kode C** (37,5% → 41,4%), TOTAL **55,3%**. DATA tetap 100%, link tetap bersih.

### Hutang yang DIBAYAR

**`put()` yang menunjuk dua alamat sudah dipecah.** Dibuktikan dulu dengan
melihat target `call` sungguhan: `shuffle`/`askopts` memanggil 0x65e0,
`xform`/`bounce` memanggil 0x6524 — dua rutin assembly berbeda dengan prolog
yang sama. Sekarang `put` = 0x65e0, `putmsk` = 0x6524. Ketiga berkas yang
sudah cocok tetap cocok sesudah rename (target `call` memang slot relokasi).

### Tiga aturan kompiler baru (semua dari `mkpal`)

1. **Nilai boolean yang DISIMPAN** (`c = (a != b);`) punya tanda tangan khas:
   dua cabang yang sama-sama `xor reg,reg`, satu diikuti `inc`.
2. **Store tertunda yang ditimpa akan GUGUR.** Dua pertukaran yang memakai
   variabel temp SAMA memancarkan satu store, bukan dua.
3. **Urutan `cnt = cnt - 1`** menentukan bentuk: ditulis LEBIH DULU →
   `mov ax,[cnt]/dec ax/mov si,ax` + store ditunda; ditulis di akhir →
   `dec word ptr [cnt]` + indeks `[si-1]`.

Plus satu dari `runfill`: **menulis ULANG ekspresi (bukan memakai variabel
penampungnya) MEMESAN temp** — 380 vs 383 byte. Ini kebalikan dari aturan CSE
yang sudah ada, dan sekarang keduanya berdampingan di README.

### Kesalahan saya yang memakan putaran

**Di `mkpal` saya melewatkan aturan yang SUDAH ADA di rulebook sendiri**
(§"CSE: yang dipakai ulang itu PENUNJUK atau OFFSET?"). Saya menulis
`base[0xc*i - 0xc]` (CSE offset) dua putaran berturut-turut sebelum sadar
yang benar `(base + 0xc*i)[-0xc]` (CSE penunjuk). Bingkai turun 0x24 → 0x22 →
0x20 dan panjang langsung tepat begitu bentuknya dibetulkan.
**Pelajaran: sebelum menebak, baca ulang rulebook untuk pola yang mirip.**

### Catatan jujur

- `mkpal`: `r` (bp+14h) dan satu lokal di bp+0ch diisi/dialokasikan tapi tak
  pernah dibaca. Ada di biner asli.
- `runfill`: `u`/`v`/`w` (bp+8/0ah/0ch) sama — cuma menampung nilai argumen.
- `runfill` memanggil `clrbot()` yang SELALU mengembalikan 0x20, jadi cabang
  ESC/Enter di switch-nya tidak pernah tercapai di biner asli. Jangan
  "diperbaiki".
- Dua global baru butuh regenerasi `gdata.c` (`gendata.py`) sebelum link —
  kalau lupa, LINK melaporkan "Unresolved Externals" dan itu satu-satunya
  gejalanya.

## 2026-07-30 (lanjutan ke-2) — tiga fungsi lagi, tembus 52,5%

| fungsi | ukuran | putaran | hasil |
|---|---|---|---|
| `setmark` (0x10fd) | 259 | **1** | COCOK byte-per-byte |
| `setzany` (0x1200) | 282 | **1** | COCOK byte-per-byte |
| `bounce` (0x2504) | 398 | 2 | COCOK byte-per-byte |

8.815 → **9.754 byte kode C** (33,9% → 37,5%), TOTAL **52,5%**. Nol probe baru
dibutuhkan: 20 aturan yang ada sudah cukup.

### Yang menarik

**Dua kembar lagi.** `setmark`/`setzany` berbagi 94 byte ekor yang identik
byte-per-byte — pola duplikasi sumber yang sama seperti `show`/`setsel`.
Setelah yang pertama cocok, yang kedua tinggal menyalin dan mengganti pembuka
plus satu syarat. **Kalau menemukan fungsi yang ekornya mirip fungsi lain,
cek dulu apakah itu kembaran — biayanya bisa turun drastis.**

**`bounce` mengungkap aturan ukuran yang halus.** Divergensi 1 byte-nya bukan
soal bentuk logika sama sekali, melainkan URUTAN penugasan global: store dari
AX memakai bentuk akumulator 3 byte, dari register lain 4 byte. Menaruh satu
penugasan immediate lebih dulu menggeser nilai keluar dari AX. Aturannya sudah
masuk README; cara membacanya = ikuti urutan PEMUATAN REGISTER, bukan urutan
store.

**Bentuk tabel switch ada dua.** `bounce` memakai tabel RAPAT (indeks 0..3,
1 kata per case) sedangkan `runmenu`/`review` memakai tabel JARANG
((nilai,label), 2 kata). Yang rapat TIDAK membalik urutan case. Sudah di README.

### Hutang yang ditemukan (bukan dibuat sesi ini)

**`put()` menunjuk dua alamat berbeda.** `xform.c` mendokumentasikan
`put()=6524`, `shuffle.c`/`askopts.c` mendokumentasikan `put()=65e0`. Karena
keduanya cuma satu stub, LINK menyatukannya — jadi salah satu pemanggilan
pasti salah di `.EXE`. Tidak berpengaruh ke pencocokan per-fungsi (target
`call` adalah slot relokasi yang di-wildcard), tapi harus dipecah jadi dua nama
sebelum `.EXE` dipakai. **Saya sengaja TIDAK memperbaikinya sekarang**: itu
menyentuh tiga berkas yang sudah cocok, dan tanpa cara menjalankan `.EXE`
belum ada cara memverifikasi perbaikannya.

### Catatan jujur

- `bounce`: lokal di `bp+6` **tidak pernah dipakai** dan `byc` (bp+10h) diisi
  tapi tak pernah dibaca. Keduanya ada di biner asli.
- `setmark`/`setzany`: `arr[0]` bukan elemen daftar melainkan pencacah gagal;
  slot ke-i ada di `arr[i+1]`. Gampang salah baca dari disassembly.

---

## 2026-07-30 (sesi lanjutan) — `runmenu` + `review` tuntas, tembus 50%

### Hasil

| fungsi | ukuran | putaran kompilasi | hasil |
|---|---|---|---|
| `runmenu` (0x34cc) | 547 | 3 + 1 probe | COCOK byte-per-byte |
| `review` (0x3c4f) | 704 | 4 + 3 probe | COCOK byte-per-byte |

Total naik 7.564 → **8.815 byte kode C** (29,1% → 33,9%), TOTAL **50,0%**.
Segmen DATA tetap 100%, link tetap bersih (54 `.OBJ`).

### Keputusan dan alasannya

**1. Menuruti rekomendasi sesi lalu: garap fungsi BARU, bukan near-miss.**
Terbukti tepat, dan selisihnya besar. Dua fungsi terbesar yang pernah ditutup
sejauh ini (547 dan 704 byte) selesai dalam satu sesi, sementara empat putaran
sesi sebelumnya di `place`/`nvar` menghasilkan nol byte. Alasannya bukan
kebetulan: 17 aturan yang sudah ada memang menutup hampir seluruh fungsi baru
sejak percobaan pertama — `runmenu` meleset 3 byte dari 547 di kompilasi
PERTAMA, `review` 2 byte dari 704 di kompilasi kedua.

**2. Probe dipakai untuk tiap pertanyaan bentuk, bukan tebak-tebakan.**
Tiga probe baru, ketiganya menjawab dalam satu kompilasi:
- `probe8.c` — 6 varian; menemukan `default: break;` sebagai satu-satunya
  penyebab jmp back-edge tersendiri di ujung switch.
- `probe9.c` — 6 varian, SEMUANYA GAGAL. Hasil negatif yang berguna: bentuk
  `if (cond) goto L;` tidak pernah menahan nilai global di AX, apa pun bentuk
  pembanding/konsumennya.
- `probe10.c` — 3 varian; `if (!cond) { blok } goto L;` berhasil, dan varian
  ke-3 membuktikan perantaian lompatan batal kalau ada pernyataan di antara
  `}` dan `goto`.

**3. `truesize.py` TIDAK boleh dipercaya untuk fungsi ber-switch.**
Dua-duanya dilaporkan jauh lebih kecil (497 vs 547; 650 vs 704) karena masih
ada back-edge + tabel + loop pencari SESUDAH epilog terakhir. Ini pengulangan
pelajaran lama ("jangan percaya `size=` di functions.txt") pada alat yang
kita tulis sendiri. Aturannya sudah masuk README; `truesize.py` sendiri belum
diperbaiki — itu hutang kecil yang belum dibayar.

### Jalan buntu yang sebabnya sudah dipahami

- **`review`, CSE nilai global.** Tiga putaran saya kira penyebabnya `else`
  eksplisit atau urutan operan pembanding. Salah — `probe9.c` membuktikan enam
  bentuk `if (cond) goto` semuanya memuat ulang dari memori. Pemicunya bukan
  bentuk UJI-nya melainkan apakah kode sesudahnya ada di cabang TRUE.

### Hal yang belum tuntas / pertanyaan terbuka

1. **`t` dan `addr` di `review` diisi tapi tak pernah dibaca** (3 tempat). Itu
   memang ada di biner asli. Ditulis apa adanya sebagai lokal; kemungkinan
   penulis aslinya menulis sesuatu yang lain dengan efek sama.
2. **Dua stub assembly baru**: `shftl` (0x5dce) dan `shftr` (0x6600), primitif
   geser layar. Menambah hutang assembly di luar ±1.200 byte yang sudah
   dicatat — angka itu perlu dihitung ulang.
3. Pertanyaan dari sesi lalu **masih belum dijawab user**: prioritas
   volume vs ketuntasan, apakah assembly bagian dari target, dan apakah
   "`.EXE` bisa dijalankan" jadi tonggak tersendiri.

---

## 2026-07-30 — sesi panjang: dari "42 pecahan" jadi .EXE yang ter-link

### Keputusan besar dan alasannya

**1. Bikin harness LINK sebelum melanjutkan rekonstruksi.**
Alasan: 42 fungsi terverifikasi tapi tak ada bukti semuanya konsisten satu sama
lain. Link membuktikan tak ada simbol menggantung / definisi ganda, DAN membuka
cara mengukur segmen DATA dari artefak yang sebenarnya. Terbukti tepat: langsung
menemukan `.OBJ` basi (`rnd.OBJ` peninggalan probe) yang menyembunyikan bahwa
`rnd` belum direkonstruksi, dan menemukan geseran 4 byte DGROUP yang membuat
`gdata.OBJ` "cocok 100%" padahal hasil link-nya salah 5.821 byte.

**2. Bikin `libmatch.py` sebelum menggarap fungsi berikutnya.**
Alasan: batas wilayah pustaka masih taksiran (0x6a48), dan beberapa "stub" terasa
seperti rutin pustaka. Hasilnya membatalkan pekerjaan sia-sia: lima nama tebakan
saya SALAH, dua di antaranya menunjuk fungsi yang sama, dan 9.935 byte terbukti
datang gratis dari `MC.LIB`. Pelajaran umum: **sebelum menulis stub, buktikan
dulu itu bukan rutin pustaka.**

**3. Menutup near-miss lebih dulu, bukan menggarap fungsi baru.**
Ini keputusan saya, dan **hasilnya tidak seimbang**. Empat putaran terakhir
menghasilkan empat aturan kompiler baru tapi NOL byte tambahan, karena `place`
dan `nvar` berhenti di dinding alokasi register/temp. Rekomendasi saya untuk
sesi berikutnya: **balik urutannya** — garap `runmenu`/`review` yang belum
tersentuh, di mana 17 aturan yang ada bisa dipakai dari awal, lalu kembali ke
near-miss dengan mata segar. `drawpair` dulu juga begitu: tutup setelah
ditinggal sebentar dan didekati dari bentuk akses, bukan dari menebak varian.

**4. Menandai satu byte `load` sebagai artefak kompiler, bukan memaksanya cocok.**
Alasan: sudah dibuktikan byte itu tak ditentukan sumber C (sumber identik memberi
nilai berbeda tergantung panjang nama berkas). Supaya angka tetap jujur,
`manifest.txt` diberi kolom `art=N` dan `verifyall.py` melaporkannya TERPISAH,
tidak dihitung cocok. **Aturan tegas: `art=` hanya boleh dipakai kalau ada bukti
setingkat itu** — bukan untuk menutupi byte yang belum dipahami. `place` yang
sisa 2 byte SENGAJA tidak ditandai `art=`, karena itu akibat bentuk sumber saya.

### Jalan buntu yang sebabnya sudah dipahami (jangan ulangi dari nol)

- **`nvar`**: tiga putaran saya kira penyebabnya bentuk `cnt++`. **Salah.** Probe
  yang meniru fase 2 persis tapi dengan pembanding sederhana menghasilkan kode
  yang benar, dan ukurannya tak berubah walau bingkai dibesarkan. Pemicunya
  ekspresi bersarang `recbase[list[r]].row`. Detail di `src/nvar.c`.
- **`place`**: sisa 2 byte murni pilihan register (SI vs DI). Sepuluh varian
  dicatat di `src/place.c`. Yang paling informatif: menjadikan `sp` bertipe
  `char *` dari awal MERUSAK fase 1 yang tadinya cocok sempurna — jadi tipe
  `struct slot *` memang benar.
- **Menebak varian satu-satu itu mahal.** Yang berhasil justru probe terkendali
  (rulebook §"Teknik: pakai PROBE"). Dua dari empat aturan baru sesi ini lahir
  dari probe, bukan dari iterasi fungsi penuh.

### Peristiwa yang mengubah cara kerja

User bertanya *"apakah semua pengalaman kamu sudah disimpan?"* — dan itu
menemukan **empat celah** yang saya tidak sadari:

1. `DECOMPILE_PLAN.md` masih memuat angka pustaka yang sudah terbantah
   (41 fungsi / 6.951 byte / target 24,5 KB).
2. `CODE_MAP.md` memberi nama SALAH untuk rutin pustaka — `FUN_1000_6e8b`
   tercatat 4 argumen, padahal itu `lseek(fh, long, mode)` = 3 argumen.
3. Satu aturan ("hanya perubahan TIPE yang mematahkan CSE") cuma ada di komentar
   `place.c`, belum di rulebook.
4. **Tujuh berkas masih berjudul "⏳ BELUM COCOK" padahal sudah cocok** —
   informasi terbantah yang paling berbahaya karena terlihat otoritatif.

Semuanya sudah dibenahi. **Kebiasaan baru: tiap kali menutup fungsi atau
menemukan aturan, periksa juga apakah ada angka/nama di dokumen lain yang jadi
terbantah.** Tandai terbantah, jangan hapus, dan sebut alat pembuktinya.

### Pertanyaan yang masih menggantung untuk user

1. **Prioritas: volume atau ketuntasan?** Saya sarankan volume dulu
   (`runmenu`/`review`). Belum ada keputusan user.
2. **Assembly (±1.200 byte)** butuh MASM, nol dikerjakan. Belum dibahas apakah
   itu bagian dari target atau boleh ditinggal.
3. **`.EXE` belum bisa dijalankan** (`main` + 20 stub kosong). Belum dibahas
   apakah "bisa dijalankan" jadi tonggak tersendiri sebelum 100% byte-identical.
