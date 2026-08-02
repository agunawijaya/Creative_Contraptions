# Peta kode port — fungsi 1985 ↔ modul Python

> Untuk siapa dokumen ini: orang yang sudah membaca [`CODE_MAP.md`](CODE_MAP.md) (peta
> gim aslinya, per alamat) dan ingin melihat **ke mana tiap bagiannya pergi** di
> tulisan ulangnya. Penjelasan *kenapa*-nya ada di
> [`PORT_ARCHITECTURE.md`](PORT_ARCHITECTURE.md).

Semua alamat di sini mengacu ke biner gim yang sudah dibuka kemasannya, dan diambil dari
`src_c/src/*.c` — sumber yang, dikompilasi ulang, menghasilkan `.EXE` byte-identical.
Kalau dokumen ini dan sumber itu berbeda, **sumbernya yang benar**.

---

## 1. Bentuk keseluruhan

```
port/
  main.py            mesin keadaan + gelung pygame          (padanan `main` @0x0082)
  import_assets.py   penyalin aset (sekali jalan)
  import_romfont.py  pengekstrak font ROM BIOS
  cc/
    cga.py           palet CGA & penskalaan jendela
    assets.py        pencari folder data
    core/            ← INTI: satu implementasi, tanpa jalur kedua
```

Aturan yang dipegang: **satu implementasi per aturan gim.** Kalau sebuah perilaku
ditulis dua kali, uji akan menguji salinan yang salah — dan itu pernah benar-benar
terjadi (lihat `PORT_ARCHITECTURE.md` §5).

## 2. Modul inti, dan apa padanannya

| modul | baris | padanan di gim asli | isi |
|---|---:|---|---|
| `rng.py` | 76 | `rnd()` **@0x5A5B** | LCG 16-bit; hasil = kata **tinggi** dari `n × seed` |
| `archive.py` | 149 | `loadarc()` @0x531D, `load()` @0x53FF | direktori arsip + dekode RLE |
| `contrap.py` | 161 | `loadcon()` @0x5035 | berkas `CONTRAP` + aturan penempatan slot |
| `pick.py` | 439 | `nvar()` @0x4094, `pickpart()` @0x131A, `mkpal()` @0x3909, `setmark()` @0x10FD, `setzany()` @0x1200, `fillans()` @0x149D | seluruh pengundian isi layar |
| `skrip.py` | 58 | pembaca `ANIMATE` | menemukan skrip satu part |
| `vm.py` | 451 | `animvm()` **@0x18DB** | 17 opcode + `bounce()` @0x2504 |
| `adegan.py` | 609 | `drawball` @0x26AE, `xform` @0x5E3B | satu adegan utuh: layar diam + animasinya |
| `render.py` | 401 | `blit` @0x672F, `fillrect` @0x6869, `shftr` @0x6600 | primitif gambar + dua kanvas |
| `font.py` | 93 | `text()` @0x644A | font gim (dari segmen datanya) |
| `dosfont.py` | 73 | `printf()` @0x6A48 → DOS | font ROM BIOS, khusus pesan permainan |
| `dgtab.py` | 84 | segmen data (DGROUP) | pembaca tabel di segmen data |
| `menu.py` | 225 | `setsel()` @0x3769, `show()` @0x381A, `runmenu()` @0x34CC | 12 layar bertabel |
| `palet.py` | 182 | `drawpal()` @0x3B83 | strip pemilih part di dasar layar |
| `hud.py` | 492 | `showsc`, `timedrw`, `hintmark`, `prompts` | bilah status, skor, timer, petunjuk |
| `resensi.py` | 85 | `review()` @0x3C4F | tata letak layar *Review Mechanisms* |
| `bunyi.py` | 181 | penangan interupsi timer `tone3` @0x5B73 | tiga mode aliran nada |

Kira-kira **5.700 baris Python** menggantikan **26.965 byte kode mesin**. Perbandingan
itu tidak berarti banyak — sebagian besar baris Python adalah komentar yang menjelaskan
kenapa sesuatu ditulis begitu, dan itu memang disengaja.

