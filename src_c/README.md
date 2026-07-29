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
