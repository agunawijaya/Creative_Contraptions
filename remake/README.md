# `remake/` — gim baru dengan aset sendiri

> **Status: ⏳ baru dimulai.** Folder ini masih kosong selain dokumen. Titik masuk untuk
> mulai mengerjakannya ada di [`PROMPT_MULAI.md`](PROMPT_MULAI.md).

## Kenapa ada

`port/` sudah membuktikan bahwa aturan main gim 1985 dipahami — 1.565/1.565 bingkai
identik. Tapi ia **memerlukan berkas gim aslinya** untuk jalan, jadi ia tidak bisa
disebarkan.

`remake/` memakai pemahaman itu untuk membuat gim yang **berdiri sendiri**: aset dibuat
baru seluruhnya, tak satu byte pun berasal dari gim 1985.

## Aturan yang tidak boleh dilanggar

1. **`src_c/` dan `port/` TIDAK BOLEH DIUBAH.** Keduanya sudah selesai dan terverifikasi;
   nilainya justru pada ketidakberubahannya. Kalau `remake/` butuh sesuatu dari sana,
   **salin idenya, jangan sunting sumbernya**.
2. **Nol byte dari gim asli.** Tidak ada sprite hasil ekstraksi, tidak ada potongan
   `DGROUP`, tidak ada teks yang disalin apa adanya dari binernya. Nama mekanisme yang
   generik (*Pulley*, *Lever*) boleh; kalimat antarmuka gim tidak.
3. **Aset dalam format terbuka**: PNG untuk gambar, JSON untuk data. Bisa di-`diff` di
   git, bisa disunting alat mana pun.

## Yang harus dibuat — dan ini lebih banyak dari sekadar gambar

Port membaca **enam** hal dari gim asli. Lima yang pertama jelas berupa aset; yang
keenam sering terlupakan dan justru paling banyak isinya.

| dari gim asli | isinya | penggantinya di `remake/` |
|---|---|---|
| `GRAPH` | objek "zany" dan pemandangan (562 record) | sprite PNG + manifes |
| `MECHS` | 15 tipe mekanisme (30 record) | sprite PNG + manifes |
| `ANIMATE` | skrip animasi (240 record) | skrip JSON |
| `MISC` | potongan antarmuka (20 record) | sprite PNG |
| `CONTRAP` | susunan kontraption per tujuan | tata letak JSON |
| **`DGROUP.bin`** | **tabel menu, SELURUH teks antarmuka, font, sprite bola, aliran nada** | JSON + PNG + font sendiri |

⚠ `DGROUP.bin` dipakai **sepuluh modul inti** di port. Mengabaikannya berarti gimnya
tidak punya menu, tidak punya teks, tidak punya font, dan tidak punya bunyi.

## Apa yang boleh diwarisi dari `port/`

Yang boleh dan sebaiknya dipakai ulang adalah **aturan mainnya**, bukan asetnya:

- generator acak dan cara ia dipakai (`cc/core/rng.py`)
- aturan pengundian varian, part, dan slot bertanda (`cc/core/pick.py`)
- mesin animasi 17 opcode (`cc/core/vm.py`)
- aturan skoring, timer, dan petunjuk (`cc/core/hud.py`)

Semuanya sudah terukur benar terhadap gim asli, dan itu modal yang mahal. Peta lengkapnya
ada di [`../PORT_CODE_MAP.md`](../PORT_CODE_MAP.md); alasan di balik bentuknya ada di
[`../PORT_ARCHITECTURE.md`](../PORT_ARCHITECTURE.md).

## Yang berubah dibanding `port/`

- **Resolusi dan warna lebih tinggi.** Ini keputusan yang sudah diambil, dan
  konsekuensinya nyata: seluruh koordinat, ukuran slot, dan tata letak di `port/` diukur
  pada 320×200 empat warna. Semuanya harus diskalakan ulang — dan itu justru alasan
  memakai kelipatan bulat, supaya penskalaannya bisa diperiksa.
