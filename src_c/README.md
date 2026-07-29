# src_c — rekonstruksi source C yang bisa dikompilasi ulang

Tujuan: menulis ulang kode game sebagai **source C asli** yang, dikompilasi dengan
Microsoft C 1.04 (kompiler yang dipakai tahun 1985), menghasilkan **byte yang sama persis**
dengan `CONTRAP_UNPACKED.EXE`.

Ini BERBEDA dari `work/ghidra_out/decompiled.c` — berkas itu keluaran Ghidra untuk dibaca
manusia (862 tipe `undefined`, 217 variabel `in_*`, 0 `#include`), tidak bisa dikompilasi.

## Isi
```
src/      berkas .c hasil rekonstruksi (satu fungsi/kelompok per berkas)
build/    compile.ps1 — kompilasi lewat MS C 1.04 di dalam DOSBox-X
verify/   objcode.py  — banding byte .OBJ kita vs biner asli
out/      keluaran build (.OBJ, log) — tidak diversikan
```

## Cara pakai
```
pwsh src_c/build/compile.ps1 -Name delay          # -> src_c/out/delay.OBJ
python src_c/verify/objcode.py src_c/out/delay.OBJ 2692 28
```
Argumen ke-2 dan ke-3 = alamat & ukuran fungsi di biner asli (lihat
`work/ghidra_out/functions.txt`).

## Status
Jalankan `pwsh src_c/build/buildall.ps1` lalu `python src_c/verify/verifyall.py`
untuk tabel status terkini.

| fungsi | alamat | ukuran | hasil |
|---|---|---|---|
| `delay` | `0x2692` | 28 B | ✅ percobaan ke-1 |
| `kbflush` | `0x36ef` | 31 B | ✅ percobaan ke-1 |
| `goalmenu` | `0x3322` | 248 B | ✅ percobaan ke-2 (+1 probe) |
| `mainmenu` | `0x341a` | 178 B | ✅ percobaan ke-1 |
| `lvlmenu` | `0x32bb` | 103 B | ✅ percobaan ke-2 |
| `menu9` | `0x30bb` | 37 B | ✅ percobaan ke-2 |
| `menu11` | `0x30e0` | 37 B | ✅ percobaan ke-2 |
| `menu12` | `0x3105` | 37 B | ✅ percobaan ke-2 |
| `clrbot` | `0x5911` | 37 B | ✅ percobaan ke-2 |
| `setball` | `0x2a53` | 51 B | ✅ percobaan ke-2 |
| `tone` | `0x370e` | 38 B | ⏳ 8 byte beda — lihat catatan di berkasnya |

**787 byte dari 19.750 (4,0%) — 10 fungsi dari 60.**

## Catatan penting: byte-identical ≠ source aslinya

Beberapa bentuk penulisan menghasilkan byte yang SAMA PERSIS. Yang kita bangun adalah
source yang *menghasilkan biner yang sama*, bukan tentu teks yang diketik penulis aslinya
tahun 1985. Untuk tujuan proyek ini (rebuild byte-identical) itu cukup — tapi jangan
menyebutnya "kode asli yang dipulihkan".

Contohnya variabel `unused` di beberapa fungsi: biner asli menyisihkan slot bingkai yang
tak pernah ditulisi. Kita mereproduksinya dengan variabel tak-terpakai. Penulis aslinya
mungkin menulis sesuatu yang lain yang kebetulan menghasilkan bingkai sama.

## ⭐ METODE UTAMA: kejar DIVERGENSI PERTAMA, jangan menebak bentuk fungsi

Ini cara kerja yang paling ampuh, ditemukan setelah tiga putaran nyaris tanpa hasil.

**Salah** (boros): menebak satu bentuk penulisan untuk seluruh fungsi, kompilasi, lihat
"panjang beda", tebak lagi. Tiap siklus cuma menguji satu hipotesis besar dan sering
bergerak ke arah yang salah.

