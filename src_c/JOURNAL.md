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
