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

## 2026-07-31 — `pickvar`: misteri Ghidra terpecahkan; ada BLOK MATI ~200 byte

Kondisi mustahil `if (param_7 + 0x141 != param_7)` yang saya peringatkan
kemarin sekarang **sepenuhnya terjelaskan**. Ia berasal dari DUA perbandingan
nyata di 0x4500..0x4519:

```
mov bx,[bp+0Ah] ; cmp bx,ax ; jne .. ; jmp 4713   ->  if (q == idx) goto L4713;
add ax,141h     ; cmp ax,bx ; jne .. ; jmp 45DD   ->  if (idx+141h != q) {...}
```

Karena `q = idx + 141h` diset di 0x439C, syarat pertama SELALU salah dan yang
kedua SELALU salah. Akibatnya **blok 0x451A..0x45DC (~200 byte) tidak pernah
tercapai** di biner asli. Ghidra melipat keduanya jadi satu syarat mustahil.

⚠ Blok mati itu **tetap harus direproduksi byte-per-byte** — byte-nya ada di
biner. Ini bukti KEDUA (sesudah bug `load` @0x53ff+134) bahwa biner ini memuat
kode yang tidak pernah jalan. Pola umumnya: kalau Ghidra melaporkan blok
tak-terjangkau ATAU syarat yang mustahil, jangan "diperbaiki" — cari
perbandingan aslinya di disassembly dan tulis apa adanya.

### Empat bentuk penulisan akses record yang terbukti

Diukur satu per satu di `pickvar`, dan semuanya berlaku umum:

1. **`recbase` dideklarasikan `char *`**, bukan `struct rec *` lalu di-cast.
   Dengan cast, kompiler memuat basis ke DX dulu (`mov dx,[73Ch] / mov si,dx`)
   — 2 byte berlebih di TIAP akses. Sisi yang butuh struct di-cast BALIK.
2. **Sisi kiri char-pointer + sisi kanan struct** memutus CSE atas `recbase`:
   biner memuatnya DUA KALI, bukan sekali lalu dipakai ulang.
3. **Bentuk penunjuk** `(... + basis)[1]`, bukan offset `basis[... + 1]`.
4. **Urutan operan** `(0xc*idx + basis)` — basis dimuat SESUDAH perkalian.

### Jebakan peta slot

`bp+08h` itu **temp kelima**, bukan lokal. Temp menempati bp+00..09, lokal
mulai bp+0Ah. Daftar "slot tidak terpakai" yang saya susun sendiri
(00 08 14 22 4E) MENYESATKAN — 00 dan 08 itu temp yang kebetulan tak dipakai.
Memberi pengganjal di 08h menggeser SELURUH slot dan membuat bingkai 54h.

### Teknik: pengganjal temp bertahap

Jumlah temp TUMBUH seiring badan fungsi ditulis, jadi selama badan belum
lengkap bingkai kurang dan semua slot bergeser — tak ada divergensi yang bisa
dibaca. `char tpad[]` di depan menutup selisih itu dan dikecilkan tiap kali
menambah kode (6 → 4 → 0). Tanpa ini, fungsi 1.730 byte praktis tak bisa
didiagnosa.

### Status pickvar

543 byte draf, 256 cocok, divergensi pertama +231. Sisa diagnosis: dengan
geseran +3 byte blok 240..249 cocok instruksi demi instruksi — strukturnya
benar, kurang satu spill `[bp+2] = si`. Empat urutan penugasan k/k2 sudah
diukur dua kali; semuanya tercatat di ujung `src/pickvar.c`.

## 2026-07-30 (lanjutan ke-6) — ASSEMBLY TUNTAS; stub tinggal dua

MASM 1.27 dipasang di sesi ini juga (lihat entri sebelumnya). Hasil akhir
jalur assembly: **11 modul, 2.379 byte, semuanya cocok byte-per-byte.**

| modul | alamat | byte | modul | alamat | byte |
|---|---|---|---|---|---|
| blit | 0x672f | 314 | text | 0x644a | 218 |
| snd2 | 0x5b57 | 356 | fillrec | 0x6869 | 208 |
| blitmsk | 0x6524 | 326 | shftl | 0x5dce | 109 |
| prep | 0x6939 | 271 | vbio | 0x5d98 | 54 |
| snd1 | 0x5a5b | 252 | keyio | 0x66fd | 50 |
| line | 0x5cbb | 221 | | | |

### Lima jebakan MASM 1.27 (semuanya otomatis di asmgen.py sekarang)

1. capstone memakai nama mnemonik 32-bit walau CS_MODE_16; `cdq` harus `CWD`.
   Kalau tidak, instruksinya **dilewati diam-diam**.
2. Kurung berisi konstanta murni ditafsirkan `[BP+konst]`; alamat absolut
   wajib `DS:[...]`.
3. Deteksi register butuh batas kata: `212CH` mengandung "CH".
4. MASM memesan 3 byte untuk `JMP` maju lalu mengisi sisanya `NOP`; paksa
   `SHORT` kalau aslinya 2 byte. **Penyebab tersering modul meleset panjang.**
5. MASM memendekkan imm16 yang muat di int8 (opcode 81 -> 83). Tidak ada
   sintaks untuk memaksanya; asmgen memancarkan `DB` khusus kasus itu.
Plus: instruksi string harus telanjang, berkas wajib CRLF, dan masm.ps1 HARUS
memeriksa jumlah error -- MASM tetap menulis .OBJ walau ada error.

### Delapan stub hilang TANPA menulis kode

Ini pola yang berulang tiga kali dan layak jadi kebiasaan:
- **di dalam modul yang sudah cocok**, hanya belum diekspor: `rdkey` (0x6853,
  di dalam blit), `refresh` (0x5c84, di dalam snd2), `sndoff`/`sndon`
  (0x5a74/0x5a76, di dalam snd1), `tone3` (0x5b73, di dalam snd2)
- **rutin MC.LIB**: `fmtnum` ternyata `sprintf` @0x7464
- **alamat yang sama dengan fungsi lain**: `drawitem` = `load` @0x53ff

**Sebelum menulis stub baru: (a) cek libmatch.py, (b) cek apakah alamatnya
jatuh di dalam modul yang sudah ada, (c) cek apakah alamatnya sama dengan
fungsi yang sudah bernama lain.**

### `pickvar` (0x42ca) — PERINGATAN sebelum ada yang menulisnya

Selain 9 blok tak-terjangkau, pseudo-C Ghidra memuat:

    if (param_7 + 0x141 != param_7) { ... }

Syarat itu **selalu benar** — mustahil ditulis begitu di sumber. Ini pola yang
sama dengan bug `load` (0x53ff+134): kompiler memancarkan instruksi yang
MERUSAK FLAG sehingga lompatan sesudahnya selalu diambil, dan Ghidra
memodelkannya sebagai perbandingan yang tidak masuk akal. Lihat README
Sec."BATAS KERAS PERTAMA".

Konsekuensinya: **jangan menulis pickvar dari pseudo-C.** Kerjakan dari
disassembly, dan curigai ada blok yang di biner asli TIDAK PERNAH TERCAPAI --
jangan "diperbaiki" supaya masuk akal.

Peta bingkai (dari sesi sebelumnya): `sub sp,0x52`, 8 argumen di bp+56h..64h,
36 slot lokal terpakai, tidak terpakai: 00 08 14 22 4e.

## 2026-07-30 (lanjutan ke-5) — `runplay` tuntas; `0x42ca` baru diintai

**`runplay` (0x5505, 964 B) COCOK byte-per-byte** — fungsi terbesar yang
tertutup sejauh ini. 11.735 byte kode C (45,1%), TOTAL **57,9%**.

Delapan temuan menutupnya; tiga di antaranya berlaku umum dan sudah masuk
kebiasaan kerja:
1. **Jumlah argumen dari Ghidra tidak bisa dipercaya.** `review()` dipanggil
   dengan 6 argumen (Ghidra menampilkan 7), `pickvar()` dengan 7 di sini tapi
   8 di `runfill`. HITUNG PUSH-nya di biner, jangan percaya tanda tangan.
2. **Argumen ke-8 `pickvar` menciptakan CSE atas `3*slot`** yang mengubah
   bentuk perkalian dari "mov ax,3 / imul [slot]" jadi bentuk offset. Argumen
   yang kelebihan bukan cuma sia-sia — ia mengubah kode di sekitarnya.
3. **`p2` bertipe `char`**, terbaca dari "mov al,[bp+8ah] + xor ah,ah" di tiap
   pemakaian. Ghidra menandainya `byte` dan saya mengabaikannya satu putaran.

### `0x42ca` — pengintaian, BELUM ditulis

Ukuran sebenarnya **1.730 byte** (bukan 1.517 dari functions.txt).

```
sub sp,0x52        bingkai 82 byte
argumen  : bp+56h..64h = 8 argumen
slot lokal terpakai (36 buah):
  02 04 06 0a 0c 0e 10 12 16 18 1a 1c 1e 20 24 26 28 2a 2c 2e
  30 32 34 36 38 3a 3c 3e 40 42 44 46 48 4a 4c 50
slot TIDAK terpakai: 00 08 14 22 4e
```

⚠ Ghidra hanya menamai 16 lokal padahal ada ~40 slot, DAN melaporkan
**9 blok tak-terjangkau** (0x1451a, 0x14566, 0x14580, 0x14585, 0x14588,
0x1459c, 0x145a2, 0x145a5, 0x1471b). Artinya pseudo-C-nya jauh kurang bisa
dipercaya daripada fungsi-fungsi sebelumnya — kemungkinan besar ada pola
seperti bug `load` (kompiler merusak flag) yang membuat cabang mati.

**Saran urutan:** kerjakan dari disassembly langsung, bukan dari pseudo-C.
Mulai dengan memetakan mana dari 36 slot itu yang lokal sungguhan vs temp,
memakai cara yang sama seperti `runplay`: tulis kerangka, cocokkan `sub sp`,
lalu kejar divergensi pertama.

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

---

## Sesi 2026-07-30/31 (semalaman, otonom lewat `/loop`)

User tidur dan meminta pekerjaan diteruskan tanpa henti, dengan protokol
anti-thrashing yang ia setujui. Yang berikut ini terjadi tanpa pengawasan;
semua angkanya bisa diaudit dari `git log --oneline`.

### Hasil utama: `pickvar` (0x42ca, 1.730 byte) dari 275 -> 1.616 byte sejajar

Ditulis blok demi blok dari disassembly. Yang mengubah segalanya bukan menulis
lebih banyak kode, melainkan **mengganti cara mengukur**.

### ⚠ PELAJARAN TERMAHAL: metrik "byte cocok per POSISI" itu MENYESATKAN

Selama berjam-jam saya mengukur kemajuan dengan menghitung byte yang sama di
posisi yang sama. Itu hanya sahih kalau panjang draf SUDAH persis. Begitu ada
satu sisipan, seluruh sisa berkas bergeser dan byte yang sebenarnya benar
terhitung salah.

Buktinya telak: satu perubahan menurunkan angka posisi 392 -> 386 **tapi**
menaikkan angka penjajaran 684 -> 704. Kalau saya percaya angka posisi,
perubahan yang BENAR akan saya buang. Di akhir sesi `pickvar` menunjukkan
POSISI 368 padahal 1.616 byte benar-benar sejajar.

Alatnya sekarang ada di repo: **`python src_c/verify/aligncmp.py <nama>`**
(dan `--sbs <alamat> <n> <geseran>` untuk banding berdampingan). Keluarannya
juga menyebut DI ALAMAT MANA panjang mulai menyimpang — itu yang menunjuk blok
berikutnya yang harus digarap, jauh lebih berguna daripada satu angka total.

### Aturan kompiler baru (semuanya sudah masuk `src_c/README.md`)

1. **Akses record selalu bentuk PENUNJUK** `(idx * 0xc + basis)[n]`.
   Bentuk offset `((char*)basis)[idx*0xc+n]` memuat basis DUA KALI (+15 byte
   sekali kena). Bentuk struct `((struct rec*)basis)[idx].f` memuat basis dini
   ke DX lalu men-spill-nya (+6 byte, dan bisa membengkakkan bingkai).
2. **KOREKSI catatan saya sendiri.** Saya pernah menulis "sisi kanan harus
   bentuk struct supaya CSE atas recbase putus". Itu KELIRU. Kedua sisi bentuk
   penunjuk; yang membedakan hanya URUTAN OPERAN perkalian:
   `0xc * list[i]` -> `mov ax,0Ch / imul word ptr [bx]` sedangkan
   `k * 0xc` -> `mov ax,cx / mov dx,0Ch / imul dx`.
3. **`if (--x < 0)` != `x--; if (x < 0)`.** Yang kedua memakai ulang flag DEC
   (`jge`, 2 byte lebih pendek); aslinya `test ax,ax` + `jns`, dan itu hanya
   keluar dari bentuk pre-decrement di dalam syarat.
4. **SWITCH JARANG: tabel nilai/label disusun KEBALIKAN urutan sumber.**
   Pemindai mulai dari entri TERAKHIR (`si=18h`, `sub si,4`, `jns`). Jadi
   urutan `case` di sumber = urutan ALAMAT badannya, dan tabel dibaca mundur.
   Tanpa aturan ini urutan case pasti tertukar.
5. **`idx == q` bukan `q == idx`** — operan kiri dimuat lebih dulu dan dipakai
   ulang di perbandingan berikutnya.
6. **Jangan menganggap slot yang belum dikenali itu "pengganjal".** Di
   `pickvar` LIMA kali berturut tebakan pengganjal ternyata variabel nyata.
7. **Kalau dua blok terlihat kembar, ukur DUA-DUANYA.** 0x4455 dan 0x46A0
   tampak identik tapi yang kedua menyimpan empat sudut ke slot dulu.
   Sebaliknya 0x4713 memang duplikat byte-per-byte dari 0x46CD — 68 byte
   gratis.

### Bug NYATA yang ditemukan di alat verifikasi sendiri

- **`symcheck` melaporkan 18 BEDA PALSU.** Ia memetakan nama simbol dari NAMA
  BERKAS di manifest, padahal satu modul assembly bisa memuat beberapa fungsi:
  modul `text` mulai di 0x644a tapi simbol `text` sebenarnya di **0x6453**
  (0x644a itu pembungkus INT 10h terpisah). Sekarang alamat diambil dari
  rekaman PUBDEF `.OBJ`, dan pemadanan nama tidak peduli besar-kecil huruf
  (MASM memancarkan HURUF BESAR, berkas `.c` huruf kecil). 24 -> 6 beda.
- **0x644a tidak pernah punya nama** — asmgen menamainya otomatis `F644A`.
  Baru ketahuan saat `main` mulai digarap, karena hanya `main` yang
  memanggilnya. Sekarang bernama `bios10`.

### `main` (0x0082, 4.219 byte) — draf dimulai, peta bingkai TERVALIDASI

⭐ **Temuan arsitektur:** hampir semua tabel besar game ini hidup di **bingkai
tumpukan `main`**, bukan di DGROUP. `recbase`, `base`, `objtab`, `level_`,
`ytop_` semuanya diisi di 0x00B5..0x00E4 dengan alamat lokal `main`. Itu
menjelaskan kenapa DGROUP cuma 9.556 byte: bingkai `main` sendiri
**0x6F96 = 28.566 byte**.

Peta bingkai diukur dari seluruh 4.219 byte disassembly: 12 penyangga + 4 int
+ dua celah 4 byte tak terreferensi. Ukurannya saling menguatkan dengan temuan
lain: `recbase` = 1.500 byte = **125 record x 12**, dan itu cocok dengan batas
`k2 > 0x78` (120) yang ditemukan terpisah di `pickvar`.

Verifikasi: `sub sp` kita 0x6F90 vs 0x6F96 — selisih **persis 6** = temp yang
belum tumbuh (kita 2 byte, aslinya 8). Bagian LOKAL sudah benar seluruhnya.

### Yang SENGAJA tidak dikerjakan (butuh keputusan user)

- **`gendata.py` membuang alamat DGROUP 0..3.** Penyaringnya `START <= a`
  dengan `START = 4`, padahal `a` itu alamat DGROUP sedangkan START offset
  DATA. Akibatnya simbol di DGROUP:0000 tidak pernah terbit, dan instruksi
  `mov bx,[0]` di `main` (0x00B9) belum bisa ditulis — biayanya 7 byte.
  **Tidak saya perbaiki** karena menyentuh penataan DGROUP yang sekarang 100%
  cocok (9.556/9.556). Ini keputusan user.
- **0x846 bernama `mode_`** padahal isinya pegangan berkas dari `open()`.
  Nama menyesatkan; tidak diganti karena aturan "satu alamat satu nama".

### Sisa `pickvar` (tidak tuntas)

TERJAJAR 1.616/1.730 (93,4%), panjang 1.726 vs 1.730. Tiga titik geseran:
`+3 @0x43B8` (aslinya memancarkan spill `mov [bp+2],si` yang tidak kita
keluarkan — di kemunculan KEDUA spill yang sama sudah keluar, jadi bedanya
tekanan register), `+1 @0x4515`, `+4 @0x495A`. Daftar "sudah dicoba & gagal"
lengkap ada di ujung `src_c/src/pickvar.c`, kini diukur dengan metrik
penjajaran (angka lama berbasis posisi dibuang karena tidak sebanding).

---

## Sesi 2026-07-31 (lanjutan semalaman, otonom)

Kelanjutan sesi sebelumnya. Semua angka bisa diaudit dari `git log --oneline`.

### Hasil terukur

| | awal sesi | akhir sesi |
|---|---|---|
| fungsi COCOK byte-per-byte | 68/72 | **72/79** |
| byte terverifikasi | 14.149 | **14.412** |
| TOTAL | 64,5% | **65,2%** |
| DATA (DGROUP) | 100% | 100% (tak tersentuh) |
| stub tersisa | 2 | **1** (`animvm`) |

`main` (4.219 B) selesai DITULIS seluruhnya — dari stub kosong jadi 4.182 byte
dengan TERJAJAR 2.682. **Belum byte-exact**, jadi tidak dihitung COCOK.
`pickvar` 1.726/1.730 byte, TERJAJAR 1.616, cacat nyata tinggal DUA.

Empat fungsi baru COCOK penuh: `f2fde` (66 B), `f171f` (114 B), `f15d0` (80 B),
`setup` (3 B). Tiga draf: `f498c` 162/165, `f278e` 141/149, `f2714` 62%.

### Alat baru

- **`aligncmp.py`** — metrik PENJAJARAN. Menghitung "byte cocok per POSISI"
  menyesatkan begitu panjang draf bergeser: satu perubahan menurunkan angka
  posisi 392→386 tapi menaikkan penjajaran 684→704, dan yang kedua yang benar.
- **`fixorder.py`** — verifikasi identitas simbol untuk fungsi yang **belum**
  byte-exact, sesuatu yang `symcheck` tidak bisa. Hasil pertama: `pickvar`
  49 slot cocok / 0 beda (sebelumnya nol terverifikasi).

### ⚠ Lubang verifikasi yang ditemukan (dan sebagian ditutup)

**Metrik penjajaran BUTA terhadap identitas simbol** — slot relokasi adalah
wildcard, jadi `mov [a],ax` dan `mov [b],ax` bytenya identik. Dibuktikan
dengan membalik urutan enam penugasan: byte SAMA PERSIS, simbol berbeda
total. `symcheck` melewati fungsi yang belum eksak, jadi `main`/`pickvar`/
`place`/`nvar`/`loadcon` **belum terverifikasi identitas simbolnya** sampai
`fixorder.py` dibuat.

### ⚠ Dua temuan AKUNTANSI (angka lama terbantah)

1. **1.200 byte NOL di 0x5F93..0x6442** — bukan kode. Target rekonstruksi mana
   pun yang menghitung seluruh wilayah `<0x69d7` sebagai kode game **terlalu
   besar 1.200 byte**. Persentase sebenarnya lebih tinggi dari yang dilaporkan.
2. **Wilayah 0x2714..0x29B0 (668 byte, ≥3 fungsi) baru ditemukan** lewat sisir
   sasaran `call` — sebelumnya tidak ada di peta mana pun.

### Aturan kompiler baru (semua sudah di `src_c/README.md`)

1. **Fungsi tanpa prolog `push bp` tidak mungkin dari C** — tulis `.asm`.
   `setup` aslinya 3 byte; C memberi 7.
2. **Ukuran fungsi jangan ditebak dari jarak ke entri manifest berikutnya.**
   `setup` diperkirakan ≤1.210 byte, nyatanya 3.
3. **Bingkai:** kompilasi DULU tanpa pengganjal → kurang: tambah pengganjal
   supaya slot TERLIHAT jatuh benar; lebih: ekspresi menuntut temp berlebih.
4. **Tipe deklarasi menentukan bentuk pengalamatan**, bukan cuma ukuran:
   `int arr[20]` → indeks langsung; `char arr[40]`+cast → hitung penunjuk.
5. **Akses record — DIPERBAIKI**: sekali pakai → penunjuk-char; penunjuk yang
   DISIMPAN dan dipakai berkali-kali → **bentuk struct**. Sebelumnya saya
   menyamaratakan keduanya, dan itu membuat `f278e` meleset dari 94,6% ke 14%.
6. **Urutan `case` di sumber = urutan ALAMAT badan case** — berlaku di KETIGA
   bentuk switch termasuk RANTAI (menaikkan penjajaran 47 byte di `main`).
7. **Ambang tanda adalah sifat FIELD, bukan fungsi** — dalam satu fungsi bisa
   ada byte tanpa pemulihan tanda DAN byte dengan ambang 0xC8 (bukan 0x80).