**Benar** (cepat): cari **byte pertama yang berbeda**, lihat instruksi di titik itu saja,
perbaiki tepat itu, kompilasi lagi. Divergensi berikutnya akan bergeser maju. Ulangi.
Tiap siklus menutup satu keputusan penulisan yang KONKRET.

```python
d = [k for k in range(n) if code[k] != orig[k] and k not in slots]
print('beda pertama +%d' % d[0])
print('kita:', code[d[0]-8 : d[0]+24])
print('asli:', orig[d[0]-8 : d[0]+24])
```

Contoh nyata: `drawpal` mandek di 192/204 setelah tiga tebakan buta (bahkan makin jauh:
186, 181). Dengan mengejar divergensi pertama, tiga siklus langsung menutupnya —
tiap siklus memberi satu fakta: (1) koordinat x ditampung lokal lalu dipakai `x+0x1f`,
(2) `nmech` tidak ditampung, (3) `lo+i` DIHITUNG ULANG di dalam cabang, slotnya cuma
sementara-kompiler. `timedrw` menyusul dua siklus: return awal, lalu urutan penunjuk.

## ⭐ RUMUS UKURAN BINGKAI (diturunkan lewat probe terkendali)

```
sub sp = 2 × (jumlah lokal) + 2 × (temp maksimum yang dibutuhkan ekspresi)
```

Diukur dengan `probes/probe5.c` (tiap faktor divariasikan satu per satu):

| bentuk | bingkai | catatan |
|---|---|---|
| tanpa lokal, hanya panggilan | **tak ada** | `ff(1,2,3)` tidak memesan bingkai sama sekali |
| tanpa lokal, `g = h + k` | 2 | satu temp |
| tanpa lokal, `(h+k)*(h-k)` | 4 | **dua** temp |
| tanpa lokal, `199-(h+(k*g)/3)` | 2 | satu temp — pola moveball |
| 1 lokal terpakai | 2 | |
| 1 lokal TIDAK terpakai | 2 | lokal tak terpakai TETAP dialokasikan |
| 2 lokal + `g = x + y` | 6 | 4 lokal + 2 temp |
| `x = ff(); g = x;` | 4 | 1 lokal + 1 temp |
| `g = ff() + 1;` | 2 | tanpa lokal |

**Cara pakai saat bingkai meleset:** selisihnya selalu kelipatan 2. Kalau kita
KELEBIHAN satu slot, biasanya ada satu pernyataan yang menuntut dua temp — cari
ekspresi yang menghitung dua nilai hidup sekaligus, dan ubah jadi bentuk yang
memakai kembali hasil sebelumnya.

**Penugasan bersarang** adalah alat utamanya. `balltop = 199 - (ballx = expr);`
menahan nilai di register (store ke `ballx` ditunda) sehingga hanya butuh SATU
temp, sementara menulisnya sebagai dua pernyataan terpisah memaksa baca-ulang
dari memori, dan menghitung ulang ekspresinya memaksa temp kedua. Inilah yang
akhirnya menutup `moveball` setelah sepuluh percobaan gagal.

## Teknik: pakai PROBE, jangan iterasi fungsi penuh

Saat sebuah fungsi tidak cocok, JANGAN menebak lalu mengompilasi ulang fungsi utuh.
Tulis probe kecil berisi 2–3 varian penulisan dari potongan yang meragukan saja
(lihat `src/probe3.c`), kompilasi sekali, lalu bandingkan BENTUK kodenya. Satu putaran
probe menjawab pertanyaan yang bisa memakan sepuluh iterasi tebak-tebakan.

Contoh nyata: `goalmenu` meleset 18 byte. Probe dgn 3 varian langsung menunjukkan
varian mana yang benar, dan percobaan berikutnya langsung cocok.

## Aturan main (mahal dipelajari, jangan diulang)

