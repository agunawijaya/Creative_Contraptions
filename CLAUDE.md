# CLAUDE.md — Creative Contraptions (decompile + port)

> **Baca ini dulu sebelum mengerjakan apa pun.** File ini ikut folder proyek ke mana pun ia
> dipindah/di-rename, jadi konteks tidak hilang meski memory Claude Code (yang terikat path)
> tidak termuat. Terakhir diperbarui: 2026-07-30.

## ⭐ KALAU USER BILANG "LANJUTKAN" — BACA INI DULU

**Jalur yang sedang aktif: `src_c/` (rekonstruksi source C byte-identical).**
Jalur port Python sedang JEDA — jangan melanjutkannya kecuali user minta khusus.

Langkah pertama tiap sesi baru:
1. Baca **`src_c/README.md`** — 17 aturan kompiler MS C 1.04 yang mahal didapat.
   Tanpa ini akan mengulang kesalahan yang sudah dibayar.
2. Baca **`src_c/JOURNAL.md`** — KEPUTUSAN & alasannya, jalan buntu yang sebabnya
   sudah dipahami, dan pertanyaan yang masih menggantung untuk user.
3. Jalankan `pwsh src_c/build/buildall.ps1` lalu `python src_c/verify/verifyall.py`
   untuk status faktual, DAN `python src_c/verify/execmp.py` (satu-satunya alat
   yang melihat identitas simbol). Jangan percaya angka di dokumen, percaya alatnya.

Arsip percakapan mentah ada di folder memory Claude Code (`*.jsonl`, 9,3 MB).
Pakai HANYA kalau perlu menelusuri satu detail spesifik; jangan dibaca utuh dan
jangan dipakai sebagai sumber status. Path lengkapnya ada di `src_c/JOURNAL.md`.

**Jalur `src_c` SUDAH SELESAI (2026-08-01).** Tidak ada pekerjaan tersisa di
sana: `.EXE` hasil link identik dengan biner asli kecuali satu byte artefak
kompiler yang terbukti ditentukan lingkungan build, bukan sumber C.

Kalau user bilang "lanjutkan" tanpa konteks lain, TANYAKAN dulu — pilihannya:
- melanjutkan jalur **port Python** di `port/` yang sedang JEDA (rencana ada di
  §"Status port" di bawah), atau
- pekerjaan lain di `src_c` yang sifatnya perawatan (mis. menaikkan cakupan
  `symcheck`, atau mencoba mencocokkan byte terakhir dengan menyetel lingkungan
  build — nilainya kecil).

⚠ Sebelum menyentuh `src_c` lagi, WAJIB baca `src_c/README.md`. Dan sesudah
SETIAP link jalankan `python src_c/verify/execmp.py` — itu satu-satunya alat
yang melihat identitas simbol; perbandingan per-fungsi mem-wildcard slot
relokasi dan pernah menyembunyikan 24 byte yang salah simbol.

## Proyek ini apa

Membedah + mem-port game DOS **Creative Contraptions** (1985, Looking Glass Software / Bantam —
bukan Looking Glass Studios). Analisis reverse-engineering **sudah selesai**. Dua produk turunan berjalan
paralel: **port Python/pygame** di `port/` dan **rekonstruksi source C
byte-identical** di `src_c/`.

- Programmer asli: Jessie Ragsdale. Compiler asli: **Microsoft C V1.04** (= Lattice C yang
  di-rebrand Microsoft/Lifeboat; string literal `MS-C  V 1.04` ada di offset 0x200 biner
  ter-unpack). **Model memori = SMALL**, int 16-bit — lihat `ARCHITECTURE.md` §Model memori.
- **Kompiler aslinya SUDAH ADA & TERBUKTI COCOK** (2026-07-29): `tools/msc104/`
  (di-.gitignore, unduh ulang dari PCjs / Internet Archive). crt0 `C.OBJ` cocok byte-per-byte
  dgn biner game (116 byte, semua beda = slot relokasi). Wilayah ≥0x69d7 (9.881 byte)
  TERBUKTI kode pustaka `MC.LIB` — 23 modul cocok byte-per-byte, lihat
  `python src_c/verify/libmatch.py` → tak perlu direkonstruksi. Target rekonstruksi
  = **27.095 byte kode game** (<0x69d7), ±1.200 byte di antaranya assembly tulisan
  tangan. Detail: `DECOMPILE_PLAN.md` §Tahap 0 dan `src_c/README.md`.
