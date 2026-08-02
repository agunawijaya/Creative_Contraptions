# Prompt untuk dijalankan di mesin lain

Salin **seluruh blok di bawah** ke Claude Code yang dijalankan dari root repo
(`Creative_Contraptions/`) di mesin tempat kamu ingin mengerjakan aset barunya.

Prasyarat di mesin itu: `git`, Python 3.11+, `pip install pygame pillow`.
**Berkas gim asli TIDAK diperlukan** untuk `remake/` — itu justru intinya.

---

```
Kerjakan kategori KETIGA repo ini: `remake/` — gim baru dgn aset sendiri.

BACA DULU, jangan lewati:
  README.md          peta repo, tiga kategori
  remake/README.md   aturan dan daftar yang harus dibuat
  ABOUT.md           sikap proyek soal hak cipta
  PORT_ARCHITECTURE.md  bentuk porting yang sudah ada, dan ALASANNYA
  PORT_CODE_MAP.md      peta modul port <-> fungsi gim 1985
  CLAUDE.md          aturan kerja proyek (berlaku juga di sini)

KONTEKS. Repo ini berisi pembongkaran gim DOS 1985 "Creative Contraptions",
dan sudah punya DUA hasil yang SELESAI dan TERVERIFIKASI:
  src_c/  source C yang dikompilasi ulang -> .EXE byte-identical
  port/   tulis ulang Python, 1.565/1.565 bingkai identik dgn gim asli
Keduanya butuh salinan gim asli untuk jalan, jadi tidak bisa disebarkan.

TUJUAN. `remake/` memakai pemahaman itu untuk gim yang BERDIRI SENDIRI:
seluruh asetnya baru, tak satu byte pun dari gim 1985, sehingga boleh
disebarkan bebas.

ATURAN KERAS:
1. JANGAN mengubah apa pun di `src_c/` atau `port/`. Keduanya selesai dan
   nilainya justru pada ketidakberubahannya. Kalau butuh sesuatu dari sana,
   SALIN IDENYA ke `remake/`, jangan sunting sumbernya. Sesudah tiap
   perubahan, pastikan 23 berkas `work/test_*.py` masih lulus.
2. NOL byte dari gim asli. Tidak ada sprite hasil ekstraksi, tidak ada
   potongan DGROUP, tidak ada kalimat antarmuka yang disalin dari binernya.
   Nama mekanisme generik (Pulley, Lever) boleh.
3. Aset dalam format TERBUKA: PNG untuk gambar, JSON untuk data.
4. Resolusi dan warna LEBIH TINGGI dari aslinya (320x200, 4 warna).

YANG HARUS DIBUAT. Port membaca ENAM hal dari gim asli; kelimanya jelas aset,
yang keenam paling sering terlupakan:
  GRAPH      objek zany + pemandangan   -> sprite PNG + manifes
  MECHS      15 tipe mekanisme          -> sprite PNG + manifes
  ANIMATE    skrip animasi              -> skrip JSON
  MISC       potongan antarmuka         -> sprite PNG
  CONTRAP    susunan kontraption        -> tata letak JSON
  DGROUP.bin tabel menu, SELURUH teks, font, sprite bola, aliran nada
             -> JSON + PNG + font sendiri   <- dipakai 10 modul inti port

BOLEH DIWARISI dari port/ (aturan main, BUKAN aset): rng.py, pick.py, vm.py,
hud.py. Semuanya sudah terukur benar terhadap gim asli.

⭐ TITIK SAMBUNG ADALAH DATA, BUKAN GAMBAR. Gim ini menyambungkan komponen
(tali-katrol, tuas-bola) dan rantai aksi-reaksinya harus tepat. Tapi titik
sambungnya BUKAN properti piksel: ia waypoint di skrip ANIMATE, dalam
koordinat LOKAL terhadap slot part. Terukur, goal 1:

    part0 slot(11,8)   masuk(10,20) keluar(14,49) lempar(A=10,N=10)
    part1 slot(67,48)  masuk(0,21)  keluar(15,0)  lempar(A=4,N=4)
    part2 slot(97,28)  masuk(0,14)  keluar(23,34) lempar(A=5,N=6)

dan lemparan `op03` MENDARAT TEPAT DI WAYPOINT PERTAMA part tujuan. Jadi tali
menyambung karena ANGKANYA bertemu, bukan pikselnya. Sprite cuma perlu
TERLIHAT benar di titik itu.

MAKA: jangkar sebagai KONTRAK, bukan warisan. Tiap aset punya berkas
pendamping berisi titik jangkar dalam piksel lokal:

    { "id": "katrol-01", "sprite": "katrol-01.png", "ukuran": [60,46],
      "jangkar": { "masuk": [20,10], "keluar": [49,14],
                   "tali": [[30,4],[30,40]] },
      "lempar": { "lengkung": 10, "langkah": 10 } }

Pelukis menggambar MEMENUHI kontrak, bukan meniru gambar lama. Kontrak ikut
terskala saat resolusi naik, mengizinkan bentuk baru, dan BISA DIUJI.

UJI PENGGANTI PEMBANDING PIKSEL -- kontinuitas rantai:
  untuk tiap kontraption, jalankan VM dan pastikan titik KELUAR part N
  berimpit dgn titik MASUK part N+1 sesudah lemparan, dalam toleransi.
Itu memeriksa aksi-reaksinya langsung, tanpa gim asli. TULIS UJI INI SEBELUM
ASET PERTAMA DIGAMBAR.

⚠ TABRAKAN YANG SUDAH DIPUTUSKAN: angka waypoint di atas adalah DATA GIM
ASLI, sementara aturan folder ini "nol byte dari gim asli". Keputusannya:
GEOMETRINYA DIKARANG ULANG. Angka asli boleh jadi rujukan rasa saat
mengembangkan, TIDAK ikut disebarkan. Yang diwarisi hanya aturan (opcode VM,
urutan rantai, cara RNG dipakai) -- itu ide, bukan data. Arahnya terbalik dan
lebih bebas: GAMBAR DULU, JANGKARNYA MENENTUKAN SKRIPNYA.

TANYAKAN KE SAYA DULU sebelum menulis kode, empat hal ini menentukan
segalanya dan saya belum memutuskannya:
  1. Resolusi target. Saran: kelipatan BULAT dari 320x200 (640x400 atau
     960x600) supaya seluruh koordinat yang sudah terverifikasi bisa
     diskalakan dan diperiksa. Kalau bebas, penskalaannya tidak bisa diuji.
  2. Palet: tetap 4 warna (gaya retro, aset jauh lebih cepat dibuat) atau
     penuh?
  3. Mesin: lanjut Python/pygame seperti port/, atau lain?
  4. Arah artistik: meniru gaya 1985, atau tampilan baru sepenuhnya?

CARA KERJA (dari CLAUDE.md, berlaku penuh di sini):
- UKUR, jangan simpulkan dari membaca.
- Di sini TIDAK ADA pembanding piksel: gim asli tidak dipakai sebagai rujukan
  aset. Penggantinya spesifikasi TERTULIS per aset + uji yang menjaga aturan
  main (mis. "tiap goal bisa dimenangkan", "seed sama -> undian sama").
  Tulis ujinya SEBELUM asetnya, supaya "kelihatannya benar" tidak jadi bukti.
- Tiap kemajuan nyata: commit + push ke origin/main + perbarui dokumen root,
  dalam satu tarikan.
- Kalau sesuatu ambigu dan tebakan yang berbeda menghasilkan pekerjaan yang
  berbeda, TANYA dulu.

LANGKAH PERTAMA: baca dokumen di atas, ajukan keempat pertanyaan itu, lalu
usulkan rencana bertahap yang tiap tahapnya menghasilkan sesuatu yang BISA
DIJALANKAN — bukan tahap "bikin semua aset dulu".
```

---

## Sesudah dijalankan di mesin itu

Repo yang sama, jadi cukup `git pull` di mesin ini untuk menariknya kembali.
Kalau dua mesin mengerjakan bersamaan, kerjakan di cabang terpisah supaya
riwayatnya tidak bertabrakan.