1. **Gaya K&R, bukan C modern.** MS C 1.04 pra-ANSI: parameter dideklarasikan setelah
   baris nama fungsi, tanpa prototype, tanpa `void`.
2. **`unsigned long` TIDAK ADA.** Mencobanya → `Error 77: identifier expected`.
   Tipe yang tersedia: `char, int, unsigned, long, float, double`.
3. **Kompilernya tidak mengoptimasi.** Perkalian `long` jadi panggilan rutin + loop geser,
   bukan satu instruksi. Jangan menulis C "pintar" berharap keluar kode ringkas — tulis
   yang lugas, itu yang cocok.
4. **Nama berkas WAJIB 8.3.** DOS tidak mengenal nama panjang; kalau dilanggar, alat akan
   "berhasil" tanpa mengerjakan apa pun (gagal diam-diam).
5. **Tidak semua fungsi berasal dari C.** Lihat §Fungsi assembly di bawah — memaksakan
   rekonstruksi C untuk fungsi assembly hanya membuang waktu.
6. **Satu `.OBJ` memuat beberapa segmen** (kode DAN data). Menggabungkannya berdasar offset
   akan membuat data menimpa awal kode. `objcode.py` memisahkan per segmen.
7. **Slot relokasi dibaca dari record FIXUPP**, bukan ditebak dari "byte kita nol".
   Tebakan itu pernah menyamarkan 2 byte berbeda sungguhan jadi laporan "cocok".
8b. **Urutan deklarasi lokal = urutan slot.** Penampung hasil panggilan biasanya
   dideklarasikan LEBIH DULU (jatuh di `bp+2`), pencacah loop sesudahnya (`bp+4`).
   Kalau instruksinya benar tapi nomor slotnya tertukar, cukup tukar urutan deklarasi.
8c. **Operan pembanding tidak boleh dibalik.** Tulis `if (r > best)` — nilai yang sudah
   ada di AX di sebelah KIRI. Menulis `if (best < r)` memaksa kompiler memuat `best`
   ke register dulu (`mov bx,[best]; cmp bx,ax`) = 2 byte lebih panjang.
8d. **Alamat DGROUP bukan konstanta biasa.** Nilai seperti `0x1dd0` yang ternyata alamat
   harus ditulis sebagai simbol (`sndptr = tune1;`), karena alamat relokatabel dimuat
   lewat `mov ax,OFFSET x` lalu disimpan — bukan store-immediate. Penugasan penunjuk
   juga ditulis SEBELUM penugasan konstanta di sebelahnya, supaya pemuatan alamat
   muncul lebih dulu seperti di biner asli.
8. **Hasil panggilan fungsi ditampung variabel tersendiri**, jangan disarangkan.
   Tulis `h = f(...); y = y + h;` BUKAN `y = y + f(...)`. Bentuk bersarang membuat
   kompiler tidak mengalokasikan slot sementara dan memilih register lain
   (`mov ax,0eh` alih-alih `mov cx,0eh`) → kode beda. Ini pola menyeluruh di
   biner ini, bukan kebetulan satu fungsi.
8e. **Nilai yang di-`switch` TIDAK ditampung variabel** — pengecualian dari aturan 8.
   `switch (getkey())` biarkan hasilnya di AX. Menampungnya menambah slot bingkai dan
   mengubah tiap pembandingan jadi akses memori (`83 7e 04 ..` bukan `3d ..`).
8f. **Kenali `switch` dari tata letaknya**: badan tiap case ditaruh LEBIH DULU, lalu
   `jmp` ke rantai pembanding di BAWAH. Rantai if/else-if menaruh uji di depan.
   **Urutan `case` di sumber = urutan badan case di biner**; rantai pembandingnya
   muncul TERBALIK. Kalau instruksinya benar tapi urutannya tertukar, balik urutan case.
   (Untuk case yang banyak, kompiler beralih ke tabel — lihat `probes/probe4.c`.)