- Bahasa target port: **Python** (pilihan user, sudah final).
- Aset asli dibaca **saat runtime** (GRAPH/MECHS/MISC/ANIMATE/CONTRAP) — tanpa re-encode.

## Aturan kerja (dari umpan balik user — jangan dilanggar)

1. **Bandingkan ke GROUND TRUTH, bukan output sendiri.** Game asli jalan di DOSBox-X/emulator
   Unicorn (`work/emu.py`). Semua kesalahan besar di masa lalu (palet salah, sprite salah,
   urutan bola salah) terjadi karena verifikasi terhadap asumsi sendiri.
2. **Jangan menerka koordinat/offset/warna/ukuran.** Ukur dari sprite atau dari kode ter-decompile.
   Tulis skrip analisa piksel untuk cari bbox eksak.
3. **Pisahkan "berjalan/ter-render" dari "COCOK dengan asli".** Jangan pernah klaim "sesuai"
   kalau yang diverifikasi baru "tidak error".
4. **Bukti VISUAL dulu** (PNG/GIF ter-zoom, side-by-side), baru penjelasan teknis. User meminta
   bukti, bukan klaim.
5. **Update dokumen MD di root tiap ada temuan** (`CODE_MAP.md`, `RESUME_EXACT.md`,
   `ARCHITECTURE.md`, `GAME_GUIDE.md`, `DECOMPILE_PLAN.md`) — bukan cuma memory.
6. **Konfirmasi dulu kalau ambigu**, sebelum mengimplementasi sesuatu yang besar.
7. **Uji lewat jalur user sungguhan** (jendela interaktif + keyboard), bukan hanya PNG headless.
8. Jalankan Claude Code **dari root proyek**, jangan dari subfolder (`work/`) — memory terpisah per path.

## Peta file

```
port/main.py            aplikasi utama: state machine TITLE→MENU→LEVEL→GOAL→PLAY→PLAYANIM
port/cc/cga.py          palet CGA-1 low-intensity bg-biru (EKSAK), framebuffer, scaling
port/cc/assets.py       decoder RLE 0xE4, arsip record, parser CONTRAP
port/cc/animvm.py       port VM animasi (parser opcode + interpolator parabola)
port/cc/text.py         teks 8×8
port/cc/draws/          daftar draw per goal/varian (dari capture emulator) — layar DESIGN
port/cc/anim/           frame animasi run ter-pack goalN_vV.dat + ballN_vV.json + reachN_vV.json
work/emu.py             emulator Unicorn + capture VRAM/blitter (SUMBER KEBENARAN)
work/                   skrip analisa, test_*.py, proof_*.py, bukti PNG/GIF
_ORIGINAL_READONLY/     backup aset asli — JANGAN diubah
tools/                  DOSBox-X, JDK 21, Ghidra 12.1.2, msc104 (MS C 1.04 + LINK 1.10),
                        masm (MASM 1.27 1984, untuk fungsi assembly)
src_c/                  rekonstruksi source C byte-identical
src_c/README.md         RULEBOOK: 17 aturan kompiler MS C 1.04 (baca sebelum menyentuh src_c)
src_c/JOURNAL.md        jurnal KEPUTUSAN + jalan buntu + pertanyaan terbuka
```

Dokumen root — ⚠ ketiganya ditulis untuk PEMBACA, bukan sebagai catatan kerja
(ditulis ulang 2026-08-01). Kalau menambah temuan, jaga nadanya:

| berkas | untuk siapa | isinya |
|---|---|---|
| `ARCHITECTURE.md` | orang yang BELAJAR pemrograman | bagaimana program 1985 dirancang, dan kenapa |
| `CODE_MAP.md` | orang yang BELAJAR membaca kode | peta kode + format data, per alamat |
| `GAME_GUIDE.md` | pemain / pembaca umum | brosur: mode, skenario, sejarah |

⚠ **Tiap gambar WAJIB punya paragraf "Penjelasan gambar."** tepat di bawahnya —
itu permintaan eksplisit user. Diagramnya dibangkitkan `python work/gendocimg.py`
(angkanya dibaca dari data nyata, jadi tidak bisa basi diam-diam) dan disimpan di
`work/doc/`. Periksa dengan:
`python -c "import re,os;[print(p,os.path.exists(p)) for _,p in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)',open('CODE_MAP.md',encoding='utf-8').read())]"`