## 3. Tempat-tempat yang paling mudah salah

Bagian ini yang paling berguna kalau kamu sedang membangun ulang program lain. Semuanya
pernah salah di sini, dan semuanya ditemukan lewat pengukuran, bukan pembacaan.

### 3.1 Urutan gambar, bukan lapisan

Model yang intuitif — "latar, lalu bola di atasnya" — **salah**. Yang benar:

```
VRAM saat masuk drawball ke-N  =  hasil drawball ke-(N−1)  +  part yang di-blit sesudahnya
```

Jadi part yang digambar **sesudah** bola akan menutupi bola itu. Dan `drawball` sendiri
menghapus bola sebelumnya dengan mengembalikan salinan latar yang **tertinggal**, bukan
latar terkini — itulah sebabnya di gim asli kadang tampak "lubang" berwarna latar lama
di dalam part yang baru digambar. Artefak itu ditiru, karena ia memang terlihat.

### 3.2 Nama variabel adalah hipotesis

Empat nama global terbukti salah, dan tiap kali yang membongkarnya **pemakaiannya**,
bukan tampilannya:

| nama | isi sebenarnya |
|---|---|
| `bally` | koordinat **X** layar |
| `ballx` | koordinat **Y** layar |
| `goal` | **jumlah bola**, bukan nomor tujuan |
| `mode_` / `seed` | pegangan berkas |

Yang membongkar `bally`: sebuah gelung memasang ikon bola **berjajar mendatar** sambil
menaikkan argumen kedua — argumen yang disimpan ke variabel bernama `bally`.

### 3.3 Dua besaran mirip yang bukan satu hal

- **`sub` bukan nomor tujuan** di mode Contraption Mix Up. Mode itu tidak memakai
  pemilih tujuan sama sekali: ia memasang `sub = 0` lalu menaikkannya tiap ronde.
- **Indeks varian relatif vs absolut.** Gelung penghindar varian di `loadcon`
  membandingkan indeks **absolut** di direktori (`rnd(cnt) + first`) dengan nilai
  sebelumnya. Keduanya kebetulan sama hanya untuk tujuan pertama, yang `first`-nya nol.
- **Cacah palet vs cacah record.** Satu undian memakai jumlah **palet** sebagai batas
  tapi mengindeks **direktori record**. Itu memang begitu di binernya.

### 3.4 Tabel mana yang dipakai berbeda per mode

`loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`:

| mode | isi `base` |
|---|---|
| Fill in Mechanisms / Zany | direktori **disaring + dipadatkan** — hanya jenis yang dipakai |
| Contraption Mix Up | direktori **penuh** |

Memberi direktori penuh untuk mode isian tetap menghasilkan **cacah** yang benar tapi
**record** yang salah — gejalanya thumbnail di strip yang meleset, bukan program yang
gagal. Kesalahan yang diam seperti ini yang paling lama bertahan.

## 4. Cara memeriksa sendiri

Tidak ada satu pun angka di dokumen ini yang perlu kamu percayai. Semuanya bisa
dibangkitkan ulang:

```
python work/test_anim_vs_gim.py    # animasi: 1.565/1.565 bingkai
python work/test_play.py           # layar bermain: 20 kasus
python work/test_layarawal.py      # menu, credits, set-up, instruksi
python work/test_mandiri.py        # membuktikan port tidak membaca rekaman
python work/gendocimg.py           # bangkitkan ulang gambar di dokumen
```

Uji-uji itu **menangkap sendiri** pembandingnya dengan menjalankan gim asli di emulator,
jadi tidak ada berkas rujukan yang harus dipercaya asal-usulnya. Hapus foldernya, dan ia
akan dibuat lagi.

⚠ Satu peringatan yang jujur: uji-uji ini menutupi apa yang **sudah** disapu. Dimensi
yang belum pernah diuji — misalnya tingkat *Master Builder* di semua mode — berstatus
*tidak diketahui*, bukan "hampir pasti benar". Empat kali di proyek ini, memperluas
cakupan ke data baru langsung memunculkan kesalahan di jalur kode yang sudah cocok.