8. **`char x[2]` tak terpakai DIBUANG** kompiler; `char x[3]`/`[4]` dialokasikan.
9. **Post-increment TIDAK bisa digeneralisasi**: `f278e` butuh satu-ekspresi
   `*(char*)p++`, `f2714` justru butuh dua-pernyataan dengan muat-ulang.
   Lihat apakah biner menaikkan MEMORI atau REGISTER.

### Jebakan alat

- `buildall.ps1` hanya mengompilasi modul di `manifest.txt` — `gdata.c` dan
  `stubs.c` harus dikompilasi manual.
- `link.ps1` menautkan SEMUA `.OBJ` di `out/`, bukan hanya yang di manifest.
- `symcheck` memetakan nama dari NAMA BERKAS; satu modul asm bisa memuat
  beberapa fungsi (18 BEDA palsu sampai dibetulkan lewat PUBDEF).
- `aligncmp` versi pertama mencoba geseran dari −24, jadi condong ke geseran
  besar pada kode berulang (198 vs 376 byte terjajar).

### Yang TIDAK selesai / menunggu keputusan user

1. **Bug `gendata.py`**: penyaring `START <= a` dengan `START = 4` membuang
   alamat DGROUP 0..3, memblokir 13 byte di `main`. Memperbaikinya menyentuh
   DGROUP yang sekarang 100% — **butuh izin**.
2. **Dua global bernama menyesatkan**: `mode_` (0x846) dan `seed` (0x72a)
   sebenarnya PEGANGAN BERKAS. Ganti nama atau biarkan?
3. **Alokasi register belum bisa dikendalikan** — near-miss `f498c` (3 byte,
   SI vs BX) dan `place` (2 byte, SI vs DI). Bentuk ekspresi tidak berpengaruh.
4. **Selisih 2 byte temp di `main`** — semua lokal 2 byte lebih rendah;
   pemicunya belum ketemu (tidak ada rujukan slot temp sama sekali di biner).

---

## Sesi 2026-07-31 (lanjutan) — `f2823` tuntas lewat probe

| | sebelum | sesudah |
|---|---|---|
| fungsi COCOK byte-per-byte | 72/79 | **73/80** |
| byte terverifikasi | 14.412 | **14.809** |
| TOTAL | 65,2% | **66,3%** |
| DATA (DGROUP) | 100% | 100% (tak tersentuh) |

`f2823` (0x2823, 397 B) — interpolator parabola gerak bola — dari TERJAJAR
118/397 langsung ke **397/397**, sekali kompilasi. Yang membuatnya cepat:
semantiknya TIDAK perlu diturunkan dari disassembly karena jalur port sudah
membedah dan memvalidasinya vs emulator (`interp_2823` di `port/cc/animvm.py`).
Yang tersisa cuma soal BENTUK, dan itu dijawab satu probe.

### `probes/probe19.c` — dua jawaban sekaligus

Pertanyaannya: dari mana slot bingkai `[bp+1Ch]` yang berisi konstanta 100
sebagai `long`? Tiga varian dengan ekspresi identik:

- `x / 100` dan `x / 100L` → **pancarannya IDENTIK**, `xor cx,cx / mov dx,64h`
  di titik pembagian, tanpa slot bingkai. Akhiran `L` tidak mengubah apa pun.
- `long hun; hun = 100; x / hun` → slot bingkai ADA, diisi sekali di AWAL fungsi
  (terjalin dengan pernyataan sebelumnya), dibaca dua kali. Persis aslinya.

Kesimpulan: **slot bingkai berisi konstanta `long` = variabel yang memang
ditulis programmernya.** Sudah masuk `README.md`.

Probe yang sama menjawab pertanyaan kedua yang tidak sengaja terjawab: draf
lama menulis `(long)(tx - fx) + ...`. Cor itu **mubazir secara semantik** —
hasilnya sama karena operan lain sudah `long` — tapi TETAP mengubah kode: ia
memperluas tanda segera dan menyimpan dua kata ke temp, sedangkan aslinya
menyimpan hasil `int`-nya saja lalu memperluas tanda di titik penjumlahan.

### Pelajaran metodologis

Sesi sebelumnya sudah membuktikan probe mengalahkan tebak-kompilasi untuk soal
register. Ini pembuktian kedua di ranah berbeda (aritmetika `long`), dan kali
ini ongkosnya satu kompilasi lawan puluhan. **Probe dulu, bukan iterasi fungsi
penuh** sekarang berlaku umum, bukan cuma untuk register.

Catatan arah: kedua produk saling membayar. Port Python menyumbang semantik
tervalidasi ke rekonstruksi C. Untuk `animvm` (0x18db, 3.040 B, stub terakhir)
jalur yang sama tersedia — `port/cc/animvm.py` sudah memparsi 17 opcode-nya.

---

## Sesi 2026-07-31 (lanjutan) — `f278e` + `f2714` tuntas: soal TIPE, bukan urutan

| | sebelum | sesudah |
|---|---|---|
| fungsi COCOK byte-per-byte | 73/80 | **75/80** |
| byte terverifikasi | 14.809 | **15.080** |
| TOTAL | 66,3% | **67,0%** |
| DATA (DGROUP) | 100% | 100% (tak tersentuh, diuji ulang) |

Dua fungsi, satu perubahan, keduanya langsung cocok penuh:
`f278e` 141/149 → **149/149**, `f2714` 76/122 → **122/122**.

### Aturan: `extern char *p` ≠ `extern int p` + cor `*(char *)p`

| sumber | pancaran |
|---|---|
| `extern char *p;` … `*p` | `mov si,[p]` (4 byte) |
| `extern int p;` … `*(char *)p` | `mov ax,[p]` + `mov si,ax` (5 byte) |

Bedanya bukan cuma satu byte per pemakaian. Bentuk cor membuat kompiler
**menahan nilainya di register**; tipe penunjuk asli **memuat ulang dari
memori tiap rujukan**. Di `f2714` yang membaca kursor enam kali, itu mengubah
seluruh bentuk kode.

### ⚠ Koreksi diagnosis lama

Catatan `f2714` sebelumnya menyimpulkan divergensinya soal URUTAN PERNYATAAN,
dan mencatat tiga bentuk yang "sudah dicoba & gagal" (termasuk penugasan
bersarang `balltop = 0xc7 - (ballx = ...)`). Pengamatannya benar — aslinya
memang memuat ulang `mov si,[3AEh]` tiap pembacaan — tapi **sebabnya salah
ditebak**. Begitu tipenya dibetulkan, semua bentuk urutan yang lama jadi tidak
relevan. Catatan yang keliru itu sudah dicabut dari berkasnya, bukan dibiarkan.

Pelajarannya: divergensi yang sudah TERLOKALISASI belum berarti sudah
TERDIAGNOSIS. "Di alamat mana" murah didapat; "kenapa" tetap harus diuji.

### DGROUP: risikonya ternyata tidak ada

Kekhawatiran lama bahwa mengubah tipe extern akan menggeser DGROUP tidak
terbukti: `gendata.py` memancarkan tiap simbol BUKAN-larik sebagai `int` apa
pun tipe yang tertulis (cabang `if not arr:`). Diuji dengan menjalankan ulang
gendata sesudah perubahan — `gdata.c` tidak berubah satu byte pun.

---

## Pengintaian `animvm` @0x18db (3.040 B) — stub TERAKHIR

Belum ditulis sebaris pun; ini peta untuk memulainya. Semua terukur.

### ⚠ Ada TABEL DATA 72 byte DI TENGAH fungsi (0x23d4..0x241b)

Disassembler berhenti di 0x23d4 dan diam saja soal itu — kalau dipercaya
mentah-mentah, 160 byte terakhir fungsi ini tak akan pernah terlihat. Kode
berlanjut lagi di **0x241c** sampai `ret` di 0x24ba.

Tabelnya 18 pasang `(nilai_case, alamat_badan)` — bentuk switch PEMINDAIAN
(README aturan 13). Pemindainya mulai `si = 0x44` lalu `sub si,4` menurun,
jadi tabel dibaca MUNDUR. Urutan pindai itu **persis sama dengan urutan ALAMAT
badan case**, konfirmasi lagi aturan 13:

| urutan tulis | case | badan |
|---|---|---|
| 1 | 0x10 | 0x1d09 |
| 2 | 0x11 | 0x1e85 |
| 3 | 0x00 | 0x1f11 |
| 4 | 0x0a | 0x1f32 |
| 5 | 0x08 | 0x1f3b |
| 6 | 0x01 | 0x1f49 |
| 7 | 0x07 | 0x1f70 |
| 8 | 0x09 | 0x1f79 |
| 9 | 0x02 | 0x1f8d |
| 10 | 0x03 | 0x1fac |
| 11 | 0x0c | 0x21e1 |
| 12 | 0x04 | 0x2280 |
| 13 | 0x05 | 0x2305 |
| 14 | 0x06 | 0x2315 |
| 15 | 0x0d | 0x2321 |
| 16 | 0x0e | 0x2334 |
| 17 | 0x0f | 0x233c |
| 18 | 0xff | 0x23d1 |

`default` = 0x1cd2 (jatuh ke sana kalau pemindaian habis).

### Bingkai 0x6a

`push bp; sub sp,6Ah; mov bp,sp` → **sembilan argumen** di bp+6E,70,72,74,76,
78,7A,7C,7E. Temp di 0x00..0x0d; lokal 0x0e..0x69 (92 byte).

Slot yang paling sering dirujuk: **+0e (17x)** indeks langkah skrip — dipakai
sebagai `arg0[i]` lewat `shl ax,1` + `add si,[bp+6e]`, jadi arg0 larik `int`.
**+54 (17x)**. **+10 dan +12 (10x)** dua pencacah yang di-`inc` bergantian
menurut `arg0[i] == -1`. **+2c** penyangga BUNYI: `lea ax,[bp+2ch]` lalu
disimpan ke `sndptr` (0x720) — jadi lokal larik, bukan skalar. **+60/+61**
diakses per-BYTE (larik `char`), sisanya kata.

### Yang sudah dipanggil (semua sudah COCOK, jadi namanya tinggal dipakai)

`f2714` (0x2714), `f278e` (0x278e), `f2823` (0x2823) — ketiganya baru selesai
hari ini dan memang dipanggil dari sini, masing-masing 2x. Juga `bounce`
(0x2504), `waitn` (0x2b11), `blit` (0x672f), `fillrect` (0x6869), `text`
(0x6453), `blitmsk` (0x6524), `shftr` (0x6600), `keyio` (0x66fd).

⚠ 0x2475 memanggil **0x24bb** — fungsi PERSIS SESUDAH `animvm`. Itu bukan
rekursi; batas fungsinya memang di situ.

### Modal dari jalur port

`port/cc/animvm.py` sudah memparsi 17 opcode-nya dan interpolatornya sudah
tervalidasi vs emulator. Sama seperti `f2823` hari ini, semantiknya TIDAK
perlu diturunkan ulang dari disassembly — cek ke sana dulu tiap menulis case.

### Ukuran pekerjaan

1.039 instruksi di badan utama + 160 byte ekor. Ini pekerjaan BERTAHAP:
kerangka (prolog, gelung baca skrip, dispatcher, ekor) dulu, baru case satu
per satu menurut urutan alamat di tabel atas.

---

## `animvm` tahap 1: prolog ditulis — stub TERAKHIR habis

| | sebelum | sesudah |
|---|---|---|
| `animvm` TERJAJAR | 0 / 3.040 (stub) | **412 / 3.040 (13,6%)** |
| stub tersisa | 1 | **0** |
| fungsi COCOK | 75/80 | 75/81 (animvm belum cocok, kini ikut dihitung) |
| DATA (DGROUP) | 100% | 100% |

480 byte tertulis, 412 di antaranya sejajar (86% dari yang ditulis). `stubs.c`
sekarang KOSONG dari fungsi — tiap fungsi game punya sumber nyata, walau lima
di antaranya belum byte-exact. `animvm` juga sudah masuk `manifest.txt` supaya
verifyall melaporkannya apa adanya, bukan menyembunyikannya.

### Bingkai: pengganjal SEMENTARA yang harus dibuang nanti

Kompilasi pertama memberi bingkai 0x60, bukan 0x6a — kurang 10 byte. Sebabnya
jelas: 92 byte lokal sudah benar, tapi draf ini baru menuntut 4 byte TEMP
karena badan case belum ditulis (aslinya 14). Tanpa ganjal, SEMUA offset lokal
bergeser 10 byte dan prolog yang sudah benar pun terhitung salah — penjajaran
cuma 326. Dengan `char tpad[10]` di depan: bingkai 0x6a tepat, penjajaran 408.

⚠ `tpad` WAJIB dibuang begitu ekspresi asli menuntut temp-nya sendiri, kalau
tidak bingkainya akan kelebihan.

### Dua perbaikan kecil yang terukur (408 → 412)

- Urutan `u42 = 0; u56 = 0;` — aslinya menyimpan +56 DULU baru +42, dan
  ternyata urutan sumber yang memberi itu justru yang terbalik dari dugaan.
- Alamat data ditulis sebagai INDEKS larik bernama, bukan literal: 0x586 dan
  0x5e6 ada DI DALAM `hdrspr[]` (@0x526) — tiga sprite 96 byte, jadi
  `hdrspr`, `&hdrspr[96]`, `&hdrspr[192]`. Literal `0x586` tidak memancarkan
  slot relokasi sama sekali, jadi selain salah byte ia juga lolos dari
  symcheck. Ini persis aturan "alamat di dalam larik bernama ditulis sebagai
  indeks larik itu".

### Yang MASIH literal (utang untuk iterasi berikut)

`sndptr = 0x978` masih angka mentah. 0x978 ada di dalam salah satu larik string
DGROUP tapi pemetaannya belum bisa dipastikan — penelusur offset ad-hoc yang
saya tulis meleset (melaporkan `hdrspr` di 0x048d padahal komentar sumber
bilang 0x526), jadi angkanya TIDAK dipakai. Pakai alat resmi `dgroup.py`, jangan
penelusur dadakan.

### Sisa pekerjaan

480 dari 3.040 byte. Yang belum ditulis: gelung utama (0x1ab8..0x1cd2),
dispatcher (0x1cd2..0x1d06 + 0x241c..0x2430), 18 badan case, dan ekor
(0x2433..0x24ba). Satu hal yang sudah terlihat dan perlu disiapkan: skor
di 0x730 ditambah dengan `add [0x730],imm / adc [0x732],0` — aritmetika `long`
atas pasangan word yang di gdata.c bernama `sclo`/`schi`. Trik yang sama
seperti `char *scrptr` berlaku: deklarasikan `extern long sclo;` (nama SAMA,
tipe beda) — tautannya tetap sah karena LINK memadankan nama, bukan tipe.

---

## Bug `sprtab`: satu NAMA untuk dua ALAMAT (2026-07-31)

Ditemukan tidak sengaja sewaktu mencari nama simbol untuk tabel yang dibaca
`animvm` di 0x1b0. Bukan kemajuan byte — tapi lebih berharga daripada byte.

`sprtab` dideklarasikan di DUA berkas dengan alamat BERBEDA: `@0x0a`
(drawpair.c) dan `@0x1ae` (drawslot.c). LINK memadankan NAMA, bukan alamat, dan
`gdata.c` cuma mendefinisikan satu `sprtab` — gendata memakai `setdefault`
sehingga berkas pertama secara abjad menang (0x0a). Akibatnya rujukan drawslot
tertaut ke 0x0a dan **meleset 420 byte**.

### Buktinya, bukan dugaan

Slot relokasi di `out/CONTRAP.EXE` hasil link dibaca langsung:

| | sebelum | sesudah | biner asli |
|---|---|---|---|
| drawslot → tabel 0x1ae | `0x0016` | **`0x01ba`** | `0x01ae` |
| drawpair → tabel 0x0a | `0x0016` | `0x0016` | `0x000a` |

Build kita menempatkan DGROUP 12 byte lebih belakang daripada biner asli
(pustaka menyumbang data sebelum `gdata.c`), jadi `+12` yang seragam di kedua
baris itulah yang BENAR. Sebelum perbaikan, drawslot meleset dari pola itu.

### Kenapa lolos begitu lama — TIGA lapis gagal sekaligus

1. `objcode.py` memperlakukan slot relokasi sebagai wildcard → `COCOK`.
2. `verifyall.py` memakai objcode → `COCOK`.
3. `symcheck.py`, yang JUSTRU dibuat untuk menutup lubang ini, menganggapnya
   "akses ber-INDEKS": selisih 420 masih di bawah ambang lamanya 0x400.

Lapis ketiga itu yang paling perlu dicatat. Alat verifikasi yang punya
pengecualian akan menyembunyikan persis kelas bug yang pengecualian itu
menyerupai. `put()` (0x6524 vs 0x65e0) dulu lolos lewat lapis 1-2; yang ini
lolos lewat lapis 3.

### Perbaikan

- Tabel di 0x1ae diberi nama sendiri: **`parttab`**. `gdata.c` otomatis
  memecah blok 594 byte jadi `sprtab[420]` + `parttab[174]` — DGROUP tetap
  9.556/9.556 byte, 0 beda. `drawslot` tetap COCOK.
- `symcheck.py`: ambang indeks diperketat `0x400` → `INDEX_MAX = 0x100`, dan
  selisih di antaranya dilaporkan sebagai baris **CURIGA** alih-alih dihitung
  diam-diam. Aman: selisih indeks SAH terbesar di seluruh proyek cuma +94
  (`mainmenu`/`mtabmn`), jadi tidak ada satu pun positif palsu. Sekarang
  CURIGA = 0.

### Aturan yang bertambah

"SATU alamat SATU nama" punya ARAH KEBALIKAN yang sama berbahayanya: **satu
NAMA tidak boleh dipakai untuk dua alamat.** Tiap kali menambah
`extern ... /* @0xNNN */`, periksa namanya belum dipakai untuk alamat LAIN —
bukan cuma bahwa alamatnya belum punya nama.

---

## `animvm` tahap 2: gelung utama + blok skor + ekor (412 → 758)

| | sebelum | sesudah |
|---|---|---|
| `animvm` TERJAJAR | 412 / 3.040 (13,6%) | **758 / 3.040 (24,9%)** |
| byte tertulis | 480 | 1.208 |
| DATA (DGROUP) | 100% | 100% |
| symcheck CURIGA | 0 | 0 |

Yang ditulis: gelung langkah utama (dua cabang MEKANISME/ZANY yang bertemu di
blok skor), gelung penafsir skrip, dan ekor. Yang belum: 17 badan case.

### Dua bentuk yang perlu dicatat

**`showsc(sclo, 1)` — satu argumen `long` mendarat sebagai DUA parameter word.**
Biner mem-`push [732h]` lalu `push [730h]`, dan `showsc.c` menerimanya sebagai
`showsc(lo, hi, flash)`. Jadi pemanggilnya memang menulis satu `long`; konvensi
pemanggilan yang memecahnya. `extern long sclo;` (nama SAMA dengan `int sclo`
di gdata.c, tipe beda) sekaligus memberi `add [730h],imm / adc [732h],0` untuk
penambahan skornya. Trik yang sama seperti `char *scrptr`.

**`switch (*scrptr++)` tanpa variabel perantara.** Opcode-nya tidak pernah
disimpan ke slot bingkai mana pun — dispatcher menerima nilai langsung di AX.

### Bingkai: ganjal dikecilkan 10 → 8

Ekspresi baru menuntut 6 byte temp (sebelumnya 4), jadi bingkai sempat jadi
0x6c. Mengecilkan `tpad` mengembalikannya ke 0x6a — dan itu **menaikkan
penjajaran 547 → 758**, bukan cuma memperbaiki angka bingkai. Offset lokal yang
meleset merusak SEMUA rujukan sesudahnya.

### ⚠ Jebakan: nama BERKAS ≠ nama SIMBOL, lagi

`keyio(0x16, 0)` gagal ditautkan: modul `keyio.asm` mem-PUBDEF `F66FD`, bukan
`keyio`. LINK bersih setelah dipanggil `f66fd()`. Ini pengulangan jebakan yang
sudah pernah menghasilkan 18 BEDA palsu di symcheck — komentar `nama()=alamat`
di kepala berkas adalah CATATAN kita, bukan nama simbol yang sebenarnya.
Untuk modul assembly, periksa PUBDEF-nya:
`python -c "import sys;sys.path.insert(0,'src_c/verify');from symcheck import read_pubdefs;print(read_pubdefs('src_c/out/keyio.OBJ'))"`

### Geseran yang tersisa (untuk iterasi berikut)

`0x1b28:+10` (terbesar), `0x1b51:-1`, `0x1b63:-3`, `0x1bd8:+4`, `0x1c07:-1`,
`0x1c3b:+2`, `0x1cfa:+6`.

Yang di 0x1b28 sudah terlokalisasi: `fail[c1]++` kita memancarkan
`mov si,[bp] / inc word ptr [si]` (alamat penuh sudah di penunjuk), aslinya
`mov si,[bp] / inc word ptr [si+7BEh]` (basis larik jadi displacement, temp
[bp] cuma berisi `c1*2` yang DIPAKAI ULANG dari ekspresi sebelumnya).
Terkait juga pilihan register di 0x1b11: aslinya `cmp ax,[di]` (dua penunjuk
hidup bersamaan), punya kita `cmp ax,[bx]`.
⚠ Ini BARU TERLOKALISASI, BELUM TERDIAGNOSIS — jangan tebak sebabnya.

---

## `animvm` tahap 3: 8 badan case (758 → 1.418, 24,9% → 46,6%)