Dokumen kerja (boleh berupa catatan mentah): `DECOMPILE_PLAN.md`,
`TARGET_LANGUAGE.md`, `RESUME_EXACT.md`, `src_c/README.md`, `src_c/JOURNAL.md`.
Catatan: bagian "Belum" di `port/README.md` **sudah basi** — percayai `CODE_MAP.md`.

## Menjalankan

```
run_original.bat               # GAME ASLI di DOSBox-X, scaler 5x -> 1600x1200
run_port.bat                   # HASIL PORT (impor aset otomatis kalau belum ada)
python port/import_assets.py   # bikin bundel aset port/cc/data/ (sekali saja)
```
**Port MANDIRI**: `find_data_dir()` memakai `port/cc/data/` lebih dulu, folder game asli
hanya cadangan saat pengembangan. Bundel di-.gitignore — repo tidak mendistribusikan game.
⚠️ Build DOSBox-X di `tools/` **mengabaikan opsi `-c`** — perintah mount HARUS lewat
`[autoexec]`. `run_original.bat` menyalin `run_original.conf` ke `%TEMP%` lalu menambahkan
`[autoexec]` berisi path dari `%~dp0` (jadi kebal rename folder).

```
python port/main.py            # jendela; ESC/Q keluar
python port/main.py --shots    # render tiap layar ke PNG (headless)
python work/test_allgoals.py   # regresi: semua goal × varian bisa dimenangkan
python work/test_nav.py        # regresi navigasi menu
```
Env emulator: `VARIANT=n VCAP=1 python work/emu.py <goal> <mode>` → capture VRAM + jalur bola.

Rekonstruksi source C (produk ke-2, folder `src_c/`):
```
pwsh src_c/build/buildall.ps1   # semua .c -> .OBJ, lalu semua .asm -> .OBJ (MASM)
pwsh src_c/build/link.ps1       # -> src_c/out/CONTRAP.EXE + CONTRAP.MAP
python src_c/verify/verifyall.py   # tabel status per fungsi + segmen DATA
python src_c/verify/symcheck.py    # WAJIB: identitas simbol (call + global)
```

## Status decompile→source — ✅ SELESAI (2026-08-01)

**`.EXE` hasil link IDENTIK dengan biner asli**, kecuali SATU byte artefak
kompiler. Periksa kapan saja:

```
pwsh src_c/build/buildall.ps1 ; pwsh src_c/build/link.ps1
python src_c/verify/execmp.py -v      # <- SATU-SATUNYA alat yang melihat IDENTITAS SIMBOL
python src_c/verify/verifyall.py      # tabel per fungsi + segmen DATA
python src_c/verify/symcheck.py       # identitas simbol (call + global)
```

- muatan 46.532 byte = 46.532 byte, `cs:ip`/`ss:sp`/`nreloc` sama, **1 byte beda**
- **83/83 fungsi COCOK**, kode 26.964/26.965, DATA 9.556/9.556
- putaran penuh `emu.py`: **14/14 tangkapan byte-identik**, log identik baris per
  baris, TANPA pemetaan alamat apa pun

Satu byte itu `load+134` (0x5485): byte tinggi immediate sampah `add ax,9449h`
dari perbandingan `p == -1L` yang rusak. Nilainya alamat heap internal kompiler.
Nama berkas sumber menggesernya (0x34..0x3a) tapi tidak pernah mencapai 0x94 —
jadi ia ditentukan tata letak memori mesin yang MENGOMPILASI, bukan sumber C.

⚠⚠ **"COCOK byte-per-byte" TIDAK melihat identitas simbol.** `verifyall`/
`aligncmp` mem-WILDCARD slot relokasi, jadi kode yang menunjuk simbol SALAH
tetap dilaporkan COCOK. `execmp.py` menemukan 24 byte semacam itu di `main_`,
`animvm`, `drawball`, dan `loadcon` — semuanya berstatus "COCOK". **Jalankan
`execmp.py` setiap kali sesudah link.**

Aturan & jebakan lengkap: **`src_c/README.md`**.

**Sweep perilaku LENGKAP**: 6 goal × 4 mode = **24 skenario**, semuanya 14/14
tangkapan byte-identik dan log identik. Tanpa pemetaan alamat.