- **Tidak ada pembanding piksel.** Di `port/` kebenaran diukur terhadap gim asli. Di
  sini tidak ada rujukan seperti itu. Penggantinya: **spesifikasi tertulis** untuk tiap
  aset, dan uji yang menjaga aturan mainnya (mis. "tiap goal bisa dimenangkan", "rantai
  undian dari seed yang sama selalu memberi hasil yang sama").

## ⭐ Titik sambung adalah DATA, bukan gambar

Gim ini menyambungkan komponen — tali ke katrol, tuas ke bola — dan rantai aksi-reaksinya
harus tepat. Nalurinya: "aset baru harus punya titik sambung yang sama dgn aset asli".

**Itu keliru, dan justru mempersulit.** Titik sambung bukan properti piksel. Ia
*waypoint* di skrip ANIMATE, dalam koordinat **lokal terhadap slot** part itu. Contoh
terukur, goal 1:

| part | slot (y,x) | masuk | keluar | lempar (A,N) |
|---|---|---|---|---|
| 0 | 11, 8 | (10, 20) | (14, 49) | (10, 10) |
| 1 | 67, 48 | (0, 21) | (15, 0) | (4, 4) |
| 2 | 97, 28 | (0, 14) | (23, 34) | (5, 6) |

Dan lemparan antar-part (opcode `0x03`) **mendarat tepat di waypoint PERTAMA part
tujuan** — terukur saat memperbaiki bug goal 6 varian 2. Jadi tali "menyambung" bukan
karena pikselnya bertemu, melainkan karena angkanya bertemu. Sprite hanya perlu
**terlihat** benar di titik itu.

### Karena itu: jangkar sebagai KONTRAK

Tiap aset punya berkas pendamping berisi titik jangkarnya dalam piksel lokal. Pelukis
menggambar **memenuhi kontrak**, bukan meniru gambar lama.

```json
{
  "id": "katrol-01",
  "sprite": "katrol-01.png",
  "ukuran": [60, 46],
  "jangkar": {
    "masuk":  [20, 10],
    "keluar": [49, 14],
    "tali":   [[30, 4], [30, 40]]
  },
  "lempar": { "lengkung": 10, "langkah": 10 }
}
```

Tiga keuntungannya: ikut terskala saat resolusi naik, mengizinkan bentuk yang
benar-benar baru, dan — yang terpenting — **bisa diuji**.

### Uji penggantinya: KONTINUITAS RANTAI

Di `port/` kebenaran dijaga dgn mengadu ke gim asli. Di sini rujukan itu tidak ada.
Penggantinya:

> Untuk tiap kontraption, jalankan VM-nya dan pastikan titik **keluar** part N berimpit
> dgn titik **masuk** part N+1 sesudah lemparan, dalam toleransi yang ditetapkan.

Itu memeriksa aksi-reaksinya secara langsung, dan berjalan **tanpa gim asli sama
sekali**. Tulis uji ini SEBELUM aset pertama digambar.

### ⚠ Tabrakan yang harus disadari

Angka-angka di tabel atas adalah **data gim asli**. Aturan folder ini berbunyi "nol byte
dari gim asli". Mewarisi waypoint = mewarisi data, dan itu menggugurkan tujuan "boleh
disebarkan bebas".

Keputusannya: **geometrinya DIKARANG ULANG.** Angka asli boleh dipakai sebagai rujukan
rasa saat mengembangkan, tapi TIDAK ikut disebarkan. Yang diwarisi hanya *aturan* —
opcode VM, urutan rantai, cara RNG dipakai — dan itu ide, bukan data.

Arahnya jadi terbalik, dan justru lebih bebas: **gambar dulu, jangkarnya menentukan
skripnya** — bukan skrip lama menyandera gambarnya.

*(Catatan: "nol byte" adalah aturan yang proyek ini tetapkan sendiri, bukan nasihat
hukum.)*

## Cara mulai

Buka [`PROMPT_MULAI.md`](PROMPT_MULAI.md), salin isinya ke Claude Code di mesin tempat
kamu ingin mengerjakan asetnya.