| | sebelum | sesudah |
|---|---|---|
| `animvm` TERJAJAR | 758 / 3.040 | **1.418 / 3.040 (46,6%)** |
| byte tertulis | 1.208 | 1.950 |
| bingkai | 0x6a | 0x6a (tetap) |
| DATA / symcheck CURIGA | 100% / 0 | 100% / 0 |

Ditulis: `0x10` (akhir goal: bonus + skor + hint, 380 B), `0x11` (teks
berparameter), lalu `0x00`, `0x0a`, `0x08`, `0x01`, `0x07`, `0x09`, `0x02`.
Tersisa 9: `0x03`(1fac), `0x0c`(21e1), `0x04`(2280), `0x05`, `0x06`, `0x0d`,
`0x0e`, `0x0f` — dan `0xff` yang sudah ada.

### ⚠ KOREKSI tata letak bingkai: `snd[]` cuma 3 kata, bukan 11

Draf tahap 1 menebak penyangga bunyi di 0x2c berukuran 11 kata karena slot
0x2c..0x41 semuanya dirujuk per-kata. Salah: prolog cuma mengisi TIGA kata
(0x2c/0x2e/0x30), dan 0x32..0x41 ternyata **delapan variabel terpisah** yang
baru kelihatan begitu badan `case 0x11` dibaca — ia memakai 0x32, 0x34, 0x36,
0x38, 0x3a, 0x3c, 0x3e sebagai parameter teks, dan `case 0x10` memakai 0x40
sebagai pencacah gelung.

Totalnya tetap 92 byte, jadi bingkai tidak berubah — tapi kalau dibiarkan,
`case 0x10` akan menulis ke `snd[10]` dan tidak akan pernah cocok. Pelajaran:
**slot yang berdekatan dan sama lebar BUKAN bukti satu larik.** Bukti larik
adalah `lea` atau indeks variabel; di sini `lea [bp+2Ch]` cuma menjangkau tiga
kata pertama.

### JATUH TEMBUS antar-case

`0x0a` jatuh tembus ke `0x08`, dan `0x07` ke `0x09` — di biner badan yang
pertama berakhir tepat di awal badan berikutnya TANPA lompatan. Keduanya
"reset posisi bola lalu lakukan sekali", jadi memang disengaja penulisnya.
Ini juga menegaskan lagi aturan urutan case: 0x0a ditulis SEBELUM 0x08 karena
alamat badannya lebih kecil, bukan karena nilainya.

---

## `animvm` tahap 4: `case 0x03` + misteri 0x1a8 terpecahkan (1.418 → 2.002)

| | sebelum | sesudah |
|---|---|---|
| `animvm` TERJAJAR | 1.418 / 3.040 (46,6%) | **2.002 / 3.040 (65,9%)** |
| byte tertulis | 1.950 | 2.508 |
| DATA / symcheck CURIGA | 100% / 0 | 100% / 0 |

### ⭐ Konstanta 0x1a8 dan 0x4 = PANDANGAN KEDUA atas tabel yang sama