**Bukti dekompilasi tanpa menjalankan program**: `python work/genscreens.py`
menyusun layar Fill in Mechanisms dari berkas aset saja (CONTRAP+GRAPH+MECHS+MISC)
— 20 PNG untuk goal 1..6 di `work/screens_gen/`, lembar kontak
`work/fillmech_semua_varian.png`. `--verifikasi`: **197/197 blit** yang ditangkap
emulator terjelaskan. Aturan penempatan lengkap ada di `CODE_MAP.md`.

## Status port (per 2026-07-21)

**Selesai & terbukti:**
- Unpack PKLITE, decompile 144 fungsi, format aset & CONTRAP tervalidasi.
- Render 6 contraption **100% pixel-match** vs game asli.
- **"Fisika bola" = VM animasi ber-skrip** (`FUN_1000_18db`, 17 opcode, tabel `CS:0x23D4`,
   skrip dari file ANIMATE) — BUKAN physics engine. Parser 100%, interpolator parabola
   `2823` **42/42 eksak**.
- **Ke-4 mode jalan**: Review Mechanisms (ensiklopedia + demo goal 7), Fill in Mechanisms
   (multi-varian acak), Fill in Zany Objects, Contraption Mix Up (timer + bonus).
- Palet part dikocok, skoring, navigasi sesuai hierarki asli (selesai/ESC → pilihan GOAL,
   bukan menu depan).
- **Layar DIAM sudah PIXEL-IDENTIK dgn game asli** (2026-08-01): 7 layar (goal 1..6 + judul
   goal 128) = **448.000/448.000 piksel** vs tangkapan VRAM emulator, diukur dari dalam port
   lewat pygame Surface. Varian part dipilih lewat RNG yang sama (`port/cc/core/pick.py`).
   Layar judul memakai JALUR KODE YANG SAMA dgn layar design, hanya `sub = 0x80`.
- Animasi judul rakitan tangan (`build_title_anim`) DIBUANG — tak satu pun pikselnya terbukti.

- **ANIMASI dibangkitkan sendiri** (2026-08-01): mesin `animvm()` di
  `port/cc/core/vm.py` menjalankan skrip dari berkas aset. Terukur vs tangkapan VRAM
  emulator: **381/402 frame byte-identik, 99,9988% piksel**. Goal 4, 5, 6 dan layar
  judul **100% frame**. Judul "CREATIVE CONTRAPTIONS" ternyata digambar opcode `0x11`
  DI DALAM skrip animasi, bukan oleh layar statis.
- **Port TIDAK lagi membaca rekaman.** `port/cc/anim/*.dat` dan `port/cc/draws/*.json`
  tidak dipakai sama sekali — layar, animasi, slot, palet, jalur bola, dan "reach"
  semuanya dari `port/cc/core/`. Keduanya kini hanya PEMBANDING.

- **Bilah status, skor, timer, petunjuk, dan pesan akhir goal SUDAH ADA** (2026-08-01):
  `port/cc/core/hud.py` = padanan `showsc`/`timedrw`/`showhint`/`prompts`/`pickmax`
  (+ `timebar`). Teks, koordinat, dan percabangannya dari DGROUP dan `src_c`, bukan karangan.
  Diuji `python work/test_hud.py`.
- **SKORING DIPERBAIKI** — port lama memberi 10000/5000/2500 ke TIAP kotak dan menghitung
  skor di semua mode. Gim asli: **satu penilaian per kontraption** dari `zcnt`, dan **hanya
  di mode 4** (Contraption Mix Up); Fill in Mechanisms dan Fill in Zany Objects memang
  latihan tanpa skor. Bonus waktu `tx * 100` (sisa waktu, Master, goal 6), bonus bola
  `(bola-1) * 2500`, bonus Master `cur2 * 1000`.
- ⭐ **Skor disimpan DIBAGI SEPULUH**: format `" %7ld0"` menempelkan nol harfiah, jadi
  `sclo += 10000` terbaca "100000". Dan `sclo` itu satu `long` di @0x730 — `schi` @0x732
  hanyalah nama paruh atasnya (terbukti dari `showsc(sclo, 2)` yang memberi DUA argumen ke
  fungsi bertiga parameter).

- **Layar menu, level, pemilih goal, dan Review dari TABEL DGROUP** (2026-08-01):
  `port/cc/core/menu.py` (`mtabmn` @0x1D48, `mtablv` @0x1B74, `menu` @0x1C28) dan
  `resensi.py`. Menu utama **64.000/64.000 piksel**, layar Review **64.000/64.000**
  vs tangkapan VRAM emulator. Strip pemilih part: `palet.py` (`drawpal()`).
