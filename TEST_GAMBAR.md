# Uji tampilan gambar — putaran 2

Hasil putaran 1: **cara 1 dan 2 muncul**, cara 3 (`file:///`) dan cara 4 (`<img>`) tidak.

Artinya viewer Anda **memang bisa memuat gambar lokal lewat path relatif** — dan itu
persis sintaks yang dipakai `ARCHITECTURE.md`, `CODE_MAP.md`, dan `GAME_GUIDE.md`.
Jadi penyebabnya bukan sintaks, melainkan gambar tertentu atau konteks tertentu.

Di bawah ini **setiap gambar yang dirujuk ketiga dokumen**, ditulis persis seperti di
dokumen aslinya. Beri tahu saya **nomor mana saja yang kosong**.

---

## A. Diagram (dipakai ARCHITECTURE.md & CODE_MAP.md)

**A1** — 1060×520, 51 KB

![Tata letak memori](work/doc/doc_mem_layout.png)

**A2** — 1000×430, 31 KB

![Encoding piksel CGA](work/doc/doc_cga_pixel.png)

**A3** — 1120×430, 39 KB

![Record arsip 12 byte](work/doc/doc_record.png)

**A4** — 1060×470, 39 KB

![Pemampatan RLE](work/doc/doc_rle.png)

**A5** — 1060×330, 33 KB

![Rantai perkakas](work/doc/doc_pipeline.png)

**A6** — 1340×560, 51 KB (gambar TERLEBAR)

![Anatomi satu layar](work/doc/doc_anatomi.png)

---

## B. Katalog (dipakai CODE_MAP.md & GAME_GUIDE.md)

**B1** — 650×430, 12 KB

![Katalog mekanisme](work/catalog_mechs.png)

**B2** — 720×850, 46 KB

![Katalog objek zany](work/catalog_zany.png)

---

## C. Lembar kontak (dipakai GAME_GUIDE.md)

**C1** — 658×2206, 104 KB (gambar TERTINGGI dan TERBESAR)

![Semua susunan Fill in Mechanisms](work/fillmech_semua_varian.png)

---

## D. Gambar di DALAM tabel (dipakai GAME_GUIDE.md)

Ini tersangka utama: sebagian penampil Markdown tidak merender gambar di dalam sel tabel.

**D1 dan D2** — masing-masing 320×200, ~5 KB

| Sebelum | Sesudah |
|---|---|
| ![Slot kosong](work/screens_gen/fillmech_goal1_v0_kosong.png) | ![Terpasang](work/screens_gen/fillmech_goal1_v0_penuh.png) |

---

## E. Gambar yang sama, TANPA tabel

Kalau D kosong tapi E muncul, berarti benar soal tabelnya.

**E1**

![Slot kosong](work/screens_gen/fillmech_goal1_v0_kosong.png)

**E2**

![Terpasang](work/screens_gen/fillmech_goal1_v0_penuh.png)

---

## Yang perlu Anda laporkan

Cukup sebutkan kode yang **kosong**, misalnya "A6 dan C1 kosong, sisanya muncul".

Dugaan saya, berdasarkan pola kegagalan putaran 1:

- **kalau D kosong tapi E muncul** → viewer tidak merender gambar di dalam tabel.
  Perbaikannya: di `GAME_GUIDE.md` saya keluarkan kedua gambar itu dari tabel.
- **kalau C1 kosong** → ada batas ukuran/tinggi. Perbaikannya: lembar kontak saya pecah
  jadi beberapa gambar yang lebih kecil.
- **kalau A6 kosong** → ada batas lebar. Perbaikannya: diagram saya bangkitkan ulang
  dengan lebar lebih kecil.
- **kalau semuanya muncul di sini** → berarti tadi dokumennya dilihat sebelum gambarnya
  dibuat, atau penampilnya menyimpan cache. Coba tutup dan buka ulang berkasnya.