8g. **Uji batas bawah ditulis `x >= 0`, bukan `x > -1`.** Aslinya `test bx,bx; js`
   (uji tanda); `> -1` menghasilkan `cmp bx,-1; jle` yang 2 byte lebih panjang.
8h. **Jangan memberi nama lokal untuk nilai yang cukup hidup di register.** Kalau
   `sub sp,N` lebih besar dari aslinya, kemungkinan besar ada lokal yang tidak
   seharusnya ada (contoh: `timebar` — semuanya cukup di AX/BX).
8i. **Basis bingkai TIDAK selalu 2.** Rumusnya `sub sp = basis + 2×jumlah_lokal`,
   tapi basisnya berbeda antar fungsi (delay: 2, xform: 4). Cara pakai: kompilasi
   sekali, lihat selisih `sub sp` kita vs asli, lalu tambah/kurangi jumlah lokal
   sebanyak selisih/2. Jangan mencoba menghitungnya dari teori.
9. **Urutan deklarasi lokal menentukan tata letak bingkai.** Ukuran bingkai =
   `2 + 2×jumlah_lokal`, dan variabel dialokasikan sesuai urutan deklarasi
   (deklarasi pertama di `bp+2`). Kalau ukuran `sub sp,N` tidak cocok, jumlah atau
   urutan lokal masih salah — itu petunjuk paling cepat.

## Fungsi assembly (jangan direkonstruksi sebagai C)

Prolog MS C 1.04 selalu `push bp; sub sp,N; mov bp,sp`. Sensus 144 fungsi:

| | jumlah | byte |
|---|---|---|
| prolog C → hasil kompilasi | 93 | 26.445 |
| bukan prolog C → assembly tulisan tangan / rutin pustaka | 51 | 2.542 |

Yang assembly termasuk **semua primitif grafis**: `672f` (blit sprite), `6453` (teks),
`5cbb` (garis/span), `6524`/`657c`/`6869` (blit bermasker) — semuanya berpola
`push bp; push es; mov bp,sp`, menyimpan ES karena menulis ke memori video.
Juga `5a5b` (RNG kongruen linier) yang memakai `mul` dan mengambil word tinggi dari DX —
mustahil ditulis di C 1983 karena `unsigned long` belum ada.

## Sisa pekerjaan — ANGKA DIKOREKSI 2026-07-29

Perkiraan lama (**19.750 byte**) TERLALU KECIL. Sebabnya: ukuran di
`work/ghidra_out/functions.txt` menghitung hanya potongan pertama yang bersambung dari
sebuah fungsi. Fungsi yang badannya terpecah oleh lompatan dihitung jauh lebih kecil dari
sebenarnya. Contoh terbukti: `FUN_1000_18db` tercatat 1.229 byte, kenyataannya
**3.040 byte** (0x18db..0x24ba, epilog di 0x24b6).

Angka yang lebih jujur, dihitung dari wilayah alamat (bukan dari daftar fungsi):

| wilayah | byte | keterangan |
|---|---|---|
| Segmen kode seluruhnya | 36.976 | 0x0000..0x9070 |
| Wilayah pustaka (≥0x6a48) | 9.768 | rutin `MC.LIB` — cukup di-link |
| **Wilayah kode game (<0x6a48)** | **27.208** | yang harus ditulis ulang |
| — di antaranya assembly tulisan tangan | ±1.200 | primitif grafis (`5cbb`,`6453`,`6524`,`657c`,`672f`,`6869`,`6939`) |
| — sisanya kode C | **±26.000** | target rekonstruksi sebenarnya |

Jadi targetnya **±26.000 byte, bukan 19.750** — sekitar 32% lebih besar.
Kemajuan 787 byte = **±3,0%**, bukan 4,0%.

**Aturan baru:** jangan percaya `size=` di `functions.txt`. Selalu cek di mana epilog
(`add sp,N; pop bp; ret`) yang cocok dengan `sub sp,N` di prolog.