- ⚠ **Angka 448.000/448.000 itu layar ATTRACT**, bukan layar permainan — emulator
  menambal nomor goal pada `loadcon` PERTAMA, yang terjadi saat layar judul. Layar
  Fill in Mechanisms sungguhan: pita atas 2.560/2.560 dan pita bawah 12.800/12.800;
  arenanya belum cocok karena keadaan RNG saat itu bukan seed 0.

**Berikutnya untuk jalur PORT:**
1. **21 frame animasi** (goal 1, 2, 3) belum byte-identik. Bedanya kecil dan terpusat;
   record dan posisinya sudah terbukti BENAR. Yang belum diturunkan adalah
   `prep`/`blend`/`putmsk`/`draw` — interaksi hapus-bola dengan blit yang datang
   sesudahnya. ⚠ **Enam percobaan di sumbu itu sudah gagal**; hipotesis "salinan latar
   basi" bahkan menurunkan hasil 381/402 → 57/402. Baca catatan panjang di
   `port/cc/core/adegan.py` sebelum mencoba lagi.
2. Suara PC-speaker (op `0x04` sudah diparse, belum dibunyikan). Nada juga dipakai
   `showsc` saat kedip dan `timedrw` saat bilah timer terisi di awal.
3. Sisa pemakaian tangkapan, keduanya data ANTARMUKA bukan render kontraption:
   `cc/anim/review_layout.json` (tata letak Review Mechanisms) dan `cc/anim/icons/`.

## Jebakan yang sudah pernah menggigit (jangan ulangi)

- **Sprite di-render OPAQUE, bukan colorkey cyan.** Blitter asli `672f` menulis semua piksel;
  cyan = warna latar, bukan transparansi. Colorkey bikin piksel cyan di dalam sprite hilang.
- ~~**Indeks varian `draws_goalN_vI.json` TIDAK sejajar dengan `goalN_vI.dat`**~~ — jebakan
  ini SUDAH TIDAK ADA. `_match_anim()` (yang mencocokkan animasi ke layar design lewat isi
  frame-0) sudah dibuang: adegan dan animasi kini lahir dari data yang sama, oleh undian
  yang sama, jadi tidak ada yang perlu dicocokkan. Bug "layar design ≠ layar run" tidak
  bisa terjadi lagi **secara konstruksi**, bukan karena diperbaiki.
- **ALAT UKUR BISA MEMBATASI TEMUAN.** Jumlah varian sempat diambil dari `len(draws_var[gid])`
  — yaitu dari berapa banyak berkas TANGKAPAN yang kebetulan ada, sehingga varian yang belum
  sempat direkam tak pernah terpilih. Yang membuatnya sulit terlihat: `work/test_allgoals.py`
  menghitung varian dengan cara yang SAMA, jadi tesnya ikut membatasi diri dan tak akan pernah
  melaporkannya. Curigai tes yang memakai sumber data yang sama dengan kode yang diujinya.
- **ANGKA YANG MEMBAIK BUKAN BUKTI PENJELASANNYA BENAR.** Penyelarasan frame "(2,1) karena
  halaman ganda" sempat memberi 101/135 dengan alasan yang keliru; urutan gambar yang benar
  memberi 119/135 tanpa pergeseran apa pun.
- **NAMA GLOBAL ADALAH HIPOTESIS, BUKAN FAKTA.** Empat nama terbukti salah, dan tiap kali
  yang membongkarnya adalah PEMAKAIANNYA, bukan tampilannya:
  `bally`(@0x25e) sebenarnya **X**, `ballx`(@0x260) sebenarnya **Y**, `goal`(@0x718)
  sebenarnya **jumlah bola**, `mode_`/`seed` sebenarnya **pegangan berkas**.
  Catatan lama "0x260/0x25e = koordinat LOGIS, drawer 5e3b menerapkan transform" SALAH —
  transform itu tidak ada; keduanya koordinat layar langsung. Lihat CODE_MAP.md §8b.
- **Urutan slot CONTRAP ≠ urutan draw** — cocokkan by-POSISI, bukan by-indeks.
- Emulator merender sprite (`672f`) tapi **tidak** teks font (`6453`/`381a`) → untuk layout
  teks, ekstrak tabel `381a`/`3769` dari DGROUP.
- Ekstraksi sub-sprite dari latar berwarna membawa piksel latar → filter hanya piksel objek;
  hapus base (fill cyan) sebelum overlay reaksi.