Utang yang tercatat dua iterasi lalu ("`u4a = 0x1a8` / `= 4`, keduanya tepat
6 byte sebelum basis tabel, bentuk C-nya belum terpecahkan") **selesai**, dan
jawabannya justru datang dari badan `case 0x03` — bukan dari menebak.

Di sana `0x1a8 + 12*k` dipakai lalu field pada **offset +8**-nya ditulis.
`0x1a8 + 12k + 8 = 0x1b0 + 12k`, dan `0x1b0` = `parttab + 2` = field `scr`.
Jadi keduanya menunjuk memori yang SAMA lewat dua basis berbeda:

| pandangan | basis | field skrip |
|---|---|---|
| `parttab` | 0x1ae | offset +2 |
| `anmech`  | 0x1a8 | offset +8 |
| `sprtab`  | 0x0a  | offset +2 |
| `anzany`  | 0x004 | offset +8 |

`f278e` menerima basis versi "an" dan membaca `spr` di offset +6 — yang sama
dengan `parttab[k].w`. Semuanya konsisten. Dua nama baru ditambahkan ke
gendata; DGROUP tetap 9.556/9.556, 0 beda.

⚠ Ini juga menghapus satu risiko diam-diam: literal `0x1a8` **tidak
memancarkan slot relokasi**, jadi ia akan cocok byte-per-byte dengan biner
asli tapi menunjuk alamat yang salah di build kita (yang DGROUP-nya bergeser
+12). Kelas bug yang persis sama dengan `sprtab` — dan kali ini tertangkap
sebelum sempat masuk.

### ⚠ Pola alamat gendata menuntut 2-4 digit hex

`/* @0x4 */` **TIDAK** terpanen — polanya `@0x([0-9a-fA-F]{2,4})`. Harus
ditulis `@0x004`. Gagalnya SENYAP: gdata.c cuma kehilangan satu simbol dan
baru ketahuan waktu jumlah simbol tidak bertambah seperti yang diharapkan.

### Switch BERSARANG dengan tabelnya sendiri

`case 0x03` memuat switch kedua, lengkap dengan tabel pindai 16 byte di
0x21ba. Keempat nilainya (0x00, 0x0a, 0x08, 0x0b) memakai badan yang SAMA di
0x2150, jadi labelnya bertumpuk; urutan label = urutan pindai tabel.

### Bingkai lagi

Ekspresi baru menuntut 8 byte temp, jadi `tpad` dikecilkan 8 → 6. Sebelum
dikecilkan penjajaran cuma 1.322; sesudahnya 2.002. Ini kali KETIGA pola yang
sama: **periksa bingkai lebih dulu, sebelum menyimpulkan apa pun dari angka
penjajaran.**

---

## `animvm` tahap 5: KE-18 CASE LENGKAP (2.002 → 2.561, 84,2%)

| | sebelum | sesudah |
|---|---|---|
| `animvm` TERJAJAR | 2.002 / 3.040 (65,9%) | **2.561 / 3.040 (84,2%)** |
| panjang | 2.508 | **3.027 / 3.040 (−13)** |
| badan case tertulis | 11 dari 18 | **18 dari 18** |
| DATA / symcheck CURIGA | 100% / 0 | 100% / 0 |

Ditulis: `0x0c`, `0x04`, `0x05`, `0x06`, `0x0d`, `0x0e`, `0x0f`. Seluruh
struktur fungsi sekarang ADA — sisanya tinggal 12 geseran kecil.

### `case 0x0f` — dua switch bersarang dan `continue` yang WAJIB

Ini bagian paling berliku. `case 0x0f` memuat DUA switch bersarang berurutan:
satu atas `keyhit()` (tabel sendiri di 0x235a) dan satu atas `u5a`.

Yang penting: badan untuk tombol ESC/ENTER/SPASI melompat **langsung ke puncak
gelung skrip**, MELEWATI switch kedua. Dalam C itu `continue`, bukan `break` —
`break` cuma keluar dari switch dalam lalu jatuh ke switch kedua, dan
perilakunya jadi lain. Salah satu dari sedikit tempat di mana pilihan kata
kunci C mengubah struktur, bukan cuma byte.

`case 0` di switch kedua **jatuh tembus** ke `case -1` (kalau byte skrip
berikutnya 0xFF, setel `u5c = 1` lalu teruskan). Ini kemunculan KEDUA pola
jatuh-tembus di fungsi ini.

### `case 0x04` — aliran bunyi diakhiri penanda GANDA

Mode 2/3 membaca sampai `0xFF 0xFF` BERURUTAN, bukan 0xFF tunggal — persis
seperti yang sudah dicatat `parse_op04` di jalur port. Bentuk C-nya:
`do { scrptr++; } while (*scrptr != 0xff || *++scrptr != 0xff);`
Pra-increment di operan kedua itu penting: biner menaikkan kursor DULU baru
membaca.

### ⚠ Nama BERKAS ≠ nama SIMBOL — menggigit KEDUA kalinya

`blitmsk(...)` gagal ditautkan: modul `blitmsk.asm` mem-PUBDEF **`PUTMSK`**
(di offset 0), bukan `blitmsk`. Sama persis dengan `keyio`/`F66FD` dua iterasi
lalu. Pemeriksaan PUBDEF sekarang WAJIB sebelum memanggil fungsi dari modul
assembly:

    python -c "import sys;sys.path.insert(0,'src_c/verify');from symcheck import read_pubdefs;print(read_pubdefs('src_c/out/blitmsk.OBJ'))"
    -> [('DRAW', 88), ('PUT', 188), ('PUTMSK', 0), ('SHFTR', 220)]

Satu modul, EMPAT simbol publik, dan tak satu pun bernama sama dengan berkasnya
kecuali kebetulan.

### Geseran tersisa (12)

`0x1b28:+10`, `0x1b50:-1`, `0x1bd8:+3`, `0x1c07:-2`, `0x1ce8:-5`, `0x1fab:-7`,
`0x2012:-1`, `0x2103:+5`, `0x21b9:+8`, `0x2236:+10`, `0x22da:+11`, `0x23a0:+13`.
Semuanya BARU TERLOKALISASI, belum terdiagnosis.

---

## `animvm` tahap 6: satu aturan baru, tiga hipotesis DITUTUP

Iterasi ini **tidak menaikkan angka agregat** (2.561 → 2.560, selisih derau).
Yang didapat: satu aturan baru yang terbukti, satu blok jadi byte-identik, dan
tiga hipotesis yang ditutup lewat probe. Dicatat apa adanya.

### ⭐ Penugasan DI DALAM syarat menahan nilai di register

`case 0x02` sekarang **byte-identik**. Sebabnya satu perubahan bentuk:

| sumber | pancaran argumen |
|---|---|
| `if ((u2a = *scrptr++) >= 0) delay(u2a);` | `push ax` (1 byte) |
| `u2a = *scrptr++; if (u2a < 0) break; delay(u2a);` | `push [bp+2Ah]` (3 byte) |

Bentuk dua-pernyataan memaksa kompiler MEMUAT ULANG dari bingkai. Sudah masuk
`README.md`.

⚠ Angka agregat tidak naik karena penjajaran serakah menggeser keuntungan itu
ke tempat lain. **Angka total bisa menyembunyikan perbaikan nyata** — daftar
GESERAN lebih informatif: entri `0x1fab:-7` hilang sama sekali.

### ⚠ Hasil NEGATIF: `imul word ptr [mem]` bukan dari perkalian biasa

Geseran pertama (0x1b28) berpangkal di 0x1afd: aslinya
`mov ax,3 / imul word ptr [bp+10h]` (5 byte), punya kita
`mov ax,[bp+10h] / mov bx,3 / imul bx` (8 byte). Tiga probe, tiga GAGAL:

| hipotesis | probe | hasil |
|---|---|---|
| urutan operan `3 * c1` vs `c1 * 3` | probe21a/b | pancarannya IDENTIK |
| konteks indeks larik / dua penunjuk hidup | probe20a-d | selalu `imul bx` |
| skala indeks larik STRUCT `t[a].id` | probe22a-c | `mov bx,6 / imul bx`, tanpa `shl` |

Kesimpulan: bentuk `imul` beroperan-MEMORI **tidak bisa dihasilkan dari
perkalian yang ditulis programmernya** di kompiler ini. Sumbernya masih belum
diketahui — dan itu dicatat sebagai belum diketahui, bukan ditebak. Ketiga
percobaan itu JANGAN diulang.

Ini penerapan aturan "TERLOKALISASI belum berarti TERDIAGNOSIS" secara sadar:
divergensinya sudah tepat di satu instruksi sejak awal iterasi, tapi tiga
tebakan yang masuk akal semuanya salah.

---

## `animvm` tahap 7: dua aturan bentuk, 2.560 → 2.642 (86,9%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.560 / 3.040 (84,2%) | **2.642 / 3.040 (86,9%)** |
| panjang | 3.025 / 3.040 (−15) | **3.034 / 3.040 (−6)** |
| geseran | 11 | **8** |

Tiga geseran lunas (`0x1ce8`, `0x2012`, `0x2103`) lewat dua aturan bentuk baru.

### ⭐ SATU ekspresi `||` menahan penunjuk di register

| sumber | uji kedua |
|---|---|
| `if (*p == 0xff || p == 0) break;` | `test si,si` (2 byte) |
| `if (*p == 0xff) break; if (p == 0) break;` | `cmp [3AEh],0` (5 byte) |

Alur kendalinya IDENTIK. Yang berbeda cuma apakah kompiler masih menganggap
penunjuknya hidup di register — dan itu bergantung pada apakah kedua uji ada
di SATU ekspresi. Sepola dengan aturan penugasan-di-dalam-syarat (tahap 6).

### ⭐ TERNARY vs `if/else` — dan pilihannya per-TEMPAT

| sumber | pancaran |
|---|---|
| `v = c ? a : b;` | hitung ke AX, SATU simpanan, AX dipakai ulang |
| `if (c) v = a; else v = b;` | simpan di KEDUA cabang, lalu MUAT ULANG `v` |

Selisih 4 byte. Yang penting dicatat: **pilihannya per-tempat, bukan
per-berkas.** Di `case 0x03` yang sama, pemilihan indeks memakai `if/else`
sedangkan pemulihan tanda ambang 0xC8 tepat di bawahnya memakai TERNARY —
dan keduanya sudah terverifikasi cocok. Menyeragamkan salah satu akan merusak
yang lain.

### Geseran tersisa (8)

`0x1b28:+10`, `0x1b50:-1`, `0x1bd8:+3`, `0x1c07:-2`, `0x21bb:+1`, `0x2236:+3`,
`0x22da:+4`, `0x23a0:+6`.

Empat yang pertama berpangkal pada dua tempat `imul word ptr [mem]` (cabang
MEKANISME 0x1afd dan cabang ZANY 0x1bb7) yang sudah dinyatakan BUNTU di tahap 6
— jangan diulang tanpa pemahaman baru.

---

## `animvm` tahap 8: "jalan buntu" ternyata gejala — 2.642 → 2.700 (88,8%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.642 / 3.040 (86,9%) | **2.700 / 3.040 (88,8%)** |
| POSISI | 982 | **2.378** |
| geseran | 8 | **4** |
| panjang | −6 | −8 |

### ⚠⚠ Koreksi penting: divergensi 0x1afd BUKAN soal perkalian

Tahap 6 mencap 0x1afd "BUNTU" setelah tiga probe gagal, dan menulis bahwa
`imul word ptr [mem]` "tidak bisa dihasilkan dari perkalian yang ditulis
programmernya". Probe-probenya benar — bentuk perkalian memang tidak
menentukan. **Kesimpulan yang ditarik darinya yang salah.**

Sebabnya ada **30 instruksi lebih jauh**: `slot = c2; curz = c1;` ditaruh
SESUDAH `printf(...)`, padahal aslinya SEBELUM. Begitu dipindah, kompiler
memuat `c1`/`c2` ke register di AWAL blok; tekanan registernya berubah; dan
`mov ax,3 / imul word ptr [bp+10h]` **plus** pemilihan `DI` untuk penunjuk
kedua muncul sendiri — tanpa satu pun perubahan pada ekspresi perkaliannya.

EMPAT geseran yang sudah dicap buntu (`0x1b28`, `0x1b50`, `0x1bd8`, `0x1c07`)
lunas sekaligus.

### Aturan yang bertambah

**Kompiler ini mengalokasikan register per-BLOK DASAR, bukan per-pernyataan.**
Instruksi pertama yang berbeda menunjukkan DI MANA akibatnya terlihat, bukan
di mana sebabnya. Kalau probe atas bentuk lokal semuanya gagal, berhenti
menguji bentuk itu — periksa URUTAN PERNYATAAN di seluruh blok.

Ini memperdalam aturan lama "TERLOKALISASI belum berarti TERDIAGNOSIS": kali
ini lokalisasinya tepat sampai ke satu instruksi, dan tetap menyesatkan.

### Geseran tersisa (4)

`0x21bb:+3`, `0x2236:+5`, `0x22da:+6`, `0x23a0:+8`. Yang di 0x21bb sudah
terlokalisasi: aslinya punya DUA `jmp 1cd2` berturut di 0x21b4/0x21b7 (yang
kedua kode MATI), punya kita cuma satu.

---

## `animvm` tahap 9: nilai yang DIBUANG — 2.700 → 2.748 (90,4%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.700 / 3.040 (88,8%) | **2.748 / 3.040 (90,4%)** |
| geseran | 4 | 4 (satu bergeser tempat) |
| panjang | −8 | −10 |

### ⭐ Pemulihan tanda yang hasilnya DIBUANG

Di `case 0x0c` biner menghitung ternary pemulihan tanda 0xC8 lalu **membuang
hasilnya** — AX ditimpa `mov ax,si` tanpa pernah disimpan balik ke `[bp+44h]`,
dan `f2823` menerima nilai MENTAH-nya. Bentuk C-nya pernyataan-ekspresi tanpa
penugasan:

```c
u44 = *scrptr++;
(u44 >= 0xc8) ? u44 - 0x100 : u44;      /* hasil DIBUANG */
```

Kelihatannya **bug di gim aslinya** — penulisnya lupa menugaskan balik. Kita
merekonstruksi apa adanya.

⚠ **PER-CASE.** `case 0x03` beberapa baris di atas melakukan hal yang sama
persis TAPI menyimpan hasilnya. Diuji: membuangnya di sana menurunkan
penjajaran 2.748 → 2.722 dan memunculkan geseran baru di 0x1ff1. Perubahan itu
langsung dibatalkan dan alasannya ditulis di berkasnya supaya tidak dicoba lagi.

Ini varian KETIGA dari pola yang sama (setelah ternary-vs-if/else dan
urutan-pernyataan): bentuk yang benar ditentukan per-TEMPAT dan harus DIUKUR.

### Yang dicoba dan GAGAL iterasi ini

Memecah `u4c = *++u54;` jadi `u54++; u4c = *u54++;` di `case 0x0c`:
panjang melonjak +10 (3.042 vs 3.040) tanpa menaikkan penjajaran. Dibatalkan.
Bentuk pra-increment satu-ekspresi tetap yang benar di sana.

### Geseran tersisa (4)

`0x21bb:+3`, `0x2219:+7`, `0x22da:+8`, `0x23a0:+10`.
Yang di 0x21bb masih sama: aslinya punya DUA `jmp 1cd2` berturut di
0x21b4/0x21b7 (yang kedua KODE MATI), punya kita cuma satu. Belum terpecahkan.

---

## `animvm` tahap 10: percobaan yang gagal ternyata benar — 2.748 → 2.753

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.748 / 3.040 (90,4%) | **2.753 / 3.040 (90,6%)** |
| geseran | 4 | **3** |
| panjang | −10 | −6 |

### ⚠ Percobaan yang GAGAL bisa BENAR sesudah perbaikan lain

Memecah `u4c = *++u54;` jadi `u54++; u4c = *u54++;` dicoba di tahap 9 dan
**gagal** (panjang +10, penjajaran tetap), jadi dibatalkan dan dicatat sebagai
jangan-diulang. Percobaan yang SAMA PERSIS dicoba lagi iterasi ini — setelah
perbaikan tahap 9 yang tidak berhubungan di blok yang sama — dan **berhasil**:
geseran `0x2219` lunas.

Alasannya sudah dipahami: alokasi register se-BLOK. Selama masih ada bentuk
yang salah di blok itu, bentuk yang BENAR di tempat lain bisa terlihat
memburuk. Konsekuensinya untuk cara kerja: **daftar "sudah dicoba & gagal"
hanya berlaku untuk keadaan blok saat itu.** Sudah masuk README.

Pemeriksaan berdampingan juga menemukan bahwa bentuk lama SALAH secara
semantik, bukan cuma boros: ia membaca byte `p+2` DUA KALI dan tidak pernah
membaca `p+3`. Bentuk baru membaca `p+2` lalu `p+3` seperti aslinya.

### Dicoba dan GAGAL iterasi ini

Gelung aliran bunyi `case 0x04` ditulis ulang sebagai
`for(;;) { scrptr++; if (*scrptr == 0xff && *++scrptr == 0xff) break; }`:
penjajaran TURUN 2.753 → 2.731 walau daftar geserannya terlihat lebih pendek.
Dibatalkan; alasannya ditulis di berkasnya. Bentuk `do/while` dengan `||` yang
benar. Sisa 1 byte di sana: aslinya MEMUAT ULANG `mov ax,[3AEh]` sedangkan kita
memakai ulang SI dari uji pertama.

### Geseran tersisa (3)

`0x21bb:+3`, `0x22da:+4`, `0x23a0:+6`.

---

## `animvm` tahap 11: struktur if/else terbalik — 2.753 → 2.799 (92,1%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.753 / 3.040 (90,6%) | **2.799 / 3.040 (92,1%)** |
| geseran | 3 | **2** |
| panjang | −6 | **−1** |

### ⭐ Arah syarat menentukan LETAK badan — dan jalur jatuh-tembusnya

`case 0` di switch dalam `case 0x0f` ditulis:

```c
if (*scrptr != 0xff) { scrptr++; break; }   /* SALAH */
u5c = 1;
```

Aslinya kebalikannya, dengan `else`:

```c
if (*scrptr == 0xff)                        /* BENAR */
    u5c = 1;
else {
    scrptr++;
    break;
}
/* jatuh tembus ke case -1 */
```

Bedanya bukan cuma `je` vs `jne`: yang kedua menaruh badan-benar LEBIH DULU
lalu `jmp` MELEWATI blok `else` untuk mendarat di badan `case -1`. Jadi
jatuh-tembusnya lewat cabang BENAR sementara cabang salah keluar duluan.
Penjajaran +41 byte dari satu perubahan ini.

### Gelung aliran bunyi: `continue` memaksa muat-ulang

Memecah syarat gelung `case 0x04` jadi dua `if` dengan `continue` memberi
`mov ax,[3AEh]` (muat ulang) seperti aslinya — bukan `mov ax,si`. +5 byte.

⚠ Tapi bentuk itu menyisakan `jmp` MUBAZIR ke instruksi berikutnya, karena
`break`-nya bukan jalur jatuh-tembus. Aslinya keluar lewat FALL-THROUGH dari
`jne` kedua. Bentuk `do/while ||` memberi jatuh-tembus itu TAPI memakai ulang
SI. **Belum ada bentuk yang memberi keduanya** — sisa 1 byte, dicatat di
berkasnya lengkap dengan apa yang sudah dicoba.

### Geseran tersisa (2)

`0x21bb:+3` (dua `jmp 1cd2` berturut di aslinya, yang kedua KODE MATI; kita
cuma satu) dan `0x2304:+1` (jmp mubazir di atas).

---

## `animvm` tahap 12: muatan register = urutan sumber — 2.799 → 2.860 (94,1%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.799 / 3.040 (92,1%) | **2.860 / 3.040 (94,1%)** |
| POSISI | 2.370 | **2.399** |
| panjang | −1 | −1 (tak berubah) |
| geseran | 2 | 2 (tak berubah) |

**+61 byte tanpa mengubah panjang sama sekali** — semuanya beda ISI, bukan
beda ukuran. Ini hasil dari menyisir CELAH (blok yang tidak masuk lari sejajar)
alih-alih daftar geseran.

### ⭐⭐ Muatan register mengikuti urutan SUMBER; simpanannya ditata ulang

Untuk dua pernyataan berurutan — satu menyimpan konstanta-immediate, satunya
menyimpan nilai yang perlu register — kompiler memancarkan:

```
mov ax, <nilai>        ← muatan register: mengikuti urutan SUMBER
mov [immediate], K     ← simpanan pernyataan LAIN, disisipkan
mov [register], ax     ← simpanan pernyataan pertama, DITUNDA
```

Jadi kalau `mov ax,X` muncul SEBELUM sebuah simpanan-immediate, pernyataan yang
memakai X ditulis LEBIH DULU di sumber — walau simpanannya belakangan.

Menukar `sndmode = N; sndptr = ...;` jadi `sndptr = ...; sndmode = N;` di EMPAT
tempat, plus `prevtop`/`prevx` sebelum `ticks`, memberi seluruh +61 byte itu.

**Konsekuensi cara kerja:** jangan membaca urutan pernyataan dari urutan
SIMPANAN — baca dari urutan MUATAN REGISTER. Sudah masuk README.

### Alat baru dalam praktik: sisir CELAH, bukan geseran

Daftar geseran cuma menunjukkan beda PANJANG. Untuk beda ISI, hitung celah
antar-lari-sejajar dari `align_runs()`. Celah terbesar saat ini:
0x1bd2 (48 B), 0x1b1d (26 B), 0x22ea (26 B) — ketiganya blok kegagalan
cabang ZANY/MEKANISME, dan bedanya murni PILIHAN REGISTER (bx/cx/dx bertukar
peran), bukan panjang. Belum ada cara mengendalikannya.

### Dicoba dan GAGAL

Memindah `both = i;` ke belakang pencacah di cabang ZANY: 2.799 → 2.798.
Dibatalkan.

---

## `animvm` tahap 13: aturan urutan-muatan disapukan — 2.860 → 2.913 (95,8%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.860 / 3.040 (94,1%) | **2.913 / 3.040 (95,8%)** |
| POSISI | 2.399 | **2.430** |
| total CELAH | 180 byte | **127 byte** |
| panjang / geseran | −1 / 2 | −1 / 2 (tak berubah) |

Sekali lagi **+53 byte tanpa mengubah panjang** — murni beda isi.

### Aturan tahap 12 dipakai untuk MEMBACA urutan sumber

Blok kegagalan kedua cabang tinggal beda PILIHAN REGISTER. Dengan aturan
"muatan register mengikuti urutan sumber", urutan pernyataannya bisa DIBACA
langsung dari biner, bukan ditebak:

| cabang | urutan muatan di biner | urutan sumber yang disimpulkan |
|---|---|---|
| MEKANISME | `ax=i`, `bx=c1`, `cx=c2` | `both=i; curz=c1; slot=c2;` |
| ZANY | `bx=c2`, `cx=c1`, `dx=i` | `slot=c2; curz=c1; both=i;` |

⚠ Perhatikan: **urutannya BERBEDA di dua cabang yang secara logika kembar.**
Kalau diseragamkan, salah satu pasti rusak. Ini contoh paling bersih dari
aturan "bentuk yang benar ditentukan PER-TEMPAT".

Celah 48 byte dan 26 byte di kedua blok itu turun jadi 21 byte total.

### Dicoba dan GAGAL

Kembali ke `do { scrptr++; } while (*scrptr != 0xff || *++scrptr != 0xff);`
di gelung bunyi `case 0x04` (pengulangan sadar sesuai pelajaran tahap 10,
karena bloknya sudah berubah): 2.913 → 2.908. Bentuk `for`/`continue` tetap
yang benar di sana. Sisa 1 byte-nya `jmp` mubazir yang belum terpecahkan.

### Celah tersisa (127 byte)

`0x22ea` (26), `0x1b22` (21), `0x2313` (13), `0x23b7` (13), `0x1ac6` (11),
`0x2332` (9), `0x1ce0` (8), `0x1a9f` (7).

---

## `animvm` tahap 14: dua penataan ulang kecil — 2.913 → 2.929 (96,3%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.913 / 3.040 (95,8%) | **2.929 / 3.040 (96,3%)** |
| POSISI | 2.430 | **2.437** |
| total CELAH | 127 byte | **111 byte** |

Panjang dan geseran tetap; semuanya beda ISI.

### Dua temuan, keduanya soal URUTAN

1. **`ch18[0] = i + 0x41;` naik ke tepat setelah `both = i;`** di cabang
   MEKANISME. Bukti dari biner: `mov [844h],ax` lalu `add ax,41h` BERURUTAN —
   perhitungannya menempel pada `both`, sedangkan simpanannya ditunda sampai
   sesudah ketiga pencacah. Persis penerapan aturan tahap 12.
   ⚠ Perubahan yang SAMA dicoba di cabang ZANY dan MEMPERBURUK (2.913 → 2.905).
   Di sana ketiga pencacah memang duluan. Kembali lagi: **per-tempat.**

2. **Penugasan nol berturut dipancarkan TERBALIK.** `failed = 0; c2 = 0;
   c1 = 0;` memancarkan simpanan `c1, c2, failed`. Jadi urutan sumber yang
   benar adalah KEBALIKAN urutan simpanan di biner. Membaliknya di sumber
   memberi +7 byte.

   ⚠ Ini pengecualian terhadap kebiasaan membaca urutan dari muatan register:
   di sini TIDAK ADA muatan pembeda (ketiganya `= 0` dari AX yang sama), jadi
   satu-satunya sinyal adalah urutan simpanan — dan sinyal itu TERBALIK.

### Celah tersisa (111 byte)

`0x22ea` (26), `0x2313` (13), `0x23b7` (13), `0x1b1c` (12), `0x1ac6` (11),
`0x2332` (9), `0x1ce0` (8), `0x1a9f` (7).

---

## `animvm` tahap 15: tanpa kemajuan angka — dua bentuk lagi ditutup

TERJAJAR tetap **2.929/3.040 (96,3%)**. Iterasi ini tidak menaikkan angka.
Yang didapat: pemahaman tentang APA yang sebenarnya tersisa, dan dua bentuk
lagi yang terbukti salah.

### ⚠ Sebagian besar "celah" ternyata ARTEFAK, bukan beda isi

Memeriksa celah 0x2313 (13 B) dan 0x23b7 (13 B) berdampingan: keduanya
**sudah identik instruksi-per-instruksi**. Yang membedakan cuma slot relokasi
dan pergeseran alamat 1 byte. `align_runs` memutus lari sejajar di batas slot
relokasi begitu ada geseran, jadi celah-celah itu TERHITUNG padahal isinya
benar.

Artinya: dari 111 byte celah, **hanya sekitar 60 yang beda isi sungguhan**;
sisanya akan lunas sendiri begitu geseran 1 byte di 0x2304 diperbaiki.
Nilai memperbaiki 1 byte itu jauh lebih besar dari kelihatannya.

### Empat bentuk untuk gelung aliran bunyi, tak satu pun lengkap

Yang dibutuhkan SEKALIGUS: (a) keluar gelung lewat FALL-THROUGH, dan
(b) operan kedua MEMUAT ULANG `mov ax,[3AEh]` alih-alih memakai ulang SI.

| bentuk | TERJAJAR | catatan |
|---|---|---|
| `do/while` + `*++scrptr` | 2.908 | fall-through OK, SI dipakai ulang |
| `do/while` + `(scrptr++, *scrptr)` | 2.909 | — |
| `do/while` + `*(scrptr += 1)` | 2.909 | — |
| `for(;;)` + `&&` satu-ekspresi | 2.731 | jauh lebih buruk |
| **`for(;;)` + `continue`** | **2.929** | muat-ulang benar, `jmp` mubazir tersisa |

Semua bentuk `do/while` memberi fall-through tapi memakai ulang SI; satu-satunya
yang memaksa muat-ulang justru yang memancarkan `jmp` mubazir. Aslinya punya
keduanya — jadi masih ada sesuatu di blok itu yang belum dipahami.
Daftar lengkapnya sudah ditulis di `animvm.c` supaya tidak diulang.

---

## `animvm` tahap 16: 2.929 → 2.941 (96,7%)

| | sebelum | sesudah |
|---|---|---|
| TERJAJAR | 2.929 / 3.040 (96,3%) | **2.941 / 3.040 (96,7%)** |
| POSISI | 2.437 | **2.447** |

Satu penataan ulang di cabang MEKANISME: `curz = c1; slot = c2;` DIPINDAH ke
antara `both = i;` dan `ch18[0] = i + 0x41;`. Aslinya memuat `bx=c1`, `cx=c2`
SEBELUM menyimpan `both` — jadi kedua pernyataan itu ada di antara keduanya.

⚠ Ini kombinasi KETIGA yang diuji di blok yang sama:
| urutan | TERJAJAR |
|---|---|
| `both; ch18; curz; slot; pencacah` | 2.929 (tahap 14) |
| `both; curz; slot; ch18; pencacah` | **2.941** |
| `both; curz; slot; pencacah; ch18` | 2.913 (sebelum tahap 14) |

Bedanya cuma letak SATU pernyataan, dan rentangnya 28 byte.

### Cabang ZANY: percobaan yang sama GAGAL untuk KEDUA kalinya

Memindah `both`/`ch18` ke belakang pencacah di cabang ZANY dicoba di tahap 14
(2.913 → 2.905) dan diulang di sini sesuai pelajaran (c) karena bloknya sudah
berubah — hasilnya tetap lebih buruk (2.941 → 2.924). Dua kali gagal dengan
keadaan blok berbeda; sekarang dicatat di berkasnya sebagai jangan-diulang lagi.

Ini juga menutup dugaan lama bahwa kedua cabang "seharusnya" simetris.
Aslinya memang TIDAK simetris: MEKANISME menaruh `both`/`ch18` di tengah,
ZANY di depan pencacah.

### Celah 0x1a9c ternyata artefak juga

Diperiksa berdampingan: sudah identik, cuma slot relokasi. Sama seperti temuan
tahap 15 — periksa isi celah sebelum menggarapnya.

---

## `animvm` tahap 17: tanpa kemajuan — tapi sisa pekerjaannya kini TERUKUR

TERJAJAR tetap **2.941/3.040 (96,7%)**. Tidak ada kemajuan angka.

### ⭐ Kesimpulan: 99 byte celah yang tersisa nyaris SELURUHNYA hilir dari DUA byte

Tiap celah tersisa diperiksa berdampingan. Hasilnya:

| celah | isi | sebab |
|---|---|---|
| 0x2313 (13) | identik | artefak geseran |
| 0x23b7 (13) | identik | artefak geseran |
| 0x1a9c (7) | identik | artefak geseran |
| 0x1ce0 (8) | identik kecuali `jmp 0x2432` vs `jmp 0x2433` | fungsi kita 1 byte lebih pendek |
| 0x1ac6 (11) | idem (`jmp 0x244f` vs `0x2450`) | idem |
| 0x22ea (26) | `jmp` mubazir + hilirannya | geseran 0x2304 |

Jadi ISI `animvm` sudah benar hampir di mana-mana. Yang tersisa: **satu byte
di 0x2304 dan tiga byte di 0x21bb**, dan seluruh sisanya akan lunas sendiri
begitu keduanya beres. Angka 96,7% itu meremehkan keadaan sebenarnya.

### Dua bentuk lagi ditutup untuk 0x21bb — keduanya TIDAK MENGUBAH APA PUN

Aslinya punya DUA `jmp 1cd2` berturut di ujung switch bersarang case 0x03
(yang kedua kode MATI); kita cuma satu. Dicoba:

- membuang `break` di dalam case switch-dalam (badannya jatuh keluar sendiri)
  → keluaran **IDENTIK**, 2.941.
- mengganti `break` case 0x03 dengan `continue` → keluaran **IDENTIK**, 2.941.

Temuan kecil yang berguna: MS C 1.04 **meruntuhkan rantai lompatan** dan
menghasilkan kode yang sama untuk ketiga bentuk itu. Jadi `jmp` mati di biner
asli TIDAK berasal dari salah satu variasi ini — sumbernya masih belum
diketahui, dan tiga bentuk sudah tertutup.

### Keputusan

Dua iterasi tanpa kemajuan di `animvm` (tahap 15 dan 17). Sesuai protokol,
iterasi berikutnya PINDAH ke `main` (2.682/4.219) atau `pickvar` (1.616/1.730),
yang daftar "dicoba & gagal"-nya ditulis SEBELUM aturan tahap 8/11/12/13/14/16
dan karena itu layak ditengok ulang dengan cara baca yang baru.

---

## `pickvar` kembali digarap — dan metrik penjajaran sendiri terbukti bisa MENYESATKAN

Sesudah `animvm` mentok dua iterasi, target pindah ke `pickvar` (1.616/1.730
menurut metrik serakah). Catatan lamanya menduga cacat +3 @0x43B8 berasal dari
"tekanan register dari `k`/`k2` di atasnya" — persis kelas masalah yang
aturan tahap 8/12 pecahkan di `animvm`.

### Percobaan yang dulu gagal, kini berhasil

Menukar `k = list[idx]; k2 = k;` jadi `k2 = list[idx]; k = k2;` pernah dicoba
dan tercatat GAGAL (1.462 vs 1.495) — tapi pengukuran itu dari keadaan blok
yang jauh lebih awal. Diulang sesuai pelajaran (c):

| metrik | sebelum | sesudah |
|---|---|---|
| TERJAJAR (serakah) | 1.616 | 1.583 |
| POSISI | 368 | **1.333** |
| panjang | −4 | **−3** |
| **GLOBAL** | 1.631 | **1.654** |

Geseran `0x4515` juga jadi **+0** (lunas).

### ⚠⚠ Temuan alat: metrik serakah melaporkan TURUN padahal MEMBAIK

Tiga dari empat ukuran menunjukkan perbaikan; hanya yang serakah turun.
Sebabnya: `aligned()` memindai dengan jendela ±24 dan lari minimal 6/12 byte,
jadi begitu POLA divergensi berubah ia bisa gagal menyambung.

`aligncmp.py` sekarang juga mencetak **GLOBAL** (difflib, slot relokasi
diperlakukan wildcard). Aturannya: **GLOBAL untuk memutuskan, serakah hanya
untuk daftar geserannya.**

⚠ Konsekuensi yang lebih luas: keputusan lama yang diambil HANYA dari angka
serakah layak ditinjau ulang. Beberapa entri "sudah dicoba & gagal" di seluruh
proyek mungkin sebenarnya berhasil. Sudah masuk README.

Sebagai perbandingan, `animvm` dengan metrik baru: GLOBAL 2.900/3.040 (95,4%)
vs serakah 2.941 — di sana yang serakah justru sedikit terlalu murah hati.
Keduanya dekat, jadi kesimpulan `animvm` tidak berubah.

---

## `main`: perancah 2 byte membuka 363 byte — GLOBAL 2.852 → 3.215 (76,2%)

| | sebelum | sesudah |
|---|---|---|
| GLOBAL | 2.852 / 4.219 (67,6%) | **3.215 / 4.219 (76,2%)** |
| TERJAJAR (serakah) | 2.690 | 3.986 |
| panjang | −25 | **−12** |
| geseran | 16 | **4** |

Catatan lama `main` sudah mendiagnosis dengan benar: aslinya memesan 4 kata
temp, kita 3, dan selisih 2 byte itu menggeser SEMUA lokal ke bawah. Yang
belum dicoba: ganjal di DEPAN.

### `int` tak terpakai DIALOKASIKAN; `char x[2]` tak terpakai DIBUANG

Catatan lama menemukan `char x[2]` yang tak dirujuk dibuang kompiler, dan
`char x[3]`/`x[4]` jadi 4 byte — jadi tidak ada cara membuat ganjal 2 byte
dengan larik char. Tapi **`int tpad;` yang tak terpakai TETAP dialokasikan.**
Itu ganjal 2 byte yang dicari.

### Kenapa ini sah sebagai perancah, sedangkan percobaan lama tidak

Percobaan lama membesarkan `lvlbuf` 2 byte: angkanya naik, tapi lvlbuf dan
recs jadi duduk di offset yang jelas SALAH menurut biner. Ganjal di DEPAN
menggeser semuanya naik seragam **tanpa mengubah ukuran atau urutan penyangga
mana pun** — semua offset lokal jadi cocok persis dengan biner.

⚠ Tetap PERANCAH, bukan kebenaran: pemicu kedalaman ekspresi yang membuat
kompiler asli memesan kata temp keempat masih belum ketemu. Sudah ditulis di
kepala `main_.c` supaya `tpad` dibuang begitu pemicunya ketemu.

Nilainya: 12 dari 16 geseran lunas sekaligus, jadi divergensi lain di `main`
sekarang BISA DILIHAT dan digarap — sebelumnya semuanya tertutup pergeseran
seragam ini.

### Verifikasi

LINK bersih, DATA 100%, symcheck CURIGA 0.
`fixorder main_`: 455 slot cocok, 11 BEDA (naik dari 10 karena lebih banyak
wilayah kini sejajar dan bisa diperiksa), 19 di luar lari sejajar.

---

## `main`: aturan urutan-muatan dipakai dua kali — GLOBAL 3.215 → 3.218

| | sebelum | sesudah |
|---|---|---|
| GLOBAL | 3.215 / 4.219 | **3.218 / 4.219 (76,3%)** |
| TERJAJAR (serakah) | 3.986 | **4.013** |
| geseran | 4 | **3** |
| `fixorder` BEDA simbol | 11 | **7** |

Dua penataan ulang, keduanya DIBACA dari urutan muatan register, bukan ditebak:

1. Blok pembuka. Aslinya memuat `ax=&ytop`, `bx=_TOP`, `cx=&basebuf`,
   `dx=&recs` lebih dulu lalu memakai ulang AX untuk `&objs` dan `&lvlbuf`.
   Urutan sumbernya jadi: `ytop_`, `g83a`, `base`, `recbase`, `objtab`,
   `level_` — bukan urutan simpanannya. Geseran `0x00d1` lunas.
2. Blok `page`/`prevx`. Aslinya `mov ax,140h` DULU, jadi `prevx`/`prevtop`
   ditulis sebelum `page`/`page2`.

`fixorder` turun dari 11 ke 7 BEDA identitas simbol — artinya sebagian
"beda simbol" itu tadinya cuma efek wilayah yang belum sejajar.

### ⚠ `main` juga punya TABEL DATA TERTANAM

Disassembly berhenti di **0x0487** (asli) / 0x04f8 (kita) — sama seperti
`animvm` yang tabelnya di tengah fungsi. Semua pemeriksaan berdampingan di
atas 0x487 HARUS memakai potongan disassembly terpisah, kalau tidak wilayah
itu tak akan terlihat sama sekali. Geseran `0x069f` dan `0x0c19` ada di
wilayah itu dan BELUM diperiksa.

### Sisa

Geseran `0x013d:+2` masih ada: aslinya memuat `bx=26Ch`/`cx=284h` ke REGISTER
lalu menunda simpanannya, kita memancarkan simpanan-immediate langsung.
Penataan ulang sudah membuat `mov ax,140h` cocok, tapi bentuk yang memaksa
pemuatan-ke-register belum ketemu.

---

## `main`: `sclo` ternyata `long` — GLOBAL 3.218 → 3.378 (80,1%)

| | sebelum | sesudah |
|---|---|---|
| GLOBAL | 3.218 / 4.219 (76,3%) | **3.378 / 4.219 (80,1%)** |
| panjang | −11 | **−1** |
| `fixorder` BEDA simbol | 7 | **4** |

### ⭐ Penolan `long` = DUA simpanan-immediate, bukan dua simpanan-AX

Blok reset skor di biner:

```
0668 xor ax,ax
066a mov word ptr [732h], 0     <- immediate, 6 byte
0670 mov word ptr [730h], 0     <- immediate, 6 byte
```

Kita menulis `schi = 0; sclo = 0;` sebagai dua `int`, dan kompiler MEMAKAI
ULANG `AX=0` yang sudah ada — 3 byte masing-masing, 6 byte lebih pendek.
Aslinya TIDAK memakai ulang AX walau AX=0 tersedia tepat di atasnya. Itu
tanda pengenal **penugasan nol pada satu `long`**: `sclo = 0;` dengan
`extern long sclo;` memancarkan dua simpanan-immediate, hi dulu lalu lo.

Catatan lama sudah mencoba lima urutan pernyataan berbeda dan `schi = sclo = 0`
untuk memaksa bentuk immediate, semuanya gagal — karena masalahnya bukan
urutan atau bentuk penugasan, melainkan **TIPE**. Ini kemunculan KETIGA pola
"deklarasikan ulang simbol gdata sebagai tipe lain di satu berkas" setelah
`char *scrptr` dan `long sclo` di `animvm`.

### Dua penataan ulang pendukung

- Blok pembuka: urutan dibaca dari muatan (`ytop_`, `g83a`, `base`, `recbase`,
  `objtab`, `level_`).
- Blok `tx`/`ta`/`range`/`count`: `mov bx,140h` DULU, jadi `tx` pernyataan
  pertama; `sub bx,14h` menempel pada `range`; `count` sesudahnya.

### ⚠ `main` punya TIGA tabel lompat PADAT

Bentuk switch KETIGA (`jmp cs:[si*2+basis]`), berbeda dari tabel PINDAI di
`animvm`/`pickvar`. Dispatchernya di 0x0496, 0x0509, 0x10e0 (asli) — struktur
kita SAMA (0x0494, 0x0507, 0x10d5). Displacement tabelnya slot relokasi, jadi
tidak bisa dibandingkan langsung dari .OBJ.

⚠ Capstone berhenti di tiap tabel TANPA peringatan. Disassembly harus dimulai
ulang di 0x0488, 0x0511, dan sesudah 0x10ca. Sebelum ini, seluruh wilayah
0x0511..0x10fc — dua pertiga fungsi — TIDAK PERNAH TERLIHAT.

---

## `main`: tanpa kemajuan angka — tapi satu KESALAHAN STRUKTUR terlokalisasi

GLOBAL tetap **3.378/4.219 (80,1%)**. Iterasi ini tidak menaikkan angka.

### ⚠⚠ Blok yang seharusnya DI DALAM `if` berjalan tanpa syarat (0x0C14)

Wilayah 0x0511..0x10fc baru bisa dilihat sejak tabel lompatnya dipetakan.
Sisiran pertama langsung menemukan kesalahan struktur nyata:

```
asli:  cmp [bp+6F1Eh],1 / je 0C19h / jmp 0D15h      <- lompat JAUH melewati badan
kita:  cmp [bp+6F1Eh],1 / jne 0C42h                 <- lompat pendek
```

Kompiler asli memakai `je`+`jmp` justru KARENA jarak lompatnya > 127 byte.
`jne` pendek kita muat **karena badan `if` kita berakhir terlalu cepat**: di
biner seluruh blok 0x0C43..0x0D14 masih DI DALAM `if` itu, sedangkan di sumber
kita blok yang sama berjalan TANPA SYARAT.

Kode di 0x0C43 dan sesudahnya sudah cocok instruksi-per-instruksi — yang salah
murni LETAK KURUNG TUTUP. Sudah dicatat di kepala `main_.c`.

⭐ Pola yang bisa dipakai lagi: **`je <dekat>` + `jmp <jauh>` di biner sementara
kita memancarkan satu lompatan pendek = badan blok kita KEPENDEKAN.** Panjang
lompatan adalah petunjuk struktur, bukan cuma detail penyandian.

### Dicoba dan GAGAL

Memindah kelompok penugasan nol ke DEPAN `sclo = 0` (mengikuti `xor ax,ax`
yang muncul lebih dulu di biner): GLOBAL **3.378 → 3.270**, walau geseran
turun 4 → 2 dan TERJAJAR naik 3.999 → 4.062. Contoh ketiga bahwa daftar
geseran yang lebih pendek TIDAK berarti lebih baik. Dibatalkan dan dicatat.

---

## `main`: kurung tutup memang salah — tapi memperbaikinya SENDIRIAN merugikan

GLOBAL tetap **3.378/4.219 (80,1%)**. Tidak ada kemajuan angka.

### Diagnosis tahap sebelumnya TERKONFIRMASI

`if (p1 == 1)` di `case 3` memang ditutup terlalu awal: di biner ia menutup
baru SESUDAH `fillans(...)` (0x0D14). Setelah kurungnya dipindah, pasangan
cabangnya **cocok persis**:

| | kita (sesudah) | asli |
|---|---|---|
| | `je 0C1Bh` / `jmp 0D17h` | `je 0C19h` / `jmp 0D15h` |
| ujung `if` | 0x0D17 | 0x0D15 |

Panjang fungsi juga bergerak persis seperti diramalkan: −1 → +2 (tepat +3,
selisih `je`+`jmp` vs `jne`).

### ⚠ Tapi hasilnya MEMBURUK — dan itu diukur, bukan dikira

| | sebelum | sesudah |
|---|---|---|
| wilayah 0x0C00..0x0D40 | **291 / 320** | 275 / 320 |
| GLOBAL seluruh fungsi | **3.378** | 3.276 |

Sebabnya sudah dipahami: memasukkan `fillans(...)` ke dalam `if` mengubah
TEKANAN REGISTER se-blok (aturan tahap 8), jadi kode panggilan itu sendiri
ikut berubah dan kehilangan lebih banyak daripada yang didapat cabangnya.

Jadi: **letak kurungnya memang salah, tapi memperbaikinya SENDIRIAN merugikan.**
Ada penyesuaian lain di blok yang sama yang harus dilakukan BERSAMAAN.
Dibatalkan, dan alasannya lengkap dengan angkanya ditulis di `main_.c`.

### Pelajaran cara kerja

Ketika bukti LOKAL (pasangan cabang cocok persis) bertabrakan dengan angka
AGREGAT, ukur WILAYAHNYA — bukan pilih salah satu berdasarkan firasat.
Pengukuran wilayah 0x0C00..0x0D40 yang menyelesaikan perdebatan ini dalam satu
langkah, dan hasilnya kebetulan berlawanan dengan dugaan awal.

---

## Papan skor GLOBAL untuk semua fungsi yang belum exact (2026-07-31)

Metrik GLOBAL yang baru dipakai untuk mengukur ULANG semuanya. Angka ini jauh
lebih berguna daripada angka serakah yang tercatat di dokumen lama:

| fungsi | GLOBAL | panjang | geseran |
|---|---|---|---|
| `place` | **501 / 503 (99,6%)** | tepat | — |
| `f498c` | **162 / 165 (98,2%)** | tepat | — |
| `loadcon` | 683 / 739 (92,4%) | tepat | 2 |
| `main_` | 3.378 / 4.219 (80,1%) | −1 | 4 |
| `pickvar` | 1.654 / 1.730 (95,6%) | −3 | 2 |
| `animvm` | 2.900 / 3.040 (95,4%) | −1 | 2 |
| `nvar` | 411 / 566 (72,6%) | −15 | 2 |

`place` dan `f498c` ternyata TINGGAL 2-3 BYTE — jauh lebih dekat daripada
kesan yang diberikan angka lama. `nvar` yang paling jauh.

## `nvar`: dugaan lama dibantah oleh metrik baru

Catatan `nvar` menyimpan satu percobaan dengan hasil "BERCAMPUR": bentuk
penunjuk-char `((char *)recbase)[list[r] * 0xc + 1]` memperbaiki PANJANG 8 byte
(551 → 559, target 566) tapi memperburuk BINGKAI (0x3c → 0x3e). Kesimpulan
yang ditarik waktu itu: "bentuk ekspresinya kemungkinan BENAR tapi memakan satu
temp lagi; cari 3 slot yang harus dilepas di tempat lain."

Diuji ulang dengan metrik GLOBAL: **411 → 335 / 566**. Jauh lebih buruk.
Panjang yang membaik ternyata mengorbankan ISI jauh lebih banyak — persis
jenis kesimpulan salah yang bisa ditarik kalau cuma melihat panjang.
Dugaan itu sekarang DIBANTAH dan dicatat di berkasnya; bentuk lama tetap
yang terbaik.

⚠ Ini kebalikan dari kasus `pickvar` (di mana metrik lama menyembunyikan
perbaikan). Metrik baru bekerja dua arah: ia membatalkan dugaan yang salah
DAN memulihkan percobaan yang salah dibuang.

---

## `f498c`: sisa 3 byte terbukti MURNI pilihan register

GLOBAL tetap **162/165 (98,2%)**, panjang tepat. Tidak ada kemajuan angka.

Divergensinya terisolasi sempurna ke satu tempat, 0x49BC..0x49C5:

```
kita: mov bx,[bp+7Ch] / add bx,ax / push [bx]
asli: mov si,[bp+7Ch] / add si,ax / push [si]
```

Panjangnya IDENTIK — yang beda cuma REGISTER. Aslinya MEMAKAI ULANG SI yang
tadi dipakai untuk `sel[i]`; kita mengambil BX yang baru bebas sesudah
`imul bx`.

### Dua bentuk indeks disapu, keduanya tidak membantu

| bentuk | GLOBAL |
|---|---|
| `nvar(tab[i * 3 + 2], buf)` (sekarang) | 162/165 |
| `nvar(tab[3 * i + 2], buf)` | 162/165 — **identik** |
| `nvar(*(tab + i * 3 + 2), buf)` | 150/165 — jauh lebih buruk |

Jadi bentuk ekspresi indeksnya BUKAN pengungkitnya. Yang tersisa: mengubah
tekanan register SE-BLOK lewat urutan/struktur pernyataan LAIN di dalam gelung
— sudut yang sama seperti yang memecahkan `animvm` tahap 8. Sudah dicatat di
`f498c.c` supaya sweep ini tidak diulang.

⚠ `place` (501/503) tersisa dengan gejala yang SAMA PERSIS (SI vs DI di
+407/+410). Kedua fungsi ini kemungkinan besar butuh pengungkit yang sama, dan
menemukannya sekali akan menuntaskan keduanya.

---

## `loadcon`: 683 → 687 lewat aturan "penugasan nol dipancarkan TERBALIK"

| | sebelum | sesudah |
|---|---|---|
| GLOBAL | 683 / 739 (92,4%) | **687 / 739 (93,0%)** |
| celah terbesar | 36 B @0x5281 | idem |

Biner menyimpan `i` lalu `zcnt`; sumber kita `i = 0; zcnt = 0;` justru
memancarkan urutan terbalik. Ditukar jadi `zcnt = 0; i = 0;` → cocok.
Penerapan lagi dari aturan: **untuk penugasan nol berturut yang berbagi satu
register, urutan SIMPANAN adalah KEBALIKAN urutan sumber.**

### ⚠ `fixorder` bisa melaporkan BEDA SIMBOL PALSU di wilayah yang belum sejajar

`fixorder loadcon` melaporkan 1 BEDA di +587: kita `nmech` (0x3ac), asli
`nzany` (0x4b4). Terlihat seperti kesalahan operan yang jelas. Ditukar jadi
`(nmech + nzany) * 2` — hasilnya **GLOBAL 687 → 682 dan BEDA malah 1 → 2.**

Jadi laporan itu ARTEFAK: +587 jatuh di sekitar 0x527E yang memang belum
sejajar, sehingga pemetaan offset-nya meleset dan membaca simbol tetangga.
`fixorder` sudah menyaring slot "di luar lari sejajar", tapi slot di TEPI
wilayah sejajar masih bisa lolos.

⭐ Aturan kerja: **verifikasi laporan `fixorder` dengan mengukur GLOBAL sesudah
perbaikan.** Kalau GLOBAL turun DAN jumlah BEDA naik, laporan itu palsu.

### Kerja `loadcon` sebelumnya sudah sangat menyeluruh

Sisa 36 byte di 0x5281 berpangkal pada satu keputusan register yang sudah
dipersempit sampai SATU instruksi dan diuji lewat probe11/12/13 (10 varian
total, semuanya memancarkan perilaku yang BENAR). Jadi pemicunya bukan bentuk
sumber di tempat itu — konsisten dengan pelajaran tahap 8 bahwa sebabnya bisa
jauh dari tempat akibatnya terlihat.

---

## `nvar`: dugaan "semuanya soal bingkai" DIUKUR dan ternyata terlalu optimis

Tidak ada kemajuan angka (GLOBAL tetap 411/566).

### Sapuan pola "penugasan nol terbalik" — sudah benar di mana-mana

Aturan yang membayar di `loadcon` dan `main` disapukan ke fungsi lain. Blok
penolan fase 2 `nvar` diperiksa: biner menyimpan `i`, `cnt`, `acc`; sumber kita
`acc = 0; cnt = 0; i = 0;` — sudah KEBALIKANNYA, jadi sudah benar. Cocok persis
modulo geseran bingkai. Tidak ada sasaran tersisa untuk pola ini.

### ⚠ Uji yang membantah hipotesis saya sendiri

`nvar` bingkainya 0x3c vs 0x38 — 2 kata temp KELEBIHAN, jadi SEMUA lokal
bergeser +4. Hipotesisnya: seperti `main`, memperbaiki bingkai akan melunasi
hampir semuanya.

Diuji langsung: normalkan displacement lokal kita (kurangi 4 dari tiap
`[bp+N]` dengan N ≥ 8) lalu banding di tingkat INSTRUKSI.

| | hasil |
|---|---|
| instruksi kita / asli | 207 / 214 |
| cocok sesudah normalisasi | **141 / 214 (65,9%)** |

Jadi bingkai BUKAN satu-satunya masalah — masih ada ~73 instruksi yang memang
beda isi. `nvar` tidak akan seperti `main` (di mana ganjal 2 byte melunasi 12
dari 16 geseran). Dugaan itu sekarang dicabut dari `nvar.c`.

⭐ Tekniknya sendiri layak dipakai lagi: **normalisasi displacement lalu banding
tingkat instruksi** memisahkan "salah bingkai" dari "salah isi" dalam satu
pengukuran, sebelum menghabiskan iterasi mengejar yang salah.


## `main` TIDAK punya lubang struktural lagi — 841 byte itu 514 luka kecil

Diukur 2026-07-31 dengan difflib atas seluruh fungsi (slot relokasi
di-wildcard), lalu celah yang tak tercocokkan didaftar per-ukuran:

```
total celah: 841   jumlah celah: 514
celah TERBESAR: 0x0690=14B, 0x0681=13B, 0x0132=6B, 0x04e5=5B,
                0x0a36=4B, 0x0bfe=4B, 0x0e01=4B, sisanya <= 3B
```

Ini mengubah strategi untuk `main`. Selama ini 80,1% dibaca sebagai "masih ada
bagian yang belum ditulis". Salah: **strukturnya sudah lengkap**. Rata-rata
celah 1,6 byte — itu profil selisih register/displacement, bukan blok hilang.
Artinya `main` kini masuk kelas kesulitan yang SAMA dengan `place` dan `f498c`,
bukan kelas "tinggal ditulis". Jangan lagi memperlakukannya sebagai sasaran
volume.

Satu-satunya gugusan nyata: 0x0681 + 0x0690 = 27 byte dalam jendela 30 byte —
tepat di antara pasangan geseran 0x066a:+4 / 0x069c:−2. Di situlah blok enam
simpanan nol berada, dan aturan barunya dicatat di README.

## `main`: kurung tutup di 0x0C14 DITOLAK LAGI, kali ini dengan GLOBAL

Percobaan sebelumnya ditolak lewat metrik WILAYAH (291 → 275). Diulang dan
diukur penuh: GLOBAL **3.378 → 3.276 (−102)**, walau geseran 0x0c19:+1 HILANG
sepenuhnya dan TERJAJAR naik 3.999 → 4.004.

Tiga metrik independen kini sepakat menolaknya. Lebih berguna lagi, panggilan
`fillans(...)` di dalam kurung itu dibandingkan instruksi-per-instruksi dan
COCOK PENUH — keempat belas `push`-nya sama, semua beda cuma slot relokasi.
Jadi geseran +1 di 0x0c19 BUKAN berasal dari letak kurung maupun dari bentuk
panggilan di dalamnya; keduanya sudah tertutup sebagai hipotesis.

## Alat ad-hoc ketiga yang salah — jangan bikin peta beda sendiri

Peta kepadatan beda per-128-byte yang ditulis buru-buru melaporkan 3.898 byte
beda untuk `main`, padahal TERJAJAR mengatakan 3.999 byte COCOK. Sebabnya model
"geseran kumulatif" itu terlalu naif. Dibuang; penggantinya memakai difflib yang
sama dengan metrik GLOBAL sehingga hasilnya pasti konsisten. Ini kejadian
KETIGA (metrik serakah, `fixorder`, sekarang ini) — pelajaran (h) berlaku juga
untuk alat yang baru saja kita tulis sendiri, bukan cuma yang lama.


## Sapuan PROFIL CELAH: cuma `nvar` yang masih "volume" (2026-07-31)

Alat baru `src_c/verify/gapprof.py` dijalankan atas ketujuh fungsi yang belum
exact. Tabelnya ada di README. Kesimpulan yang mengubah rencana kerja: enam dari
tujuh sudah LENGKAP secara struktur; yang tersisa di sana murni alokasi register.
Hanya `nvar` yang masih punya celah >= 20 B.

Karena itu urutan prioritas lama ("garap yang persentasenya paling rendah")
salah arah. `main` (80,1%) justru sekelas `place` (99,6%) dalam hal JENIS
kesulitan; yang membedakan cuma banyaknya luka, bukan sifatnya.

## `nvar`: gumpalan 0x41b4..0x423e dibedah, empat bentuk sumber diuji, semua gagal

Disassembly berdampingan menunjukkan sebabnya jelas dan konsisten:

```
ASLI  41af mov ax,[bp+0ah]      KITA  41af mov ax,[bp+0eh]
      41b2 inc word ptr [bp+0ah]      41b2 mov [bp],ax        <- tumpahan
      41b5 shl ax,1                   41b5 inc ax
                                      41b6 mov bx,[bp]        <- dibaca lagi
```

Aslinya menyimpan `cnt` yang baru KE MEMORI SEGERA (`inc word ptr`), sehingga
nilai lama cukup ditahan di AX. Kita MENUNDA simpanan `cnt` sampai akhir
pernyataan, jadi nilai BARU yang menempati AX dan nilai lama harus ditumpahkan
ke temp — persis dua kata temp yang membuat bingkai kita 3ch vs 38h.

Akibat lanjutannya terlihat 40 byte kemudian: aslinya menahan `list` di BX dari
0x41c0 sampai 0x41f0 dan memancarkan `mov ax,cx / mov dx,0ch / imul dx` (7 B),
kita kehilangan BX dan memancarkan `mov ax,0ch / imul dx` (5 B) plus `mov si,cx`
tambahan. Jadi satu keputusan di 0x41b2 membiayai selisih di seluruh blok —
contoh paling bersih dari pelajaran (a).

Empat bentuk sumber diuji, GLOBAL dasar 411/566:
```
E2  ternary menggantikan if/else untuk r        -> 401  (-10)
E3  arah syarat dibalik (b >= a)                -> 390  (-21)
E4  (recbase + list[r])->row                    -> 411  (BYTE-IDENTIK, lihat README)
E5  if (r != 0) menggantikan if (r > 0)         -> 410  (-1)
```
Tidak satu pun memicu bentuk `inc word ptr [cnt]`. Yang menentukan bukan bentuk
ekspresi di sekitarnya melainkan kapan simpanan `cnt` boleh dilakukan; pengungkit
untuk itu belum ketemu.


## ✅ `nvar` SELESAI byte-per-byte — 411/566 -> 566/566 (2026-07-31)

Fungsi ke-76 yang cocok. `verifyall`: COCOK 76/81, 15.646 byte (naik 566).
Satu-satunya fungsi berprofil VOLUME kini habis; sisanya semua kelas register.

Perubahannya SATU baris: dua `if` bersarang digabung jadi `if (A && B)`.
Aturannya dicatat lengkap di README.

Yang membuat ini layak diingat adalah bagaimana diagnosis SALAH bertahan lama.
Gejala yang paling mencolok — `cnt++` kita jadi tumpahan temp sedangkan asli
`inc word ptr [bp+0ah]` — dikejar lewat empat probe (ternary 401, arah syarat
390, penunjuk 411 byte-identik, `r != 0` 410), semuanya gagal. Yang akhirnya
membongkarnya adalah pertanyaan yang seharusnya ditanyakan LEBIH DULU:

  "idiom yang sama dipakai di DUA tempat — apakah yang satu lagi cocok?"

Fase 1 memakai `list[cnt++] = i;` dan biner asli di sana justru memancarkan
bentuk TUMPAHAN yang sama dengan kita (0x4100 `mov ax,[bp+0ah]`, 0x4106 `inc ax`,
0x4119 simpanan ditunda). Begitu itu terlihat, "bentuk `cnt++` salah" langsung
gugur, dan perhatian pindah ke apa yang BEDA antara kedua tempat itu — yaitu
`if` bersarang di fase 2.

⭐ Teknik yang lahir dari sini dan layak dipakai lagi: **kalau sebuah idiom
dicurigai salah, cari tempat LAIN di fungsi yang sama memakai idiom itu.** Kalau
di sana cocok, idiomnya bukan sebabnya — dan itu satu pengukuran yang jauh lebih
murah daripada menebak bentuk sumber.

Petunjuk kedua yang terlewat: 48 celah SATU BYTE merata dari 0x4097 sampai
0x41ae. Keseragaman itu tanda bingkai bergeser, bukan isi yang salah — dan
seharusnya langsung mengarahkan ke "kenapa bingkai kita 2 kata lebih besar",
bukan ke bentuk pernyataan.


## Sapuan aturan `&&` ke semua fungsi sisa — `nvar` satu-satunya yang kena

Begitu aturan `if (A) { if (B) }` -> `if (A && B)` ditemukan, ia langsung
disapukan. Hasilnya JANGAN dipakai sebagai "aturan ini jarang berguna" —
dipakainya sekali sudah menyelesaikan satu fungsi utuh.

Penyaring pertama, GEJALA BINGKAI: tak satu pun fungsi sisa punya bingkai lebih
besar dari asli.
```
pickvar 0x52 = 0x52   place 0x26 = 0x26   f498c 0x74 = 0x74   animvm 0x6a = 0x6a
```
Jadi tidak ada lagi yang menunjukkan gejala utama `nvar`.

Penyaring kedua, KANDIDAT SINTAKSIS (`if` bersarang yang `if` dalamnya adalah
pernyataan pertama):
* `pickvar` baris 207 — bentuknya PERSIS seperti `nvar`, termasuk pembanding
  `- 100 ==`. Digabung: GLOBAL **1.654 -> 1.567 (-87)**. DITOLAK. Bersarangnya
  memang asli di sana. Kemiripan bentuk sumber BUKAN bukti; tetap harus diukur.
* `animvm` baris 214 dan 269 — keduanya TIDAK MEMENUHI SYARAT: ada kode lain di
  dalam `if` luar sesudah blok `if` dalam, jadi `&&` akan mengubah semantik.
  Alat penggabung menolaknya sendiri lewat assert, bukan diam-diam menghasilkan
  kode yang salah.

Kesimpulan: sasaran untuk aturan ini habis. Sisa pekerjaan seluruhnya kelas
alokasi register.


## `loadcon` dipersempit ke DUA situs; predikat untuk aturan `&&` ditemukan

**`loadcon`** — bingkai KITA = ASLI (`sub sp,0x124`), panjang TEPAT 739. Diff
tingkat instruksi: 268 instruksi di kedua sisi, 224 cocok. Dari 44 situs yang
"beda", hampir semuanya PALSU (operan slot relokasi). Yang NYATA cuma dua:

```
0x5115  KITA mov bx,[lastgoal] / cmp bx,[sub]     ASLI mov ax,... / cmp ax,...
0x527e  KITA mov ax,[A] / mov dx,[B] / add dx,ax  ASLI mov ax,[A] / add ax,[B]
```

Yang kedua penting karena idiom yang SAMA muncul 60 byte sebelumnya di 0x5239
dan di sana bentuk kita SUDAH BENAR (`mov ax,X / add ax,Y`). Jadi per teknik (A)
bentuk sumbernya BUKAN sebabnya — konteksnya yang beda. Sejalan dengan
probe11..13 yang dulu mereproduksi bentuk lokal ini dan semua variannya
memancarkan perilaku yang benar.

**Predikat untuk aturan `&&`** — empat titik data, tabelnya di README.
Ringkasnya: pertukaran hanya berpengaruh kalau syarat dan badan berbagi
subekspresi MAJEMUK. `place` baris 129 dipecah dan keluarannya BYTE-IDENTIK
(hash b3ae839b60d6fec7); `pickvar` 317 juga tak berubah — keduanya tidak berbagi
apa pun yang layak di-CSE. Predikat menyaring kandidat; arahnya tetap harus
diukur, karena `nvar` dan `pickvar` 207 nyaris sama tapi jawabannya BERLAWANAN.

Alat pemecah menolak sendiri lima dari enam kandidat `pickvar` (karena `while`,
atau tak berkurung) — menolak lebih baik daripada diam-diam mengubah semantik.


## `animvm`: satu syarat dibaca TERBALIK — koreksi dari biner, bukan dari nama

`animvm` 2.900 -> 2.901/3.040. Angkanya cuma +1 byte, tapi yang diperbaiki
adalah SEMANTIK, bukan sekadar byte.

Di 0x1c72 biner asli memancarkan `je 0x1cd2` — melompat KELUAR blok saat
`i == n1 + n2 - 1`. Sumber kita memancarkan `jne`. Jadi badan bonus itu berjalan
saat `i != n1 + n2 - 1`, bukan saat sama. Komentar lama di berkas ("Bonus hanya
di langkah TERAKHIR") adalah TEBAKAN yang berangkat dari nama variabel, bukan
bacaan kode — persis kesalahan yang aturan kerja no. 1 larang. Sudah dikoreksi
di sumber DAN di komentarnya.

Kenapa cuma satu dari tiga syarat yang membedakan: `mode == 4` yang salah dan
`mode != 4` yang benar sama-sama memancarkan `jne` ke sasaran lewat. Hanya
syarat PERTAMA yang arahnya terbaca dari opcode. Pelajaran umum: dalam rantai
`&&`, hanya syarat pertama yang arahnya bisa diverifikasi dari satu opcode;
sisanya ambigu dan harus diperiksa lewat sasaran lompatannya.

## Diff instruksi KASAR (mnemonic + register saja) — cara membaca fungsi besar

Dua percobaan pertama gagal: normalisasi yang tidak simetris melaporkan 49
"beda" pada `call` saja, dan capstone ikut membaca tabel data di 0x23d4
sehingga jumlah instruksi meleset (1.124 vs 1.039).

Yang berhasil: batasi rentang SEBELUM tabel data, lalu ganti SEMUA literal heksa
di kedua sisi dengan satu penanda. Hasilnya `animvm` 1.020/1.037 instruksi cocok
(98,4%) dengan hanya TUJUH situs beda — dan salah satunya langsung menunjuk
`je`/`jne` di atas. Bandingkan dengan profil celah byte yang melaporkan 114
celah: diff kasar memisahkan "beda BENTUK" dari "beda ALAMAT" yang bukan soal.

## `loadcon`: bentuk ekspresi `expect` digugurkan (tiga varian)

Dasar GLOBAL 687/739. `expect` dipecah jadi dua pernyataan -> 665; `2 * (nzany +
nmech)` -> 687 (sama); dijabarkan `nzany * 2 + nmech * 2` -> 669. Tidak ada yang
menyentuh situs 0x527e.

Menguatkan kesimpulan sebelumnya: bentuk sumber di sana BUKAN pemicunya —
`(nzany + nmech) * 2` yang SAMA persis di baris 151 sudah memancarkan bentuk
yang BENAR (`mov ax / add ax`) di 0x5239.

⚠ JEBAKAN HARNESS yang hampir lolos: sapuan pertama tiga varian ini melaporkan
687 untuk KETIGANYA. Sebabnya salah indeks argumen — ketiganya menulis literal
`"x"` ke berkas, kompilasi gagal, dan `.OBJ` LAMA yang terukur. Sejak itu tiap
pengukur menghapus `.OBJ` dulu dan menolak melapor kalau kompilasi gagal. Ini
kejadian KEDUA dari kelas yang sama (yang pertama: `cp` ke `/tmp` yang tidak ada).


## `animvm` 2.901 -> 2.921 lewat DUA `default:` yang hilang

96,1%. Profil celah berubah dari 140 B/114 celah jadi **119 B/76 celah**,
terbesar 5 B. Diff instruksi kasar: 1.021 -> 1.029 dari 1.037 cocok.

Keduanya ditemukan lewat gejala yang SAMA di diff kasar: `insert @asli` berupa
satu `jmp` tepat sebelum sebuah tabel switch (0x21b7 sebelum tabel 0x21ba, dan
0x23d1 sebelum tabel 0x23d4). Aturannya dicatat di README.

Yang menarik: `default:` DI DEPAN `case 0xff` tidak berpengaruh (2.908), yang
DI BELAKANG memberi +13. Jadi bukan keberadaan `default:` yang penting,
melainkan bahwa badan `case` terakhir berhenti menjadi yang terakhir.

Sisa di `animvm` (3 situs bentuk):
* 0x22ea — KITA punya `jmp` yang ASLI tidak punya (kelebihan `break`?)
* 0x23d1 — masih dilaporkan hilang walau GLOBAL naik; perlu dicek ulang apakah
  laporan itu artefak penjajaran sesudah tabel
* 0x235c/0x2365/0x2374 — di sekitar tabel pindai 0x235a; kemungkinan besar
  ARTEFAK karena tabel kita bergeser 2 byte akibat `jmp` ekstra di 0x22ea.
  Perbaiki 0x22ea dulu, baru nilai ulang ketiganya.

⚠ Catatan alat: byte tabel switch KITA tampak acak di disassembly karena
wildcard slot relokasi memakai offset KITA; kalau tabel bergeser relatif ke
asli, byte yang disalin mendarat di posisi yang salah. Jangan membaca isi tabel
dari keluaran ber-wildcard.


## ✅ `animvm` SELESAI byte-per-byte — 3.040/3.040 (2026-07-31)

Fungsi ke-77 dan yang TERBESAR di antara sisa. `verifyall`: COCOK 77/81,
18.686 byte (naik 3.040). Kode C game 60,2% -> **71,9%**; TOTAL 68,6% -> **76,8%**.

Jalannya dalam satu iterasi: 2.901 -> 2.908 -> 2.921 -> 2.961 -> **3.040**.

1. `default: break;` di switch DALAM (case 0x03) — +7.
2. `default: break;` di switch UTAMA sesudah `case 0xff` — +13.
3. Gelung bunyi ditulis ulang dengan **dua `goto` ke satu label** — +40.
   Ini yang menentukan; aturannya di README.
4. `default:` di switch UTAMA DIHAPUS lagi — +79, jadi 100%.

Butir 4 adalah pelajaran yang paling layak diingat. Perbaikan di butir 2 BENAR
menurut pengukuran saat itu (+13), tapi ia sebenarnya menambal geseran 3 byte
yang disebabkan gelung bunyi yang masih salah. Sesudah butir 3, ia berubah jadi
penghalang. Kenaikan yang KECIL patut dicurigai sebagai tambalan.

Gejala yang menuntun ke sana murni data: panjang 3.043 vs 3.040, dan tujuh celah
1-byte yang SEMUANYA displacement lompatan +3 (75 vs 72, 8b vs 88, 81 vs 7e,
54 vs 51, 4d vs 4a, 9e vs 9b, 16 vs 13) plus satu displacement 16-bit
0x0902 vs 0x08ff. Keseragaman itu berarti SATU sisipan 3 byte, bukan tujuh
kesalahan. Menelusuri di mana offset KITA-ASLI berubah dari +0 ke +3 menunjuk
tepat ke 0x23d4, dan byte mentahnya memperlihatkan DUA `jmp` (`e9 fe f8` +
`e9 fb f8`) di tempat asli cuma punya satu.

⭐ Diff instruksi KASAR mencapai 1.037/1.037 sesudah butir 3 — semua beda
struktural habis — padahal byte masih 79 beda. Jadi diff kasar dan profil celah
saling melengkapi: yang satu menutup BENTUK, yang lain menutup PANJANG.


## `main_` 3.378 -> 3.707 (80,1% -> 87,9%) — dan kenapa ini BELUM tentu benar

Perubahannya satu baris: `page2 = 0x284;` -> `page2 = page + 0x18;`.

Sebabnya PANJANG. Bentuk literal memancarkan simpanan-immediate
`mov [page2],284h` (6 byte); aslinya memuat KEEMPAT konstanta ke ax/bx/cx/dx
lebih dulu (termasuk `0x8004`, argumen `open()`) baru menyimpan semuanya.
Selisih 2 byte itu menggeser SELURUH fungsi. Sesudah diperbaiki, panjang cocok
lagi mulai 0x013b dan 324 celah ikut terjajar — dari situlah +329 datang.

⚠ TAPI KODE LOKALNYA MASIH SALAH, dan ini harus dicatat jujur:
```
KITA 0126 mov [page],bx / add bx,0x18      ASLI 0126 mov cx,0x284
```
Asli memuat DUA literal terpisah (`bx=0x26c`, `cx=0x284`) dan MENUNDA kedua
simpanannya; kita menyimpan `page` lebih awal lalu menghitung. Jadi
`page + 0x18` kemungkinan besar BUKAN bentuk sumber aslinya — ia kebetulan
memberi panjang yang benar. Persis kelas "TAMBALAN" yang baru dicatat dari
`animvm`, cuma kali ini tambalannya besar (+329) karena yang ditambal adalah
geseran global.

Hipotesis untuk bentuk yang BENAR: MS C menaruh konstanta di register hanya
kalau nilainya dipakai LEBIH DARI SEKALI (itu sebabnya `0x140` masuk AX — dua
global memakainya). Untuk `page`/`page2` yang masing-masing dipakai sekali, ia
memilih simpanan-immediate. Perlu dicari apa yang membuat keduanya dianggap
dipakai ulang. Sisa celah di situ: 4 byte @0x0132.

⭐ Karena ini tambalan, UJI ULANG baris ini begitu ada perbaikan lain di `main_`
yang mengubah panjang.

## `pickvar`: bentuk `goto` DIGUGURKAN — `do/while ||` memang benar

Aturan `goto` yang memecahkan `animvm` disapukan ke dua gelung `do/while ||` di
`pickvar` (baris 111..124). Hasilnya GLOBAL **1.654 -> 1.635 (-19)**. Ditolak.
Catatan lama di berkas ("SATU do-while dengan `||`, bukan dua loop bersarang")
tetap berlaku. Contoh lagi pelajaran (b): aturan yang baru saja membayar besar
di satu tempat bisa merugikan di tempat lain.

`pickvar` sisa: 602/653 bentuk cocok (92,2%), panjang -3. Situs utamanya 0x43a5
— asli meng-commit simpanan lebih dulu lalu MEMUAT ULANG register yang sama
(tanda batas blok), dan memancarkan `mov [bp+2],si` (tumpahan 3 byte) yang kita
tidak punya. Itu persis -3 kita.

## Alat baru: `src_c/verify/shapediff.py`

Diff instruksi KASAR dijadikan alat tetap (sudah dua kali membayar). Pasangan
dari `gapprof.py`: gapprof menutup PANJANG, shapediff menutup BENTUK.
Pakai `--stop <addr>` untuk berhenti sebelum tabel data.


## `main_` 3.707 -> 4.169 (87,9% -> 98,8%) — PANJANG SUDAH TEPAT

Dua perbaikan, KEDUANYA pernah DITOLAK sebelumnya. Ini iterasi yang paling
jelas membuktikan pelajaran (c): daftar "dicoba & gagal" KEDALUWARSA.

1. **Satu nol dipindah ke depan `sclo = 0`** — 3.707 -> 3.910 (+203).
   Persis percobaan yang dulu tercatat sebagai GAGAL (3.378 -> 3.270). Yang
   berubah bukan bentuknya melainkan DASARNYA: begitu `page2` diperbaiki,
   panjang fungsi berhenti bergeser, dan bentuk yang benar berhenti terukur
   buruk. Keenam nol tetap memberi hasil byte-identik.

2. **Kurung tutup di 0x0C14 dipindah** (fillans ADA DI DALAM blok) —
   3.910 -> 4.169 (+259). Ini DITOLAK DUA KALI: sekali lewat metrik wilayah
   (291 -> 275) dan sekali lewat GLOBAL (3.378 -> 3.276). Kedua penolakan itu
   diukur saat panjang masih bergeser.

Sesudah keduanya: **panjang KITA = ASLI = 4.219 tepat.** Celah tinggal 50 byte
dalam 25 celah, terbesar 4 B. Geseran offset tinggal DUA ekskursi lokal
(0x0780 -2 pulih di 0x0786; 0x0e0e -2 pulih di 0x0e1a).

⭐ POLA KERJA yang terbukti di sini dan layak jadi urutan baku:
   PANJANG dulu -> lalu UJI ULANG semua penolakan lama -> baru BENTUK lokal.
   Selama panjang masih bergeser, metrik apa pun akan menghukum bentuk yang
   benar dan memberi hadiah pada bentuk yang kebetulan menambal geseran.

## `page2 = page + 0x18` BUKAN tambalan — diuji ulang dan bertahan

Iterasi lalu ini dicatat sebagai kemungkinan tambalan (angkanya naik, kodenya
belum cocok). Diuji ulang sesudah panjang fungsi lurus: bentuk literal
`page2 = 0x284;` memberi **3.305**, bentuk `page + 0x18` memberi **4.169**.
Jadi bentuk ini benar; yang tersisa cuma 4 byte LOKAL @0x0132
(asli `mov cx,284h`, kita `mov [page],bx / add bx,18h`).

⭐ Pelajaran tambahan: kecurigaan "ini cuma tambalan" HARUS diuji, bukan
diasumsikan — sama seperti kecurigaan sebaliknya. Dua kali kecurigaan diuji
iterasi ini, satu terbukti (animvm `default:`) dan satu terbantah (ini).


## `main_` 4.169 -> 4.175 (99,0%) — dua ekskursi offset terakhir hilang

Panjang tetap TEPAT 4.219 dan kini **tidak ada geseran offset sama sekali**.
Celah tinggal 44 byte dalam 22 celah, terbesar 4 B.

Kedua ekskursi -2 yang tersisa (0x0780 dan 0x0e0e) ternyata GEJALA YANG SAMA,
dan cocok digarap berpasangan (pelajaran g):

```
ASLI  xor ax,ax  lalu  mov [p1],1        KITA  mov [p1],1  lalu  xor ax,ax
```

Nolnya bukan cuma satu penugasan — ia dipakai BERKALI-KALI: di 0x0e0c untuk
`goal`, `pass`, DAN dua argumen `f171f`; di 0x077e untuk `slot` DAN argumen
`loadarc`. Karena dipakai lebih dari sekali ia masuk register (aturan 6), dan
asli memancarkan `xor ax,ax` di PUNCAK blok. Memindah SATU penugasan nol ke
depan `p1 = 1` memulihkan urutannya: +4 lalu +2.

⚠ Situs KETIGA dengan bentuk yang mirip (baris 737, `f171f` lalu `p1 = 1` lalu
`pass = 0`) DITOLAK: memindah `pass = 0` ke depan memberi 4.175 -> 4.169.
Urutan di sana memang sudah benar. Tiga situs, bentuk sumber nyaris identik,
dua perlu dipindah dan satu tidak — pelajaran (b) lagi.

Sisa `main_` (22 celah): 0x0132=4B (asli `mov cx,284h`), 0x0a36=4B, 0x0bfe=4B,
0x0e01=4B, 0x0256=3B, 0x04e2=3B, sisanya <= 2 B. Semuanya BENTUK lokal;
tidak ada lagi masalah panjang untuk disingkirkan lebih dulu.


## `main_` 4.175 -> 4.189 (99,3%) lewat TIGA pembalikan arah syarat

Celah tinggal 30 byte dalam 17 celah, terbesar 4 B.

Ketiganya gejala yang SAMA dan digarap berpasangan (pelajaran g): `jcc` diikuti
DUA `jmp` berurutan, sasarannya sama tapi urutannya TERBALIK dari asli.
Aturannya dicatat di README.

* baris 636 (`endcase2`) `!= -1` -> `== -1` + badan ditukar : +5
* baris 703 (`endcase3`) `!= -1` -> `== -1` + badan ditukar : +4
* baris 587 (`case 1`)   `== -1` -> `!= -1` + badan ditukar : +5

⚠ Perhatikan arahnya BERLAWANAN di situs ketiga. Bentuk sumbernya nyaris
identik dengan dua yang lain, tapi jawabannya kebalikan — kesekian kalinya
kemiripan bentuk sumber terbukti bukan bukti.

## `pickvar`: urutan pernyataan DIGUGURKAN (tiga permutasi)

Dasar 1.654/1.730. Empat penugasan sebelum `if (idx + 1 < n)` (`k2`, `k`, `q`,
`sel`) dipermutasi: `q,sel,k2,k` -> 1.584; `sel,q,k2,k` -> 1.579;
`k2,k,sel,q` -> 1.649. Semua LEBIH BURUK.

Jadi -3 byte di `pickvar` bukan soal urutan pernyataan. Yang dicari tetap
apa yang membuat asli MENUMPAHKAN `si` ke `[bp+2]` di 0x43b5 (3 byte) dan
memakai DI alih-alih SI sesudahnya — tanda `&list[idx]` masih HIDUP di sana.
Kita menghitung ulang, jadi tidak perlu menumpahkan.


## `main_` 4.189 -> 4.199 (99,5%); sapuan arah-syarat TUNTAS

Celah tinggal **20 byte dalam 13 celah**, dan 10 di antaranya menumpuk di satu
situs (0x0126..0x0138, blok `page`/`page2`).

**Sapuan aturan pembalikan arah syarat: BERSIH.** Dua pemindai dijalankan atas
kelima fungsi sisa — satu untuk pola ketat (`jcc` + dua `jmp` bertukar), satu
untuk pola longgar (SEMUA `jcc` yang mnemonic-nya terbalik dari asli). Keduanya
melaporkan NOL di `pickvar`, `loadcon`, `place`, `f498c`, dan `main_`. Aturan
itu sudah habis dipakai; jangan disapukan lagi.

**Dua situs baru diperbaiki** lewat perluasan aturan hoisting konstanta (yang
sebelumnya cuma dirumuskan untuk NOL):
```
0x0256  ASLI mov ax,1 / mov [sub],80h    KITA mov [sub],80h / mov ax,1
0x04e2  ASLI mov ax,1 / mov [sub],7      KITA mov [sub],7   / mov ax,1
```
Nilai `1` dipakai dua kali (`goal`+`lvl`, dan `lvl3`+`lvl2`), jadi ia masuk
register dan dimaterialisasi di puncak blok. Memindah `sub = ...` ke BELAKANG
kedua penugasan `1` memberi +5 masing-masing. Aturannya diperluas di README:
berlaku untuk konstanta APA PUN, bukan cuma nol.

**Uji ulang `page2` (aturan kedaluwarsa):** di dasar 4.199, bentuk literal
`page2 = 0x284;` memberi 3.329 dan `page = page2 - 0x18;` memberi 3.318. Bentuk
`page + 0x18` bertahan untuk KEDUA kalinya. Sisa 10 byte di situs itu adalah
soal LOKAL: asli menahan `0x26c` di BX dan `0x284` di CX dengan KEDUA simpanan
ditunda; kita menyimpan `page` lebih awal lalu menghitung. Belum ketemu bentuk
sumber yang memberi dua literal terpisah ke register.


## `main_` 4.199 -> 4.201 (99,6%); DUA sapuan pola lagi TUNTAS

Celah tinggal **18 byte dalam 12 celah**.

**Sapuan aturan HOISTING KONSTANTA: BERSIH.** Pemindai mencari tempat di mana
ASLI memancarkan `mov reg,imm` sementara KITA memancarkan `mov [glob],imm` di
alamat yang sama. Hasilnya NOL di `pickvar`, `loadcon`, `place`, `f498c`, dan
`main_`. Bersama sapuan arah-syarat iterasi lalu, DUA aturan besar kini habis
sasarannya — sisa pekerjaan tidak bisa lagi ditemukan lewat pemindaian pola
yang sudah dikenal.

**Satu perbaikan:** `f171f(mode, 0x8ca, ...)` -> `f171f(2, ...)` di baris 777.
Asli memancarkan `mov bx,2 / push bx`, kita `push [mode]`. +2.

⚠ JEBAKAN yang hampir lolos: pola `f171f(mode, 0x8ca, cur + 1, nmax, postab)`
muncul DUA kali (baris 750 dan 777) dan `replace()` mengenai yang PERTAMA.
Hasilnya TURUN (4.199 -> 4.195), yang sempat terbaca sebagai "hipotesisnya
salah". Ternyata cuma salah sasaran; yang kedua memberi +2. ⭐ Kalau sebuah
anchor muncul lebih dari sekali, PILIH BARISNYA — jangan `replace()` buta.

**Situs 0x0b40 dibedah dan DIPARKIR:** ours `jmp 0x450` (restart) vs asli
`jmp 0xbf6` (uji ekor `endcase2`). Ukuran instruksinya SAMA; yang beda cuma
SASARAN. Sebabnya peruntuhan rantai lompatan: kita meruntuhkan `goto endcase2`
menjadi lompatan langsung ke `restart`, asli tidak. Tidak ada pengungkit sumber
yang jelas untuk melarang peruntuhan itu.

Sisa `main_` (18 byte): gugusan 8 byte di 0x0126..0x0138 (blok `page`/`page2`),
0x0b41=2B (rantai lompatan di atas), dan enam celah 1-byte.


## `probeA`: waktu simpanan TERJAWAB — dan jawabannya menutup satu jalur penuh

Sasaran "apa yang menentukan WAKTU SIMPANAN ke memori" akhirnya diuji dengan
probe terkendali alih-alih ditebak. Lima varian sumber dari bentuk yang sama
(`src_c/probes/probeA.c`), dikompilasi sekali, dibandingkan disassembly-nya.

Empat dari lima memancarkan simpanan yang DITUNDA. Yang membedakan cuma satu:
kalau UJI memakai variabel yang baru dihitung (`if (q + 1 < n)` alih-alih
`if (idx + 1 < n)`), kompiler menyimpan SEGERA lalu memakai ulang registernya.

Jadi simpanan-segera BUKAN pilihan bentuk sumber melainkan gejala kebutuhan
register. Aturannya dicatat di README.

⭐ NILAI TEMUAN INI ADA DI APA YANG DITUTUPNYA. Selama beberapa iterasi, empat
situs terakhir digarap dengan asumsi "ada bentuk sumber yang benar dan belum
ketemu". Probe membuktikan asumsi itu SALAH: untuk bentuk ini bawaan kompiler
memang menunda, dan bentuk sumber apa pun tidak mengubahnya. Itu menjelaskan
sekaligus kenapa tiga permutasi `pickvar`, sepuluh varian `loadcon`
(probe11..13), dan beberapa varian `nvar` semuanya gagal — semuanya menyerang
faktor yang tidak berpengaruh.

Pengungkit yang tersisa untuk keempat situs bukan bentuk pernyataan melainkan
TEKANAN REGISTER: membuat nilai lain tetap hidup melintasi blok itu. Di
`pickvar` yang hidup di asli adalah `&list[idx]` (SI, lalu ditumpahkan ke
`[bp+2]` — persis 3 byte yang kita kurang).

⚠ CATATAN OPERASIONAL: `link.ps1` menautkan SEMUA `.OBJ` di `out/`, jadi probe
WAJIB dihapus `.OBJ`-nya dan sumbernya dipindah ke `probes/` sesudah dipakai.


## `pickvar`: sudut TEKANAN REGISTER diuji dan TERBANTAH

Sesudah `probeA` menutup jalur "bentuk sumber", sudut yang tersisa adalah
membuat `&list[idx]` tetap HIDUP melintasi blok — meniru asli yang menahannya
di SI lalu menumpahkannya ke `[bp+2]` (3 byte yang kita kurang).

Diuji dengan mengubah pengganjal `char f1[2]` (slot 0x14, tak terpakai) menjadi
`int *lp`, lalu memakai `lp` untuk `list[idx]`, `lp[1]` dua kali:

```
GLOBAL 1.654 -> 1.557 (-97)      panjang -3 -> -10
```

⚠ Pengukurannya SAH: bingkai tetap `sub sp=0x52`, jadi hasil buruk itu BUKAN
efek samping bingkai yang berubah. Menahan penunjuk di lokal justru membuat
kompiler memancarkan LEBIH SEDIKIT kode (panjang makin jauh dari asli), yaitu
arah yang BERLAWANAN dengan yang dicari. Hipotesis terbantah.

⭐ KOREKSI ATURAN BINGKAI: `char f1[2]` di posisi ini TERNYATA MENEMPATI SLOT —
menggantinya dengan `int *` menjaga bingkai tetap 0x52. Catatan lama
"`char x[2]` DIBUANG" karena itu TIDAK berlaku umum; ia bergantung posisi/konteks.
Jangan memakai catatan itu untuk memperkirakan ukuran bingkai tanpa mengukur.

Sisa jalan untuk `pickvar` -3 byte: belum ada. Yang sudah gugur di situs ini:
tiga permutasi urutan pernyataan, bentuk `goto`, `&&` baris 207, dan kini
penunjuk-lokal. `probeA` sudah membuktikan bentuk sumber bukan pengungkitnya.


## ✅ `f498c` SELESAI byte-per-byte — 162/165 -> 165/165 (2026-07-31)

Fungsi ke-78. `verifyall`: COCOK 78/81, 18.851 byte. Kode C game 71,9% ->
**72,5%**; TOTAL 76,8% -> **77,3%**.

Perubahannya: penjaga `if (sel[i] < 0) continue;` + `continue` kedua diganti
penjaga POSITIF bersarang dengan `if/else`. Aturannya di README.

⭐ NILAINYA MELEBIHI 3 BYTE ITU. Ini **pengungkit pertama yang terbukti untuk
kelas "beda register murni"** — kelas yang selama belasan iterasi dianggap tak
terkendali dan berkali-kali saya sebut "murni pilihan register, tidak ada
pengungkit". Ternyata ada: BENTUK PENJAGA menentukan pilihan alokator.

Ini juga mengoreksi cara saya menutup kasus. Beberapa kali saya menulis "sisanya
MURNI pilihan register" seolah itu vonis akhir. Yang benar: itu deskripsi
GEJALA, bukan sebab — dan gejala yang sama ternyata punya pengungkit sumber.

⚠ Disapukan ke `place` (satu-satunya fungsi sisa dengan bentuk serupa) dan
DITOLAK: `while (j < n) { i = flag[j]; if (i < 0) break; ... }` diubah jadi
`while (j < n && (i = flag[j]) >= 0)` memberi 501 -> 473. Per-tempat lagi.


## Sapuan pengungkit BENTUK PENJAGA: sasarannya ternyata cuma satu

Aturan yang menyelesaikan `f498c` langsung disapukan. Hasilnya menutup
harapan bahwa ia akan membayar berkali-kali:

* `pickvar` dan `loadcon` TIDAK PUNYA `continue` sama sekali — pengungkit ini
  tidak bisa diterapkan di sana. (Diperiksa dengan grep, bukan diasumsikan.)
* `main_` punya enam `continue`, tapi tak satu pun bertepatan dengan celah.
* `place`: bentuk setara sudah ditolak (-28).

Jadi `f498c` adalah satu-satunya tempat pengungkit ini berlaku. Itu tetap
berharga — ia MENGOREKSI vonis "murni pilihan register" — tapi jangan berharap
ia menutup situs lain.

## `main_`: tiga situs sisa dibedah, tiga hasil negatif

Dasar 4.201/4.219. Semua diukur, semua ditolak atau tanpa efek:

1. **0x05f1/0x05f9 — dua `cmp` TERTUKAR** (kita uji 3 lalu 2, asli 2 lalu 3).
   Sumbernya `switch (mode) { case 3: ... case 2: ... }` di baris 414.
   Menukar urutan `case` memberi **4.201 -> 4.199**. DITOLAK — komentar lama
   ("badan 0x566 = case 3 lebih dulu, jadi case 3 duluan") ternyata BENAR.
   Rantai perbandingan dipancarkan SESUDAH badan dan urutannya TIDAK mengikuti
   urutan `case` di sumber; belum ketemu apa yang menentukannya.

2. **0x0c83 — `mov bx,[recbase]` vs `mov si,...`**, persis kelas `f498c`
   (SI mati lalu dipakai ulang oleh asli, kita ambil BX). Gelungnya
   `for (j = 0; j < cnt2; j++) { if (...) break; }` di baris 667.
   Memindahkan syarat ke dalam `for` memberi angka IDENTIK (4.201) — tidak
   berpengaruh sama sekali.

3. **0x0b41 dan 0x0e01 — sasaran `jmp` berbeda** (0x450 vs 0xbf6; 0xd31 vs
   0xd15). Ukuran instruksi SAMA; kita meruntuhkan rantai lompatan, asli tidak.
   Tetap DIPARKIR — belum ada pengungkit sumber untuk melarang peruntuhan.

⭐ Yang layak dicatat dari nomor 1: ini kelas beda BARU yang belum pernah
dirumuskan — **urutan rantai perbandingan `switch` bisa berbeda dari urutan
`case` di sumber**, dan keduanya tidak bergerak bersama. Kalau nanti ada
pemahaman soal itu, ia menutup 2 byte di sini.


## `probeB`: rantai perbandingan `switch` = KEBALIKAN urutan `case` (main_ +2)

Kelas beda yang iterasi lalu baru teridentifikasi, kini TERJAWAB — lagi-lagi
lewat probe, bukan tebakan. Lima varian, satu kompilasi, urutan `cmp` dibaca
langsung. Aturannya di README.

Yang membuat ini tidak sepele: aturan LAMA "urutan `case` = urutan ALAMAT BADAN"
juga benar, dan keduanya BERGERAK BERLAWANAN. Karena itu menukar urutan case
yang punya badan masing-masing memperbaiki satu hal sambil merusak yang lain —
persis yang terukur iterasi lalu (4.201 -> 4.199, ditolak).

Yang bisa diperbaiki cuma kelompok label yang BERBAGI badan, karena di situ
urutan label tidak memengaruhi tata letak. `main_` baris 403 (`case 2: case 3:`
-> `case 3: case 2:`) memberi 4.201 -> **4.203**. Kandidat kedua (baris 354,
`case 2: case 3: case 4:`) diuji juga: TIDAK berubah.

Celah `main_` tinggal **16 byte dalam 10 celah**.

⭐ Ini kali KETIGA probe terkendali menjawab pertanyaan yang tebakan berulang
gagal jawab (probeA waktu-simpanan, bentuk penjaga f498c, probeB urutan rantai).
Polanya konsisten: begitu sebuah pertanyaan bisa dirumuskan sebagai "faktor apa
yang membedakan?", probe menjawabnya dalam SATU kompilasi.

CLAUDE.md ikut disegarkan ke 78/81 / 18.851 / 77,3%.


## `main_` 0x0b39: pemetaan ke sumber AMBIGU — dicatat supaya tidak diulang

Situs ini dua kali disebut "rantai lompatan yang kita runtuhkan". Dibedah lebih
teliti, dan kesimpulan itu BELUM TENTU benar — pemetaannya ke sumber tidak
konvergen. Rinciannya dicatat supaya iterasi berikutnya tidak mengulang analisis
yang sama dari nol.

Yang TERUKUR di biner:
```
0x0b39  cmp word ptr [cursel], -1
0x0b3e  jne 0x0b43          <- 0x0b43 = `again2` (badan f498c, terverifikasi
                               dari urutan push: e80, e58, recC, nzany, ytop)
0x0b40  KITA jmp 0x0450     ASLI jmp 0x0bf6
        0x0450 = `restart`   0x0bf6 = ekor `endcase2` (yang MENGUJI ULANG cursel)
```

Kenapa ambigu: kode itu duduk TEPAT sebelum `again2:` (baris 616), tapi sumber
di baris 601..615 (`case 2:` sampai `again2:`) TIDAK punya uji `cursel` sama
sekali. Kandidat lain — ekor `case 4` (baris 598, `if (cursel != -1) goto reset;
continue;`) — juga tidak cocok: sasaran `jne`-nya seharusnya `reset` (0x0668),
bukan `again2` (0x0b43).

Jadi salah satu dari ini benar dan belum bisa dipilih tanpa bukti tambahan:
* sumber kita memang `goto restart` di tempat yang aslinya `goto endcase2`
  (dua-duanya berakhir di `restart`, jadi SETARA secara semantik), atau
* MS C meruntuhkan `goto endcase2` kita menjadi lompatan langsung ke `restart`
  sementara asli tidak.

⭐ LANGKAH BERIKUTNYA YANG BENAR: jangan menebak bentuk sumbernya. Tentukan dulu
BLOK SUMBER MANA yang memancarkan 0x0b39 — mis. dengan menyisipkan penanda unik
(sebuah pemanggilan yang gampang dikenali) di kandidat blok, kompilasi, dan lihat
di alamat mana ia mendarat. Baru sesudah itu bentuknya layak diutak-atik.

⚠ Selama pemetaannya belum pasti, `main_` 0x0b41 dan 0x0e01 TETAP DIPARKIR.
Keduanya 2 byte dan 1 byte; tidak sebanding dengan risiko menebak.


## `main_` 0x0b39 TERPECAHKAN lewat PEMETAAN PENANDA — 4.203 -> 4.205 (99,7%)

Situs yang iterasi lalu dicatat "pemetaannya ambigu, jangan ditebak". Teknik
penanda dipakai persis seperti yang direncanakan, dan langsung menjawab.

Penanda `f2fde();` disisipkan tepat sebelum `again2:`, lalu `.OBJ`-nya di-diff
terhadap build dasar. difflib melaporkan `insert` di **0x0ab2** — jadi `again2`
ada di 0x0ab2, BUKAN di 0x0b43 seperti dugaan dua iterasi terakhir. Dengan itu
`cmp` di 0x0b3c jelas milik `if (cursel == -1) goto endcase2;` (baris 626),
jauh di bawah `again2`.

⚠ Percobaan pertama mencari penandanya dengan memindai pola `call` di
disassembly GAGAL — terlalu banyak kandidat. Yang bekerja: DIFF terhadap build
dasar. Dicatat di README.

Perbaikannya lalu jelas: asli melompat ke UJI EKOR, bukan ke `endcase2` yang
badannya cuma `break` (dan karenanya diruntuhkan MS C jadi lompatan langsung ke
`restart`). Diberi label `tail2:` pada uji ekor dan `goto tail2` — +2.

Padanannya di `case 3` DITOLAK (4.205 -> 4.204): strukturnya beda, ujinya
SESUDAH `endcase3:`. Per-tempat lagi.

Celah `main_` tinggal **14 byte dalam 9 celah**, dan yang tersisa: gugusan 8 B
di 0x0126 (`page`/`page2`, dua alternatif sudah gugur di dua dasar), tiga celah
1-byte di 0x0c84/88/8a (BX vs SI), dan 0x0e01.


## `main_` 0x0c84 dipetakan PASTI; dua bentuk operan gugur

Teknik penanda dipakai lagi, kali ini sebagai LANGKAH PERTAMA (bukan sesudah
tersesat). Penanda disisipkan sebelum `for (j = 0; j < cnt2; j++)` dan mendarat
di **0x0c62** — jadi gelung di 0x0c68..0x0c98 memang blok itu. Pemetaan PASTI
sebelum satu pun hipotesis dicoba.

Dua bentuk operan diuji pada `(buf6f22[j] * 0xc + (char *)recbase)[1]`:
```
(0xc * buf6f22[j] + (char *)recbase)[1]   -> 4.205  IDENTIK (tak berpengaruh)
((char *)recbase + buf6f22[j] * 0xc)[1]   -> 4.200  LEBIH BURUK
```
Jadi urutan operan BUKAN pengungkit BX-vs-SI di situs ini. Ini melengkapi
daftar: bentuk penjaga (ditolak di `place`), syarat-dalam-`for` (identik), dan
kini urutan operan — ketiganya gugur untuk kelas BX-vs-SI di `main_`.

⚠ CATATAN PROSES — BUG HARNESS YANG TERULANG. Sapuan pertama melaporkan "GAGAL
KOMPILASI" untuk KEDUA varian. Sebabnya sama persis dengan kejadian di `loadcon`
beberapa iterasi lalu: fungsi shell dipanggil `V x '<pengganti>'` sehingga
`sys.argv[2]` berisi `"x"`, bukan penggantinya. Sudah dicatat sebagai jebakan,
tapi TETAP TERULANG karena harness-nya ditulis ulang dari nol tiap kali.
⭐ Perbaikannya: tulis skrip pengganti sebagai BERKAS di scratchpad
(`mrep.py`) dengan argumen eksplisit, lalu panggil berkas itu — jangan menaruh
heredoc di dalam fungsi shell yang argumennya diteruskan berlapis.


## `probeC`: kelas BX-vs-SI TIDAK bisa dijawab probe — batas teknik ditemukan

Sesuai disiplin (situs gagal 3x -> berhenti menebak, bikin probe), kelas
BX-vs-SI diprobe dengan lima varian. HASILNYA SERAGAM: kelimanya memakai BX.
Rinciannya di README.

Ini hasil negatif yang PALING informatif dari beberapa iterasi terakhir, karena
ia menutup teknik-nya, bukan cuma satu hipotesis:
* bentuk sumber lokal TIDAK menentukan pilihan BX vs SI di situs ini;
* probe kecil TIDAK bisa mereproduksi keadaan alokator se-fungsi;
* jadi `main_` 0x0c83 dan `place` 0x4fd4 tidak akan terpecahkan dengan alat yang
  ada sekarang.

⭐ ATURAN PROSES BARU: kalau SEMUA varian probe memberi jawaban SAMA, itu tanda
pertanyaannya SALAH TINGKAT. Naikkan cakupan pertanyaannya — jangan menambah
varian di tingkat yang sama.

⭐ HARNESS akhirnya disimpan sebagai berkas tetap (`rep.py` di scratchpad,
argumen lewat BERKAS, ber-assert anchor unik). Bug argumen berlapis yang sudah
dua kali menggigit tidak akan terulang lagi.

## Keadaan pekerjaan: 71 byte tersisa, semuanya kelas tersulit

Sesudah iterasi ini, sisa yang belum byte-exact:
```
main_    14 byte / 9 celah   (99,7%)
pickvar   3 byte  (-3 panjang)
loadcon  52 byte
place     2 byte
```
Semuanya kelas alokasi register, dan untuk `main_` 0x0c83 + `place` baru saja
TERBUKTI di luar jangkauan alat yang ada. `pickvar` sudah gagal EMPAT kali,
`loadcon` sudah menggugurkan 13 varian. Kemajuan per iterasi kini 0-2 byte.


## PENUTUPAN CAKUPAN: ~57 dari 71 byte sisa ada di kelas yang TERBUKTI di luar
## jangkauan alat sekarang

`loadcon` dipetakan lewat penanda (mendarat 0x5101, jadi situs 0x5115 memang di
dalam gelung `do` seperti dicatat — pemetaan lama BENAR kali ini). Lalu celahnya
diukur ulang:

```
52 byte / 41 celah, SELURUHNYA terkurung di 0x5107..0x5298
sebelum 0x5115: cuma 1 byte (displacement lompatan ke dalamnya)
sesudah 0x5298: TIDAK ADA
```

Jadi klaim lama di berkas — "seluruh sisa adalah SATU kaskade dari satu
keputusan register" — TERBUKTI dengan pengukuran, bukan cuma dugaan. Dan
keputusan itu (`mov bx,[lastgoal]` vs asli `mov ax`) persis kelas yang `probeC`
baru saja buktikan TIDAK bisa dijawab dari bentuk sumber.

⭐ AKIBATNYA, PETA SISA PEKERJAAN JADI JELAS:
```
KELAS "DI LUAR JANGKAUAN ALAT SEKARANG" (pilihan register se-fungsi)
  loadcon  52 byte  (kaskade dari 0x5115)
  main_     3 byte  (0x0c84/88/8a, BX vs SI — probeC seragam)
  place     2 byte  (0x4fd4, SI vs DI)
  pickvar   3 byte  (0x43b5, tumpahan — gagal 4x, sekelas)
  = 60 byte
KELAS LAIN (masih mungkin)
  main_    ~11 byte (gugusan 8 B di 0x0126 = penundaan simpanan; sisanya kecil)
```

Ini BUKAN vonis "tidak bisa selesai" — ini pengakuan bahwa alat yang ada
(pemetaan penanda, probe terkendali, pemindai pola, metrik GLOBAL) sudah
mencapai batasnya untuk kelas itu. Yang dibutuhkan: pemahaman tentang bagaimana
MS C 1.04 mewariskan keadaan alokator antar-blok dalam satu fungsi. Itu
pekerjaan tersendiri, bukan iterasi tambahan dengan alat yang sama.

⚠ Konsekuensi praktis: `loadcon` TIDAK LAGI sasaran paling menjanjikan meski
byte-nya paling banyak. Sasaran yang tersisa dengan peluang nyata cuma ~11 byte
di `main_`.


## `main_` 4.205 -> 4.215 (99,9%) — literal 0x26c/0x284 ternyata SIMBOL

Sasaran iterasi ini adalah gugusan 8 byte di 0x0126, satu-satunya blok >2 byte
yang belum terbukti buntu. Ternyata bukan soal penundaan simpanan sama sekali:
0x26c dan 0x284 adalah `pbufA`/`pbufB`, simbol DGROUP yang sudah dideklarasikan
di `drawball.c`. Diganti jadi `(int)pbufA` / `(int)pbufB` -> **+10**.

Celah `main_` kini **4 byte dalam 4 celah**, semuanya 1-byte:
0x0c84, 0x0c88, 0x0c8a (kelas BX-vs-SI yang sudah DIPARKIR) dan 0x0e01.
Artinya `main_` praktis selesai: yang tersisa cuma kelas yang terbukti di luar
jangkauan alat, plus satu byte di 0x0e01.

⭐ PELAJARAN TERPENTING: `page2 = page + 0x18` bertahan DUA kali uji-ulang dan
sempat saya sebut "BUKAN tambalan" dengan yakin — karena panjangnya memang
benar. Yang membongkarnya bukan pengukuran ke sekian, melainkan pertanyaan yang
belum pernah diajukan: "apakah angka ini simbol?" Pengukuran memverifikasi
hipotesis yang ADA; ia tidak memunculkan hipotesis yang belum terpikir.

## Sapuan "literal yang sebenarnya simbol": tidak ada kandidat lain

Pemindai dibuat (kumpulkan semua `@0xNNN` dari deklarasi `extern` di seluruh
`src_c/src/`, lalu cari literal heksa 3-4 digit di baris KODE) dan dijalankan
atas `loadcon`, `pickvar`, `place`, `main_`, `f498c`, `nvar`, `animvm`.
Hasilnya: tidak ada kandidat yang bisa ditindaklanjuti — sisa temuannya semua
teks komentar, dan dua literal argumen `load()` di `main_` (0x526 `hdrspr`,
0x646 `hintspr`) tidak berada di celah mana pun, jadi byte-nya memang sudah
cocok.

Peta sisa DIPERBARUI: dari 71 byte tinggal **61 byte**, dan 60 di antaranya
kelas yang terbukti buntu. Yang berpeluang tinggal 1 byte (`main_` 0x0e01).


## `main_` 4.215 -> 4.216: label `again3` terlalu belakang — dan SISA PROYEK
## kini SELURUHNYA di kelas yang diparkir

Celah terakhir `main_` yang bukan kelas-buntu: 0x0e01, ekor `endcase3`.
```
0x0dfe je 0x0e03        (cursel == -1 -> restart)
0x0e00 KITA jmp 0x0d31   ASLI jmp 0x0d15   <- 28 byte lebih AWAL
```
Selisih 28 byte itu persis panjang panggilan `drawslot(ytop, nmechc, recB, ed0,
ef8)`. Jadi label `again3:` kita ditaruh SESUDAH `drawslot`, padahal asli
menaruhnya SEBELUM — artinya `drawslot` ikut diulang tiap iterasi gelung.
Dipindah -> +1.

⭐ Cara menemukannya layak dicatat: SELISIH SASARAN LOMPATAN ITU UKURAN. 0x0d31
- 0x0d15 = 28, dan tinggal mencari pernyataan yang panjangnya 28 byte tepat
sebelum label. Tidak perlu menebak bentuk sama sekali.

**KEADAAN AKHIR — semua sisa ada di satu kelas:**
```
main_    3 B  0x0c84/88/8a  BX vs SI   [DIPARKIR — probeC seragam]
loadcon 52 B  kaskade 0x5115 BX vs AX  [DIPARKIR]
pickvar  3 B  0x43b5 tumpahan          [DIPARKIR — gagal 4x]
place    2 B  0x4fd4 SI vs DI          [DIPARKIR]
       = 60 B, SEMUANYA kelas alokasi register se-fungsi
```
Tidak ada lagi sasaran di luar kelas itu. Jalur ini mencapai batas alat yang
tersedia: `probeC` sudah membuktikan bentuk sumber lokal TIDAK menentukan
pilihan register di situs-situs itu, dan probe kecil tidak bisa mereproduksi
keadaan alokator se-fungsi.

Untuk melanjutkan dibutuhkan hal yang BUKAN iterasi tambahan: pemahaman
bagaimana MS C 1.04 mewariskan keadaan alokator antar-blok dalam satu fungsi
(mis. dengan membaca kode generator MS C 1.04 sendiri, atau menyusun model
alokatornya dari eksperimen sistematis berskala jauh lebih besar).


## TIGA TEMUAN BESAR DI TINGKAT .EXE (2026-07-31 sore)

Sesi ini beralih dari "byte per fungsi" ke "apakah .EXE-nya benar", dan langsung
menemukan tiga hal yang selama ini tidak terlihat karena tidak pernah diukur.

### 1. `main_` TIDAK ADA DI MANIFEST — 4.219 byte tidak pernah dihitung
`verifyall` membaca `manifest.txt`, dan `main_` tidak tercantum di sana. Jadi
angka "78/81 fungsi, 18.851 byte" selama berminggu-minggu MENGABAIKAN fungsi
terbesar kedua. Ditambahkan -> laporan jadi 78/82 dan `main_` muncul apa adanya
("3 byte beda"). ⭐ Pelajaran: alat verifikasi hanya melihat apa yang didaftarkan
kepadanya. Periksa CAKUPAN alat, bukan cuma keluarannya.

### 2. PEMBAGI PERSENTASE salah DUA KALI
* `~26.000` memuat 1.207 byte NOL di 0x5F93 yang bukan kode -> KODE NYATA 25.758.
* `total_target = 26000 + 1200 + data` MENGHITUNG GANDA: modul assembly (blit,
  snd1, prep, text, ...) semuanya sudah ada di manifest dan ikut `ok_bytes`;
  menambah "+1.200 assembly" menghitungnya dua kali — dan +1.200 itu sendiri
  keliru karena wilayah itu NOL.
Sesudah dikoreksi: TOTAL 77,3% -> **79,9%** (bukan turun; angka lama yang salah).

### 3. `drawtab` dan `setsel` ADALAH FUNGSI YANG SAMA — 177 byte dihitung ganda
Keduanya terdaftar di 0x3769 ukuran 177, dan keduanya "COCOK". Byte-nya berbeda
HANYA di slot relokasi (rujukan simbol), jadi kode mesinnya identik. `drawtab`
(29 Jul, 1 pemanggil) adalah rekonstruksi lama dari fungsi yang sama dengan
`setsel` (30 Jul, 12 pemanggil). Akibatnya fungsi itu di-LINK DUA KALI.
Disatukan ke `setsel`; `askopts` diarahkan ulang; `drawtab.c` dipindah ke
`probes/drawtab_DUPLIKAT.c`.
⚠ Aturan lama "SATU NAMA jangan untuk DUA alamat" ternyata punya CERMIN yang
sama berbahayanya: **DUA NAMA untuk SATU alamat**. Yang pertama bikin simbol
salah tunjuk; yang kedua bikin kode terduplikasi di .EXE dan angka menggelembung.

### 4. URUTAN LINK SALAH — abjad, bukan alamat
`link.ps1` memakai `Sort-Object BaseName`. LINK menempatkan modul sesuai urutan
pemberian, jadi .EXE kita isinya benar tapi TATA LETAKNYA acak. Diukur:
```
sebelum perbaikan   : 6,7% byte cocok per posisi, emulator LANGSUNG KELUAR
urut alamat         : 34,1%
+ duplikat dibuang  : 43,0%
```
Sesudahnya geseran offset tinggal **±8 byte sampai 0x6449** — dan ±8 itu persis
defisit per-fungsi yang sudah dikenal (place -2, pickvar -3, loadcon dst.).

### 5. SISA TERBESAR DI TINGKAT .EXE: 1.207 byte NOL yang tidak kita hasilkan
Di 0x06449 offset melompat -1.215: wilayah 0x5F93..0x6442 (1.207 byte NOL) ada
di biner asli tapi TIDAK ADA di build kita. Manifest lompat dari `setup`
(0x5f90, 3 B) langsung ke `text` (0x644a). Jadi ada satu "modul" sepanjang
1.207 byte nol yang belum diketahui asalnya — kemungkinan penyangga tak
terinisialisasi di modul assembly, atau padding LINK.
⭐ INI SASARAN BARU YANG BUKAN KELAS ALOKATOR. Ia tidak butuh pemahaman
alokator sama sekali, cuma perlu tahu modul apa yang menempati wilayah itu.

### Butir yang TIDAK dikerjakan, dengan alasan
Sudut "ubah keadaan alokator dari HULU" untuk 3 byte `main_` 0x0c83:
blok tepat sebelumnya berakhir dengan panggilan `nvar()`, yang mengosongkan
semua register. Jadi pilihan register di situ memang dibuat dari keadaan
BERSIH — persis kondisi yang sudah diuji `probeC` (lima varian, semuanya BX).
Mengubahnya berarti merestrukturisasi kode yang sudah cocok byte-per-byte,
mempertaruhkan 4.216 byte demi 3. Tidak sepadan; tetap DIPARKIR.


## SASARAN BARU DIKERJAKAN: lubang 1.207 byte DITUTUP, .EXE dari 6,7% -> 95,9%

### Apa yang mengisi 0x5F93..0x6449
Dipindai byte-per-byte atas seluruh `E8` (near call) di 0x0082..0x9062:
**TIDAK ADA satu pun `call` yang menunjuk ke dalam 0x5F93..0x6442.** Wilayah itu
1.200 byte NOL murni — bukan kode. Tepat sesudahnya, 0x6443..0x6449, ada tujuh
byte yang juga tak pernah dipanggil: `mov al,4 / mov ah,0 / int 10h / ret`
(set mode CGA 4).

Dibuat `src_c/asm/mode4.asm` = 1.200 byte nol + proc 7 byte, didaftarkan
`mode4 5f93 1207`. **COCOK byte-per-byte.**

Akibatnya pada angka: kode game 72,5% -> **77,2%**, TOTAL 79,9% -> **83,4%**.
Ini bukan perbaikan kosmetik — 1.207 byte itu memang bagian biner yang selama
ini tidak pernah dihasilkan build kita.

### Kualitas .EXE secara keseluruhan
```
GLOBAL seluruh muatan .EXE : 44.602 / 46.532  = 95,9%
   kode game (<0x69d7)     : 25.402 / 26.965  = 94,2%
   MC.LIB                  :  9.520 /  9.867  = 96,5%
   DGROUP + ekor           :  9.570 /  9.570  = 100,0%
```
Geseran offset di wilayah kode game tinggal **±8 byte sampai 0x5343** — persis
defisit per-fungsi yang sudah dikenal (place -2, pickvar -3, dst.).

### DUA relokasi yang hilang — dan sebabnya
Header asli punya 4 relokasi, kita cuma 2. Ketiga situs yang hilang ternyata
`mov ax,907h` — itu NILAI SEGMEN DGROUP yang seharusnya ditulis `MOV AX,DGROUP`
supaya LINK memancarkan fixup. `vbio.asm` sudah benar; `snd2.asm` dan
`keyio.asm` memakai literal. Diperbaiki -> keempat relokasi muncul, dan kedua
modul TETAP COCOK byte-per-byte (literal dan simbol memberi byte yang sama;
yang beda cuma ADA/TIDAKNYA fixup).
⭐ ATURAN: byte yang cocok TIDAK menjamin relokasi yang benar. Nilai segmen
yang ditulis sebagai literal lolos semua pemeriksaan byte kita, tapi membuat
.EXE tidak bisa dimuat di segmen mana pun. PERIKSA TABEL RELOKASI, bukan cuma byte.

### Kenapa .EXE masih belum jalan — bukti untuk keputusan `gendata` DGROUP 0..3
Dijalankan di emulator Unicorn: asli menelusuri normal, punya kita keluar
seketika. Sebabnya ketemu di `crt0` (0x00..0x40 muatan):
```
ASLI  89 1e 00 00   mov [0000],bx      a3 02 00   mov [0002],ax
KITA  89 1e 0c 00   mov [000c],bx      a3 0e 00   mov [000e],ax
```
Variabel `crt0` mendarat di DGROUP **+0x0C**, bukan 0x00 — DGROUP kita 12 byte
lebih panjang DI DEPAN. Ini konsekuensi konkret dari `gendata.py` yang membuang
alamat DGROUP 0..3 (`START = 4`).
⚠ Selama ini isu itu cuma dicatat sebagai "memblokir 13 byte di `main`". Sekarang
terbukti dampaknya jauh lebih besar: **ia yang membuat .EXE tidak bisa
dijalankan.** Keputusan user diperlukan sebelum menyentuhnya.


## ⭐⭐⭐ `.EXE` REKONSTRUKSI AKHIRNYA BERJALAN (2026-07-31 malam)

Emulator Unicorn proyek menjalankan `src_c/out/CONTRAP.EXE` dan ia MENELUSURI
KODE GAME SUNGGUHAN sampai masuk mode atraksi:
```
[trace] first 26ae (drawball)   [trace] first 131a (pickpart)
[trace] first 3f0f (drawslot)   [trace] first 18db (animvm)
[attract] 18db start capture (solved contraption)
FINAL CS:IP=0110:6837  started=True   EXIT state: False
```
Sebelumnya ia keluar seketika di offset 2.

### Hipotesis saya SALAH — bukan `gendata`
Iterasi lalu saya simpulkan penyebabnya `gendata.py START = 4` yang membuang
DGROUP 0..3, dan saya minta keputusan user untuk itu. **Itu keliru.** Sebab
sebenarnya:

`DATA SEGMENT` kita mulai di 0x090CC sedangkan paragrafnya 0x090C0 — jadi DATA
duduk di **offset 12 dalam grupnya**, dan `crt0` menulis ke `[0x0C]`. Di asli
DATA pas di batas paragraf sehingga offsetnya 0. Yang menentukan itu **PANJANG
SEGMEN PROG**, bukan isi DGROUP sama sekali. Isi DGROUP kita memang sudah benar
(9.556/9.556) sejak lama.

⭐ Pelajaran: "akibat yang terlihat di DGROUP" tidak berarti "sebabnya di
DGROUP". Saya melompat ke tersangka yang sudah lama ada di daftar tunggu
alih-alih mengukur dulu. Untung diperiksa sebelum menyentuh DGROUP yang 100%.

### Yang sebenarnya kurang: satu fungsi KOSONG 5 byte
Pemeriksaan cakupan manifest menemukan tepat satu lubang: **0x5318, 5 byte**
= `push bp / mov bp,sp / pop bp / ret` — badan C kosong. Tidak ada `call` yang
menunjuk ke sana (dipindai byte-per-byte), jadi ia mati di rilis; sama seperti
`setup` yang tinggal `SUB AX,AX/RET`. Ditulis sebagai `f5318.c` -> COCOK.

Menambahkan 5 byte itu membuat PROG berakhir pas di batas paragraf, DATA jatuh
di offset 0, dan `crt0` langsung menulis ke `[0x0000]` seperti asli. **Satu
fungsi kosong 5 byte yang tak pernah dipanggil adalah yang memisahkan .EXE yang
mati dari .EXE yang berjalan.**

### Koreksi batas wilayah kode
Aritmetika cakupan hanya tertutup kalau wilayah kode = **0x0082..0x6A48**, bukan
0x0082..0x69D7 seperti dicatat selama ini: `prep` (0x6939, 271 B) berakhir tepat
di 0x6A48, dan `printf` MC.LIB mulai di 0x6A48. Dengan batas itu:
jumlah manifest 27.073 + lubang 5 = 27.078 = persis besar wilayahnya.

### Keadaan .EXE sekarang
```
GLOBAL seluruh muatan : 45.725 / 46.532 = 98,3%   (awal sesi: 6,7%)
geseran di kode game  : ±3 byte saja
sisa geseran          : +110 byte, MULAI TEPAT di batas pustaka 0x6A49
ukuran                : 48.000 vs 46.532 (+1.468; DGROUP kita punya 1.364 byte
                        ekor berlebih dari `stubs.c`: sndbuf[16] + menu[360])
```

### Yang BELUM selesai
1. **+110 byte di wilayah MC.LIB** — geserannya melompat TEPAT di 0x6A49, jadi
   sumbernya modul pustaka (jumlah/urutan), bukan kode game.
2. **1.364 byte ekor DGROUP** dari `stubs.c` — `sndbuf`/`menu` kemungkinan sudah
   ada di `gdata.c` dan duplikat; perlu dicek sebelum dihapus.
3. Perilaku belum sama: punya kita tidak pernah memanggil `loadcon` (0x5035),
   dan `loadcon` memang satu dari empat fungsi yang belum byte-exact.


## TIGA SISA .EXE DITUTUP — dan jejak eksekusi kini COCOK dengan asli

### 1. `menu` diduplikasi di `stubs.c` — bug KEBENARAN, bukan cuma ukuran
`stubs.c` mendefinisikan `char menu[360]`, padahal `menu` ada @0x1c28 — DI DALAM
wilayah DGROUP terinisialisasi yang `gdata.c` sudah sediakan. Akibatnya
`goalmenu` menulis ke larik TERPISAH, bukan ke DGROUP 0x1c28. Bukan sekadar
360 byte berlebih: datanya mendarat di tempat yang salah.
Diperbaiki dengan menambah penanda `@0x1c28` pada `extern struct mitem menu[]`
di `goalmenu.c` supaya `gendata` memanennya (`char menu[288]` di gdata.c), lalu
definisi di `stubs.c` dihapus. DGROUP tetap 9.556/9.556.

### 2. `prep` 113 byte terlalu panjang — isinya modul PUSTAKA
Manifest menyebut `prep 6939 271` (berakhir 0x6A48), tapi `libmatch.py` jelas:
```
0x69d7  113 byte  CXM33   (pembantu perkalian long)
0x6a48  271 byte  PRINTF
```
Jadi 113 byte terakhir `prep.asm` sebenarnya **CXM33 milik MC.LIB**. Kode itu
tidak pernah di-PUBLIC di `prep.asm`, jadi ia beban mati: LINK tetap menarik
CXM33 dari pustaka untuk memenuhi rujukan, dan salinan lokalnya menggeser
SELURUH wilayah pustaka +113 byte. `prep.asm` dipotong ke 158 byte -> COCOK.

⚠ INI JUGA MEMBATALKAN "koreksi" saya sendiri iterasi lalu. Saya menyimpulkan
batas wilayah kode = 0x6A48 karena aritmetikanya hanya tertutup begitu.
Ternyata yang salah bukan batasnya melainkan UKURAN `prep`. Batas yang benar
tetap **0x69D7**, dan sesudah `prep` dipotong `tot_bytes` jadi tepat 26.965 =
0x69D7-0x82. ⭐ Aritmetika yang "tertutup rapi" bukan bukti — ia bisa tertutup
karena dua kesalahan saling menutupi.

### 3. Hasilnya di tingkat .EXE
```
GLOBAL seluruh muatan : 45.794 / 46.532 = 98,4%
geseran               : -3 byte KONSTAN dari 0x4959 sampai DGROUP
                        (dulu melompat +110 di batas pustaka -- sekarang TIDAK)
DATA                  : offset paragraf 0, isi 9.556/9.556
```
Geseran -3 itu PERSIS sisa kelas alokator yang diparkir. Tidak ada lagi
kesalahan tata letak.

### 4. JEJAK EKSEKUSI COCOK
Uji perilaku sebelumnya MENYESATKAN: emulator memasang hook di alamat ASLI,
sedangkan build kita bergeser -3, jadi hook untuk fungsi >=0x4959 tidak pernah
menyala. Sesudah 8 konstanta alamat di `emu.py` digeser -3:
```
KITA : 5035 6869 672f 26ae 131a 498c 3f0f 18db
ASLI : 5035 6869 672f 26ae 131a 498c 3f0f 18db 2714 278e
```
**Delapan fungsi pertama dipanggil dengan URUTAN YANG SAMA**, dan `draw672`
melonjak dari 0 ke 49.511 (blit benar-benar berjalan). Divergensi sesudahnya
wajar: `loadcon` (52 byte), `pickvar`, `place`, `main` (3 byte) belum exact.

⭐ PELAJARAN: uji perilaku yang memakai alamat TETAP tidak sah selama build
masih bergeser. Sempat menyimpulkan "kita tidak pernah memanggil loadcon"
padahal ia dipanggil di 0x5032 dan hook-nya di 0x5035.
