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
| fungsi | alamat | ukuran | hasil |
|---|---|---|---|
| `delay` | `0x2692` | 28 B | ✅ cocok byte-per-byte, percobaan ke-1 |
| `kbflush` | `0x36ef` | 31 B | ✅ cocok byte-per-byte, percobaan ke-1 |
| `goalmenu` | `0x3322` | 248 B | ✅ cocok byte-per-byte, percobaan ke-2 (+1 probe) |

**307 byte dari 19.750 (1,6%) — 3 fungsi dari 60.**

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

## Sisa pekerjaan
Setelah dikurangi rutin pustaka `MC.LIB` (tak perlu ditulis, cukup di-link) dan fungsi
assembly, target rekonstruksi C = **60 fungsi / 19.750 byte**.
