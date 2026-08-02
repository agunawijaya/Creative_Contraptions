# Tentang proyek ini

## Apa yang sebenarnya dikerjakan

Sebuah gim DOS tahun 1985 dibongkar sampai byte terakhirnya, lalu dibangun ulang —
sekarang menjadi **tiga hal yang berbeda tujuan**:

| | pertanyaannya | jawabannya |
|---|---|---|
| **`src_c/`** | apakah kodenya terbaca benar? | `.EXE` hasil kompilasi **byte-identical** dgn biner 1985 |
| **`port/`** | apakah *aturannya* dipahami? | tulis ulang dalam Python, **1.565/1.565 bingkai identik** |
| **`remake/`** | bisakah pemahaman itu jadi gim yang bebas disebarkan? | ⏳ sedang dibangun, dgn aset baru sepenuhnya |

Ketiganya menjawab pertanyaan yang berbeda, dan itu disengaja. Rekonstruksi yang cocok
byte-per-byte membuktikan **pembacaan**; ia tidak membuktikan **pemahaman** — sebuah
program bisa disalin sempurna tanpa dimengerti sama sekali. Port yang cocok piksel-per-
piksel membuktikan pemahaman, tapi masih memerlukan berkas gim aslinya. Yang ketiga
melepaskan ketergantungan itu.

## Gimnya

**Creative Contraptions** (1985) — Looking Glass Software untuk Bantam Electronic
Publishing. *Bukan* Looking Glass Studios; kemiripan namanya kebetulan.

Sebuah gim edukasi bergaya Rube Goldberg: pemain menyusun mesin bertingkat dari katrol,
tuas, bidang miring, dan pegas, lalu menjalankan bolanya untuk melihat apakah rantainya
bekerja.

- **Programmer:** Jessie Ragsdale
- **Kompiler:** Microsoft C 1.04 — yaitu Lattice C yang di-rebrand — model memori SMALL,
  `int` 16 bit
- **Tampilan:** CGA mode 4, 320×200, empat warna

Ceritanya lebih lengkap ada di [`GAME_GUIDE.md`](GAME_GUIDE.md).

## Sikap soal hak cipta

**Creative Contraptions © 1985 Bantam Electronic Publishing.** Proyek ini tidak
mengklaim hak apa pun atas gim itu, dan **tidak mendistribusikannya**.

Yang ada di repo ini:

- **kode dan analisis** — hasil membaca program, ditulis sendiri;
- **pengekstrak**, bukan hasil ekstraksi. Berkas gim (`GRAPH`, `MECHS`, `ANIMATE`,
  `MISC`, `CONTRAP`, `DGROUP.bin`) dan font ROM BIOS semuanya di-`.gitignore`. Pengguna
  menyediakan salinannya sendiri.

`src_c/` dan `port/` **memerlukan** salinan gim milikmu untuk dijalankan. `remake/`
tidak — begitu selesai, ia berdiri sendiri dan boleh disebarkan bebas.

Kalau kamu pemegang hak Creative Contraptions dan keberatan dgn apa pun di sini, hubungi
pemilik repo; materi yang dipersoalkan akan dicabut.

## Cara kerja yang dipakai

Satu aturan yang dibayar mahal berkali-kali:

> **Bandingkan ke sumber kebenaran, bukan ke keluaran sendiri.**

Setiap angka di dokumen-dokumen ini berasal dari mengadu hasil dgn gim asli yang
berjalan di emulator, per piksel dan per bingkai. Tidak ada yang berasal dari
"kelihatannya benar".

Tiga pelajaran yang paling sering menggigit, dan ketiganya diceritakan lengkap dgn
kegagalannya di [`ARCHITECTURE.md`](ARCHITECTURE.md):

1. **Angka yang membaik bukan bukti penjelasannya benar.** Beberapa hipotesis menaikkan
   skor kecocokan dgn alasan yang ternyata keliru.
2. **"Jalur kodenya sama" itu argumen, bukan pengukuran.** Enam kali bagian yang
   dibiarkan tak diuji dgn alasan itu, dan keenamnya memunculkan kesalahan.
3. **Sebelum menyimpulkan "alatnya tidak bisa", periksa alat sendiri.** Sebelas dari
   sebelas kali, "terhalang emulator" ternyata "terhalang stub/hook/urutan tombol
   sendiri".

Aturan yang sama berlaku untuk `remake/`, dgn satu perbedaan penting: di sana tidak ada
gim asli untuk dijadikan pembanding. Yang menggantikannya adalah **spesifikasi tertulis**
dan uji yang menjaga aturan mainnya — lihat [`remake/README.md`](remake/README.md).

## Kredit

- Gim asli: **Jessie Ragsdale** (Looking Glass Software), 1985.
- Pembongkaran, port, dan dokumen: pemilik repo, dibantu Claude Code.
- Alat pihak ketiga (di-`.gitignore`, unduh sendiri): Ghidra, DOSBox-X, Unicorn Engine,
  MS C 1.04 + MASM dari arsip PCjs / Internet Archive.
