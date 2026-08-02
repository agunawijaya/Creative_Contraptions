# CLAUDE.md — Creative Contraptions (decompile + port)

> **Baca ini dulu sebelum mengerjakan apa pun.** File ini ikut folder proyek ke mana pun ia
> dipindah/di-rename, jadi konteks tidak hilang meski memory Claude Code (yang terikat path)
> tidak termuat. Terakhir diperbarui: 2026-08-02.

## ⭐ KALAU USER BILANG "LANJUTKAN" — BACA INI DULU

**KEDUA JALUR SUDAH SELESAI (2026-08-02).**

- `src_c/` — `.EXE` hasil link identik dgn biner asli kecuali satu byte artefak
  kompiler yang terbukti ditentukan lingkungan build, bukan sumber C.
- `port/` — seluruh bagian yang bisa diadu piksel sudah diadu; tidak ada lagi
  yang berstatus "argumennya kuat tapi belum diukur". Angkanya di §Status port.

Kalau user minta melanjutkan, TANYAKAN dulu apa sasarannya. Yang tersisa hanya
perawatan dan perluasan cakupan ke dimensi yang belum pernah disapu. Semua
dimensi yang pernah kami sebut sudah disapu; `test_play.py` kini **44 kasus**
(6 goal x 2 mode x 2 tingkat, 6 ronde Mix Up x 2 tingkat, dan **jalur pemain
untuk ketiga mode x kedua tingkat**).

⚠ Pengalaman 2026-08-02: **ENAM** celah cakupan ditutup dan **keenamnya**
memunculkan kesalahan — jangan menganggap dimensi yang belum diuji "hampir
pasti benar". Yang kelima (tingkat Master Builder) bahkan memunculkan artefak
gim 1985 yang belum pernah terlihat siapa pun: huruf liar di tengah arena
karena `hintmark()` membaca `postab` satu entri di luar jangkauan. Lihat
`CODE_MAP.md` §3.1c.

### Repo & cara kerja git

Remote SUDAH ada: **`github.com/agunawijaya/Creative_Contraptions`**, **private**.
Kerja terakhir (2026-08-02) ada di commit `62c1282`, dan `main` sinkron dgn
`origin/main`.

⚠ **Harapan user: tiap kemajuan nyata = commit + push + dokumen root diperbarui,
dalam satu tarikan.** Jangan menumpuk pekerjaan tanpa commit, dan jangan commit
tanpa push. Berkas gim TIDAK PERNAH ikut (sudah di-.gitignore) — periksa dgn
`git ls-files | grep -icE "_ORIGINAL_READONLY|\.exe$|\.zip$"` yang harus 0.

### Langkah pertama tiap sesi baru

Kerja TERAKHIR ada di jalur **port** dan dokumen. Mulai dari situ kecuali user
menyebut src_c:

1. Jalankan seluruh `work/test_*.py` (**23 berkas**) untuk status faktual jalur
   port. Angka di dokumen bisa basi; alatnya tidak.
2. Baca §"Status port" di bawah, lalu `port/README.md` §"Keadaan terukur".
3. Kalau menyentuh **`src_c`**: WAJIB baca `src_c/README.md` (17 aturan kompiler
   MS C 1.04) dan `src_c/JOURNAL.md` lebih dulu; sesudah SETIAP link jalankan
   `python src_c/verify/execmp.py`.
4. Dokumen untuk PEMBACA (README, ARCHITECTURE, CODE_MAP, PORT_*) — jaga nadanya,
   dan tiap gambar/diagram wajib punya paragraf "Penjelasan gambar."

Arsip percakapan mentah ada di folder memory Claude Code (`*.jsonl`, 9,3 MB).
Pakai HANYA kalau perlu menelusuri satu detail spesifik; jangan dibaca utuh dan
jangan dipakai sebagai sumber status. Path lengkapnya ada di `src_c/JOURNAL.md`.

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
| `README.md` | pengunjung repo | pintu depan: dua produk, bukti, cara jalan, kebijakan aset |
| `ARCHITECTURE.md` | orang yang BELAJAR pemrograman | bagaimana program 1985 dirancang, dan kenapa |
| `CODE_MAP.md` | orang yang BELAJAR membaca kode | peta kode + format data, per alamat |
| `PORT_ARCHITECTURE.md` | orang yang BELAJAR pemrograman | bagaimana yang lama diterjemahkan jadi Python, dan apa yang SENGAJA tidak diperbaiki |
| `PORT_CODE_MAP.md` | orang yang BELAJAR membaca kode | fungsi 1985 ↔ modul port, per alamat |
| `GAME_GUIDE.md` | pemain / pembaca umum | brosur: mode, skenario, sejarah |

Urutan baca yang disarankan untuk pemula: `ARCHITECTURE` → `PORT_ARCHITECTURE` →
`CODE_MAP` → `PORT_CODE_MAP`.

⚠ **Tiap gambar WAJIB punya paragraf "Penjelasan gambar."** tepat di bawahnya —
itu permintaan eksplisit user. Berlaku juga untuk **diagram Mermaid** (blok
```` ```mermaid ````), yang dirender GitHub secara bawaan dan dipakai di
`README.md`, `PORT_ARCHITECTURE.md`, dan `PORT_CODE_MAP.md`.
⚠ Tidak ada perender Mermaid di mesin ini, jadi sintaksnya TIDAK bisa diuji
lokal — periksa dengan mata, dan hati-hati pada dua hal yang pernah salah:
`end` sebagai id node (memutus `subgraph`), dan ARAH `flowchart`
(dgn panah "bergantung pada", `TD` menaruh lapis dasar di BAWAH; `BT`
membalikkannya dan pernah membuat keterangan gambar bertentangan dgn
gambarnya). Diagramnya dibangkitkan `python work/gendocimg.py`
(angkanya dibaca dari data nyata, jadi tidak bisa basi diam-diam) dan disimpan di
`work/doc/`. ⚠ `doc_sisi_sisi.png` (asli vs port vs peta beda) butuh tangkapan
`work/playseq/` — jalankan `python work/test_play.py` dulu, kalau tidak langkahnya
dilewati dan PNG lama dibiarkan. Periksa dengan:
`python -c "import re,os;[print(p,os.path.exists(p)) for _,p in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)',open('CODE_MAP.md',encoding='utf-8').read())]"`

Dokumen kerja (boleh berupa catatan mentah): `DECOMPILE_PLAN.md`,
`TARGET_LANGUAGE.md`, `RESUME_EXACT.md`, `src_c/README.md`, `src_c/JOURNAL.md`.
`port/README.md` sudah disegarkan (§"Keadaan terukur"); `RESUME_EXACT.md` ditandai
DOKUMEN SEJARAH — isinya catatan kerja dari saat tujuannya masih terbuka.

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
python work/test_intro.py      # pembuka animvm (jam pasir + bilah bola)
python work/test_tabmenu.py    # 12 tabel layar vs sumber src_c byte-exact
python work/test_layarawal.py  # credits/askopts/3 layar instruksi vs VRAM gim
python work/test_suara.py      # frekuensi PIT + sapuan mode 1
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

- ⭐ **ANIMASI 100% IDENTIK** (2026-08-01): mesin `animvm()` di `port/cc/core/vm.py`
  menjalankan skrip dari berkas aset. Terukur vs tangkapan VRAM emulator, animasi
  PENUH ketujuh layar dari frame pertama sampai habis:
  **1.565/1.565 frame byte-identik, 100.160.000/100.160.000 piksel (100,000000%)** —
  KESEPULUH varian CONTRAP, bukan satu per goal.
  Uji mandiri (membuat tangkapannya sendiri): `python work/test_anim_vs_gim.py`.
  Rinciannya: goal 1 136, goal 2 71, goal 3 88, goal 4 79, goal 5 66, goal 6 95,
  layar judul 675 frame.
  Tiga hal yang membuka sisanya, dan ketiganya DIUKUR bukan dibaca:
  - opcode `0x05` = **hapus bola** (`putmsk(buf9c5, page2)` dgn mask nol), bukan no-op;
  - `end` (0xFF) = akhir skrip **satu part**, bukan akhir animasi — gelung luar
    `animvm.c` memajukan ke part berikutnya;
  - opcode `0x11` memanggil `bounce()` LEBIH DULU: bola memantul enam kali ke tepi
    layar acak, teks "CREATIVE CONTRAPTIONS" baru muncul sesudahnya. Undiannya cocok
    karena seed port sesudah pemilihan part = `0xa6b8`, sama dgn @0x71a di emulator.
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

- **Strip palet `drawpal()` 7.680/7.680 piksel** (2026-08-01). Urutannya `rowtab` @0x870
  = `[100,110,115,120,130,132,135,141,150]` — perhatikan **141** untuk Lever, bukan 140.
  ⚠ Sempat dikira terhalang emulator; penyebabnya sepele: tangkapan diambil di alamat
  MASUK `drawpal`, sehingga selalu memperlihatkan keadaan SEBELUM ia menggambar. Di
  alamat RET (0x3C4E) isinya langsung muncul. Alat diagnosisnya di `work/emu.py`:
  `CC_VSWORD` (word DGROUP per frame), `CC_VSMEM` (byte dari alamat tetap),
  `CC_VSPTR` (baca word sebagai alamat lalu buang isinya), `CC_MAXINSN`, `CC_OBSKEYS`.
- **Strip di mode ISIAN juga terukur** (2026-08-01). "Terhalang emulator" untuk KEDUA
  kalinya berarti "terhalang harness kita sendiri": `work/emu.py` mem-bypass gelung
  penempatan part (`hook_2e90`) dan `drawpal()` hidup di dalamnya. Saklar baru
  `CC_NOSKIP=1` mematikan bypass-nya. Hasil: aturan jendela-geser + urutan-dibalik +
  isian hitam berlaku sama di mode ISIAN, pada posisi piksel yang sama.
- ⭐ **BERAPA pilihan yang ditawarkan tergantung MODE** (2026-08-01). `nmech` @0x3ac
  terukur 3, 4, 3 untuk goal 1, 2, 4 dan **13** untuk Mix Up — jumlah JENIS yang
  DIBUTUHKAN kontraption itu, bukan sembilan kategori seperti yang selalu diberikan
  port lama. Sebabnya di `mkpal()` @0x3909:
  `if (lvl3 != 1 || base[i*0xc] == tab[j*3+2])`, dan `lvl3 == 1` di mode 1/2/3
  sedangkan `lvl3 == 3` di mode 4. Jadi Fill in Mechanisms hanya menawarkan part yang
  memang dipakai — soalnya "taruh di kotak yang benar" — sementara Contraption Mix Up
  menawarkan seluruh daftar (13 = 15 id record MECHS sesudah 140/141/150 diciutkan
  jadi satu oleh dedup), dan itulah yang membuatnya lebih sulit.
  `mkpal()` kini ditiru utuh di `pick.palet_mekanisme()`, dan pencocokan jawaban
  memakai id record EKSAK seperti gim (`ord1[c1] != rec1[3*c1+2]`), bukan kategori.
- ⭐ **STRIP PALET terukur di KEDUA mode**: **48.384/48.384 piksel**
  (`python work/test_palet.py`). ⚠ `idtab[]` @0x2ea mengindeks `base`, dan `base`
  berbeda per mode — `loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`: mode isian 6
  record (disaring+dipadatkan), Mix Up 30 (direktori penuh).
- ⭐ **CONTRAPTION MIX UP = RENTETAN 6 KONTRAPTION** (2026-08-01), bukan satu yang
  dipilih lewat layar goal. `main_.c` case 4 tidak pernah memanggil `goalmenu()`; ia
  memasang `sub = 0; goal = 6; pickmax();` lalu tiap putaran `sub++`. Master Builder =
  enam ronde lalu keluar; Apprentice tak berujung (`goal++` dan `goal--` saling
  meniadakan). Skor terkumpul lintas ronde. Diuji `python work/test_mixup.py`.
- **`hintmark()` ADA** (2026-08-01): `hud.Petunjuk`. Penanda huruf pindah ke slot acak
  tiap pewaktu habis; warna 0 = petunjuk sungguhan dan menyalakan `mflag` (syarat bonus
  bola), warna 2 = penanda biasa. `count` menyusut tiap `pickmax()`, jadi petunjuknya
  makin sempit seiring permainan.
- **Layar menu, level, pemilih goal, dan Review dari TABEL DGROUP** (2026-08-01):
  `port/cc/core/menu.py` (`mtabmn` @0x1D48, `mtablv` @0x1B74, `menu` @0x1C28) dan
  `resensi.py`. Menu utama **64.000/64.000 piksel**, layar Review **64.000/64.000**
  vs tangkapan VRAM emulator. Strip pemilih part: `palet.py` (`drawpal()`).
- ⚠ **Angka 448.000/448.000 itu layar ATTRACT**, bukan layar permainan — emulator
  menambal nomor goal pada `loadcon` PERTAMA, yang terjadi saat layar judul.
- ⭐ **KETIGA MODE BERMAIN 64.000/64.000 piksel** (2026-08-02) — SELURUH layar
  termasuk arena, untuk Fill in Mechanisms, Fill in Zany, DAN Contraption Mix
  Up; Fill in Mechanisms juga diukur lewat jalur pemain (`main.Game` + `key()`).
  `python work/test_play.py`. Aturannya berbeda tiap mode: slot mekanisme
  kosong = petak abu; slot zany kosong TIDAK menggambar apa pun (kecuali yang
  TERAKHIR — itu gambar hasil goal); di Mix Up keduanya tetap digambar dan yang
  "kosong" adalah slot BERTANDA dgn sprite pengganti (id >= 0x80).
- ⭐ **`prompts()` dan `hintmark()` TERUKUR** (2026-08-02):
  `python work/test_prompts.py`. prompts diadu MASUK-vs-RET, 64.000/64.000
  untuk goal 1 dan 6. hintmark butuh saklar baru `CC_LEVEL=2` — ia mati total
  di level 1, jadi selama ini tak terjangkau. Dua nilai awalnya ternyata salah
  di port: `lvl6` mulai dari `nmax` (bukan 0) dan `range` DIACAK tiap
  kontraption (`tx - (rnd(200)*0x17/199 + 2)`), bukan dipatok `0x140 - 0x14`.
- ⭐ **`autofill()` DAN BUNYI KLIK MENU** (2026-08-02), dua perilaku yang lama
  tidak ada sama sekali:
  - `autofill()` @0x5954 mengisikan jawaban benar untuk slot yang pencacah
    gagalnya `>= 2`, dan `main_.c` memanggilnya HANYA di Apprentice
    (`if (lvl == 1)`). Tanpa itu pemain pemula bisa tersangkut selamanya.
  - `tone2()` @0x3734 dipanggil `runmenu()` tiap pilihan diterima — arpeggio
    tiga not (1048, 1176, 1320 Hz) dari @0x1DDB. Port lama diam total di menu.
  Diuji `python work/test_bantuan.py`.
- ⭐ **URUTAN PEMBUKA LENGKAP** (2026-08-02). `main_.c` sesudah animasi judul:
  `getkey()` → `credits()` → `askopts()` → `sndini()` → **20 undian pemanasan
  `rnd(1)`** → gelung utama. Port lama melompat dari judul LANGSUNG ke menu,
  jadi dua layar hilang dan rantai RNG-nya bergeser 20 undian.
- ⭐ **SUARA TERUKUR vs GIM** (2026-08-02): pembagi PIT yang benar-benar
  ditulis gim ke port 0x42 → **500, 0, 500, 0, ..., 630, 0, 749** Hz, dan
  dekode port dari DGROUP @0x978 memberi urutan yang SAMA PERSIS termasuk
  keheningannya. Ini yang membuktikan angka skrip = FREKUENSI, bukan pembagi
  (kalau pembagi, 500 akan terdengar sebagai 2.386 Hz).
  Butuh `CC_SNDISR=1`: bunyi digerakkan ISR INT 1Ch yang tidak dijalankan
  emulator, jadi port speaker SUNYI berapa lama pun — saklar itu memanggil
  `sndisr` @0x670E sendiri dari `vbwait`.
- ⭐ **LAYAR INSTRUKSI ADA** (2026-08-02): `menu9`/`menu11`/`menu12`
  (tabel DGROUP @0x1634 9 entri, @0x1796 11, @0x18f8 12). Gim menampilkannya
  SEKALI per mode (`if (k == 1)` di main_.c), dan port lama TIDAK PUNYA
  layar ini sama sekali — pemain tak pernah diberi tahu aturan modenya.
  Alur sekarang: MENU → LEVEL → **INSTRUKSI** → GOAL (atau langsung main di
  Mix Up). ⚠ Byte 0x80..0x83 di dalam stringnya GLYPH PANAH, bukan huruf.
  ⚠ `k = 1` ada di PUNCAK gelung utama, jadi layar itu muncul TIAP KALI pemain
  lewat menu utama — bukan sekali selamanya.
- ⭐ **LAYAR JUDUL sempat TERPOTONG di frame 400** (2026-08-02). `main.py`
  memanggil `adegan.frames()` tanpa `maks`, jadi memakai bawaannya 400 —
  padahal layar judul 675 frame. Uji per-modul tidak melihatnya karena ia
  memakai batasnya sendiri. Sekarang `Game.ANIM_MAKS = 1200`, dan
  `test_anim_vs_gim.py` menambah tahap **jalur pemain**: 675/675.
- ⭐ **PART SALAH BARU KETAHUAN SAAT DIJALANKAN** (2026-08-02). Port dulu
  MENOLAK part yang salah di tempat dan langsung bilang "does not work". Gim
  menerima apa pun yang ditaruh; satu-satunya tempat yang memeriksa adalah
  `animvm()` (`if (ord1[c1] != rec1[3*c1+2]) { zcnt++; printf(msgmech); }`) —
  tidak ada pemeriksaan di `pickloop()`/`review()` sama sekali. Jadi seluruh
  ketegangan mode ini hilang di port lama. `zcnt` ikut pindah ke saat
  dijalankan, karena `animvm` yang menaikkannya.
- ⭐ **SEMUA TEKS ANTARMUKA dari DGROUP** (2026-08-02). Port mengarang sembilan
  kalimat; tak satu pun ada di gim. Dan di gim baris pesan itu KOSONG saat
  bermain. Yang benar mis. `'       Mechanism %c does not work.'` @0x9dd —
  tujuh spasi depannya bagian dari string, dan itulah yang menempatkannya.
  Empat hal
  yang ternyata karangan port dan sekarang dari gim:
  `drawslot()` (slot kosong = PETAK PENUH warna 3, bukan kotak bergaris berisi
  huruf), `drawbox()` (sorotan EMPAT garis XOR warna 3), baris pesan (di baris
  teks cyan `fillrect(0x10,0xc0,0x12f,199,1)`, bukan di pita atas), dan pojok
  kanan pita atas yang menampung SKOR **atau** nama goal menurut `f171f()` —
  port lama selalu menggambar skor sehingga "Up and At 'Em" jadi "00' Em".
  Arenanya belum diadu langsung karena keadaan RNG saat itu bukan seed 0.

**Berikutnya untuk jalur PORT:**
1. ~~Frame animasi yang belum byte-identik~~ — **SELESAI**: 1.565/1.565 frame (10 varian),
   100,000000% piksel (`python work/test_anim_vs_gim.py`). Catatan panjang tentang
   sembilan percobaan yang gagal tetap disimpan di `port/cc/core/adegan.py`: yang
   akhirnya membuka semuanya adalah MEREKAM (`CC_TRACEWR`) lalu MENYAPU kombinasi
   secara terukur, bukan menafsirkan assembly.
2. ~~Suara PC-speaker~~ — **SELESAI**: `port/cc/core/bunyi.py`. Angka di skrip adalah
   **frekuensi dalam Hz** (dari `1193182 / CX` di `snd2.asm`), bukan pembagi PIT.
   Tiap not 3 byte: `u16 frekuensi + u8 durasi` (tik INT 1Ch, ~18,2/detik), diakhiri
   `FFFF`; mode 2 sekali jalan, mode 3 BERULANG, mode 1 sapuan tiga word.
   Diuji `python work/test_bunyi.py`. 117 not terdekode dari skrip goal 1.
3. ~~Layar yang belum ada di port~~ — **SELESAI**. `credits()` @0x312A dan
   `askopts()` @0x31DA sudah dipasang, dan bersamanya URUTAN PEMBUKA yang
   benar (lihat di bawah).
4. ~~Menu GOAL belum diadu piksel~~ — **SELESAI**: **64.000/64.000**, bersama
   menu LEVEL dan layar CREDITS tahap 0 (ketiganya lewat `setsel()` yang sama). Penghalangnya jebakan LAMA yang terulang: tangkapan diambil di
   alamat MASUK `setsel`, jadi yang terlihat layar SEBELUMNYA. Di RET (0x3819)
   keduanya langsung muncul. Butuh juga `CC_NOMENUSTUB=1`.
5. ~~Suara belum diadu dgn gim~~ — **SELESAI**: `python work/test_suara.py`.

4. ~~Strip palet di mode Mix Up~~ — **SELESAI**: `python work/test_palet.py`,
   **48.384/48.384 piksel** di KEDUA mode. Yang menghalanginya bukan `pickvar`
   melainkan urutan tombol OBSERVE bawaan yang diakhiri ESC.
5. ~~Antarmuka bermain port karangan sendiri~~ — **SELESAI**:
   `python work/test_play.py`, **64.000/64.000 piksel SELURUH LAYAR**, dan
   diukur DUA kali: lewat modul inti DAN lewat jalur pemain sungguhan
   (`main.Game` + `key()`). `drawslot()`/`drawbox()` kini di
   `port/cc/core/render.py`.
6. ~~Arena layar bermain belum diadu langsung~~ — **SELESAI**, termasuk arena
   (48.640/48.640). Penghalangnya bukan emulator melainkan model port:
   `loadcon.c` mengundi varian dgn `do { pick = rnd(cnt)+first; } while
   (lastgoal == sub && cnt >= 2 && pick == lastvar)`, dan `susun()` tidak
   memodelkan gelung itu — pengulangan MEMAJUKAN seed satu undian lagi
   sehingga seluruh pemilihan part sesudahnya bergeser.
   ⚠ `VARIANT=` TIDAK bisa dipakai sebagai jalan pintas: hook-nya memaksa
   SEMUA `rnd()` di dalam `loadcon` sehingga gelung do/while itu tak berujung
   (gejalanya "0 frame"). Yang benar: BACA seed @0x71a, lastgoal @0x1e2e, dan
   lastvar @0x1e30 dari memori gim.
7. ~~Pesan DALAM permainan~~ — **TERUKUR** (2026-08-02), termasuk barisnya.
   Yang dulu saya sebut "tidak bisa diukur" ternyata terhalang SATU hal di
   harness sendiri: `animvm()` dibuka gelung "jam pasir"
   `for(;;) { waitn(0x10); ...; if (ticks <= 0) break; }`, dan `ticks` dihitung
   mundur ISR timer yang tidak berjalan di emulator — jadi eksekusi berhenti
   jauh sebelum sampai ke `printf`. Terlihat sebagai 2,1 juta penulisan yang
   SEMUANYA di offset kode 0x18db..0x19a1.
   Saklar `CC_NOWAIT=1` menol-kan `ticks` di stub `waitn()`. ⚠ Sekadar
   mengembalikan `waitn` seketika TIDAK cukup — gelungnya cuma berputar lebih
   cepat; yang menghentikannya `ticks`, bukan kembalinya `waitn`.
   Sesudah itu `CC_TRACEDOS=1` merekam **INT 10h AH=02h: set kursor ke
   (baris 22, kolom 0), 11 kali** — dan `f66fd` @0x66fd, yang dipanggil
   `animvm.c:219` sebagai `f66fd(0x16, 0)` di puncak gelung per-slot, juga
   terpanggil tepat 11 kali (= 11 slot). Jadi baris pesannya **y = 176, x = 0**,
   dan tujuh spasi depan `msgmech` menggeser katanya ke x = 56.
   Port dibetulkan dari y = 192 ke y = 176.
   ⭐ WARNANYA JUGA TERUKUR, dan ternyata **3** (dugaan pertama 2 salah).
   Penghalang kelima juga harness sendiri: `hook_mechmatch`/`hook_zanymatch`
   MEMAKSA IP melompat ke jalur "cocok", jadi cabang yang memuat `printf`
   dilewati tanpa syarat — berapa kali pun datanya dipoke. `CC_SALAH=1`
   sekarang mematikan paksaan itu, dan printf langsung mengeluarkan
   `'      Zany object A does not work.'` lewat **INT 21h AH=02h**, 36
   panggilan untuk 36 karakter.
   Karena keluar lewat AH=02h, ATRIBUTNYA dipilih driver konsol DOS — bukan
   oleh gim — jadi tidak ada apa pun di biner yang bisa dibaca. Diukur di DOS
   sungguhan lewat `work/test_dosteks.py`: program 69 byte dirakit tangan
   (mode 4 → kursor (22,0) → cetak lewat AH=02h → buang 16 KB VRAM ke berkas),
   dijalankan headless di DOSBox-X. Hasil: 28 piksel, semuanya **warna 3**, di
   **x 0..5, y 176..182** — sekaligus KONFIRMASI INDEPENDEN atas barisnya.
   ⭐ BENTUK GLYPH-nya JUGA sudah ditutup. Font ROM BIOS diekstrak dgn teknik
   PROBE yang sama (`python port/import_romfont.py`: cetak ASCII 32..126 di
   mode 4, buang VRAM, dekode 95 sel 8x8) ke `port/cc/data/romfont.bin` —
   di-.gitignore, sama seperti aset gim: **yang ikut ke git PENGEKSTRAKNYA,
   bukan hasilnya**. `cc/core/dosfont.py` memuatnya; kalau belum diekstrak,
   port jatuh ke font gim dan itu dikatakan apa adanya.
   Diuji `python work/test_dosteks.py`: pesan gim sungguhan
   `"       Mechanism A does not work."` dirender port lalu diadu dgn hasil DOS
   di layar yang sama — **64.000/64.000 piksel**.
8. ~~Sisa pemakaian tangkapan (`review_layout.json`, `icons/`)~~ — **SELESAI**,
   dan catatan lama itu memang sudah basi. Dibuktikan `work/test_mandiri.py`:
   `builtins.open` dan `pygame.image.load` dibungkus supaya SETIAP pembacaan
   di bawah `port/cc/anim/` atau `port/cc/draws/` melempar, lalu port
   dijalankan lewat jalur pemain — nol pembacaan.
   ⭐ Font ROM sekarang ikut alur pemasangan biasa: `port/import_assets.py`
   memanggil `import_romfont.py` di ujungnya. Kalau DOSBox-X tidak ada di
   `tools/`, langkahnya dilewati dengan pesan dan port tetap jalan.
9. ~~Pembuka `animvm()` (jam pasir + bilah bola)~~ — **SELESAI (2026-08-02)**:
   `adegan.intro()`, **59/59 bingkai, 151.040/151.040 piksel**
   (`python work/test_intro.py`). Sebelum bola pertama, `animvm()` @0x18db
   menjalankan dua gelung di pita atas: jam pasir 48×8 berkedip di x=0x88,
   lalu bilah 16×8 meluncur dari x=0x78 ke `nbola*10`, 2 piksel per bingkai,
   ditutup `shftr()` dua kali + satu `fillrect`.
   ⚠ Mengukurnya butuh memperbaiki HARNESS SENDIRI dua kali — lihat §Jebakan.
   Primitif `render.shftr()` (geser CGA per BYTE, `blitmsk.asm` @0x6600) baru
   ditambahkan: `delta = -1` menggeser isi ke KIRI; namanya menggambarkan arah
   SUMBER, bukan arah isinya.
10. ~~`askopts` + ketiga layar instruksi belum diadu piksel~~ — **TERFOTO
   (2026-08-02)**, sesudah tiga penghalang di harness sendiri dibuka.
   `python work/test_layarawal.py`, masing-masing **64.000/64.000**:
   credits tahap **0, 1, 2, 3**, `askopts` **pertanyaan 1 DAN 2**, dan ketiga
   layar instruksi (**menu9** Fill in Mechanisms, **menu11** Fill in Zany,
   **menu12** Contraption Mix Up). Delapan layar; tidak ada sisa.
   Keempat penghalangnya:
   - `menu9()` @0x30BB **di-stub tanpa syarat** di `work/emu.py`, jadi layar
     instruksi mode 2 memang tidak pernah digambar. `menu11()` @0x30E0 dan
     `menu12()` @0x3105 tidak pernah di-hook sama sekali — keduanya sudah
     menggambar sendiri sejak dulu, tinggal ditangkap. 0x30BB kini patuh
     pada `CC_NOMENUSTUB`.
   - melepas stub `credits`/`askopts` (`CC_NOSTARTSTUB=1`) saja tidak cukup:
     memaksa `keyhit()` selalu ENTER membuat `kbflush()` @0x36EF menguras
     antrean yang TAK PERNAH HABIS. Itulah "menggantung sesudah credits".
   - dgn antrean berhingga pun `kbflush()` MEMAKAN satu tombol (terukur
     hilang di `ret=0x3707`), urutannya bergeser satu, dan `credits()` lalu
     menolak `Y` sampai antrean habis. Jawabannya sudah ada di berkas yang
     sama, di jalur OBSERVE: **lihat siapa pemanggilnya** — dari dalam
     `kbflush`, `keyhit()` harus bilang "buffer kosong".
   - pertanyaan KEDUA `askopts` butuh satu lapis lagi: `tone2()` di depannya
     memanggil `delay(5)` @0x2692, dan `delay()` gelung sibuk MURNI pada
     `ticks` — tanpa `vbwait()`, jadi `CC_SNDISR` pun tak menolong.
     ⚠⚠ Men-stub-nya dgn `force_ret_near()` di alamat MASUK justru **gagal
     diam-diam**: terukur dgn saklar baru `CC_DBGSP`, puncak tumpukan di
     0x2692 berisi **0x0005** — ARGUMEN `delay(5)`, bukan alamat balik — jadi
     ia melompat ke IP=5, mengembara, lalu muncul lagi di `main_`. Gejalanya
     persis seperti bug ALUR GIM ("askopts kembali ke awal"), padahal
     harness sendiri. Yang benar tidak menyentuh tumpukan: nol-kan `ticks`
     di UJI GELUNGNYA (0x26A2) lalu biarkan `delay()` keluar sendiri.
   ⚠ ALAT UKUR PUN BISA BERBOHONG: `CC_DBGSP` mula-mula didaftarkan SESUDAH
   `hook_waitn` pada alamat yang sama, jadi yang terbaca keadaan SESUDAH
   force_ret_near — SP dua byte terlalu tinggi, puncaknya nilai basi. Bacaan
   itu "mustahil" dan sempat menyesatkan. Ia kini didaftarkan di depan.
   Alamat + jumlah entri seluruh 12 tabel tetap terverifikasi terpisah lewat
   `python work/test_tabmenu.py` (diadu dgn `src_c/src/*.c` yang
   `.EXE`-nya byte-identik).

## Tiga celah cakupan yang ditutup 2026-08-02 — dan tiga bug yang ditemukannya

Ketiganya bukan "bug yang diketahui", melainkan bagian yang statusnya
"argumennya kuat, tapi belum diukur". Begitu diukur, dua di antaranya salah.

1. **Varian animasi.** Uji hanya mengadu SATU varian per goal. Digeser lewat
   keadaan RNG (saklar baru `CC_SEED`, BUKAN `VARIANT=`), seed 0x7 memunculkan
   varian kedua goal 1/3/4/6. Hasil **1.565/1.565 bingkai**.
   ⭐ BUG: goal 6 varian 2, `op03` yang melempar ke part TANPA titik jalur.
   `_tujuan()` punya cadangan "pakai posisi part itu sendiri" — keliru; gim
   tidak melempar sama sekali. Terbukti dari jejak `scrptr` @0x3AE: gim
   memakan 9 byte (`03 0a 03 | 09 00 | ff | 08 09 0c`) tanpa satu pun
   `drawball`. Falsifikasi lolos: itu satu-satunya kasus dari sepuluh varian.
2. **Layar bermain goal 2..6.** Hasil **14 kasus 64.000/64.000**.
   ⭐ BUG: `loadcon_pick()` membandingkan indeks varian RELATIF dgn `lastvar`
   @0x1e30 yang ABSOLUT — hanya kebetulan benar untuk goal 1 (`first = 0`),
   satu-satunya goal yang pernah diuji. Goal 4 meleset 13.370 piksel.
   `contrap.parse()` kini menyimpan `idx` absolut tiap record.
   ⚠ Uji sendiri juga salah: Contraption Mix Up TIDAK memakai pemilih goal
   (`sub` @0x3b2 terukur selalu 1), jadi menjalankannya enam kali hanya
   mengulang layar yang sama.
3. **Sapuan suara mode 1.** Penguraiannya bertanda "Ditafsirkan" dan memang
   belum pernah diukur. `tone3` @0x5B73 (L5C50): tiap tik ISR memainkan
   `[BX]` lalu `[BX] += [BX+4]`, dan berhenti saat `[BX] == [BX+2]` **sebelum
   memainkannya** — jadi nilai akhir TIDAK PERNAH terdengar. Port dulu
   memasukkannya.
   ⭐ Dan panjangnya TIDAK ditentukan data: gim hanya sempat membunyikan 25
   nada (500..884) sebelum `sndoff()`, padahal deret penuhnya sampai 1444.
   ⚠ Selama ini tak terlihat karena `test_suara.py` mengurai CETAKAN emulator
   yang DIPOTONG 16 nada — alat ukur yang membatasi temuannya sendiri.
   Daftar frekuensi penuh kini ditulis ke `pit_hz.json`.

### Celah keempat: RENTETAN enam ronde Contraption Mix Up (2026-08-02)

Mode 4 bukan satu layar melainkan enam kontraption berurutan (`sub++`), dan
hanya ronde PERTAMA yang pernah diadu. Menjangkau sisanya butuh tiga koreksi
harness, semuanya bukan emulator:

- `hook_58c9` menghentikan emulasi tepat sesudah animasi ronde pertama —
  kini patuh `CC_NOSTOP=1`;
- urutan tombol OBSERVE bawaan diakhiri **ESC**, dan ESC MEMBATALKAN ronde,
  jadi mode 4 dimasuki ulang dan `sub` selalu kembali ke 1. Yang benar:
  `pickloop()` @0x2E90 — SPACE di dalam `review()` mengembalikan
  `cur | 0x8000` (nilai NEGATIF, itu yang keluar dari gelung), lalu SPACE
  KEDUA dibaca `clrbot()` (case 0x20 → jalan). Panah tidak dipakai: mengubah
  pilihan berarti part benar-benar DITARUH;
- tanpa `CC_NOWAIT` animasi ronde pertama tak pernah selesai.

⭐ **BUG KETIGA.** `setmark()` mengembalikan DUA daftar tanda; port memakai
yang zany dan MEMBUANG yang mekanisme. Padahal `fillans.c` baris 46:
`if (lvl3 == 3 && markf[i] != 0) tt[i] = b[rnd(nmech) * 0xc];` — di Mix Up
slot mekanisme bertanda mendapat id ACAK. Ronde 4 dan 6 meleset 369 dan 606
piksel.

⚠ Rantai undiannya justru COCOK 16/16 sejak awal — yang salah PEMAKAIANNYA,
bukan undiannya. Alat yang membuktikannya baru: **`CC_RNDLOG`**, pencatat
tiap panggilan `rnd()` berikut alamat pemanggilnya (formatnya persis yang
sudah lama ditunggu `pick.uji_log()`, tapi belum pernah ada penghasilnya).
Ia menunjuk tepat ke `rnd(13)` dari 0x14FC di dalam `fillans`.

⚠ Perbaikannya perlu DUA hal sekaligus: memodelkan undian `mkpal` di dalam
`fillans`, DAN memakai direktori PENUH sebagai `base` di mode 4
(`loadarc(..., lvl3 == 1 ? 0 : 1, ...)`) — id acaknya diambil dari `base`,
dan di tabel tersaring id itu sering tidak ada. Memodelkan hanya yang pertama
justru MEMPERBURUK angkanya; itu petunjuk bagus bahwa penjelasannya belum
lengkap, dan alasan kenapa "angka membaik" bukan bukti.

→ enam ronde **384.000/384.000 piksel**; `test_play.py` kini 20 kasus.

### Celah keenam: JALUR PEMAIN untuk semua mode (2026-08-02)

`uji_interaktif` menjalankan `main.Game` + `key()` sungguhan, tapi hanya untuk
Fill in Mechanisms, satu tujuan, Apprentice. Diperluas ke **ketiga mode x kedua
tingkat**, dan memunculkan **enam bug port** yang TIDAK SATU PUN bisa terlihat
dari jalur modul inti — semuanya di `main.py`, jalur yang dilalui pemain:

1. `_scene_surface()` memanggil `susun()` **tanpa `isi_zany`**. Parameter itu
   ditambahkan belakangan untuk jalur modul inti; jalur pemain tidak ikut, jadi
   Fill in Zany menggambar objek yang seharusnya kosong (12.384 piksel).
2. `isi` diturunkan dari `fixed_archs`, bukan dari `fill_mode` — salah untuk
   Mix Up. Sekarang aturannya SATU dan sama dengan `start_play()`.
3. `drawslot()` diberi SELURUH slot, padahal ia penggambar **mekanisme**; slot
   zany kosong tidak menggambar apa pun dan di Mix Up tak ada yang kosong
   (5.654 piksel).
4. ⭐ `lvl2`/`lvl3` per mode-tingkat SALAH. `main_.c` menaikkan besaran yang
   BERBEDA tiap mode di Master: Fill in Mechanisms menaikkan `lvl3` ke 2 —
   syarat penyaring `mkpal()` gugur dan SELURUH daftar part ditawarkan
   (`nmech` 3 -> 13) — sementara Fill in Zany menaikkan `lvl2` dan `lvl3`-nya
   tetap 1. Aturannya kini di `adegan.tingkat()`.
5. ⭐ `mkpal()` dipanggil DUA KALI (sekali di `fillans`, sekali untuk strip).
   Gim hanya sekali — terukur di `CC_RNDLOG`: satu blok 15 undian dari 0x3a8d,
   tidak ada blok kedua. Lima belas undian ekstra menggeser seluruh urutan
   strip. Paletnya kini dipakai ulang lewat `pil["palet"]`.
6. Jumlah bola: `goal = 6` hanya berlaku di Master (`if (lvl == 1) goal = 1;`),
   dan port memberi 6 untuk keduanya — lima ikon berlebih di pita atas.

⚠ Urutan undian juga berpengaruh: prolog `runplay()` (satu `rnd(200)`) jatuh
SESUDAH `mkpal()`, bukan sebelum. Menaruhnya di tempat yang salah memberi
himpunan part yang benar tapi URUTAN yang salah.

### ⏳ BELUM SELESAI: animasi JALUR BERMAIN (dibuka 2026-08-02)

Uji animasi (1.565/1.565) menangkap `emu.py <goal> **1**` — yaitu animasi
**attract/demo**. Animasi yang berjalan sesudah pemain menekan SPACE di mode
2/3/4 BELUM pernah diadu piksel, dan ia memang berbeda.

**Terukur** (goal 1, Fill in Mechanisms, tangkap di `drawball` @0x26AE):

| keadaan | bingkai |
|---|---|
| tanpa satu pun part ditaruh | **41** |
| beberapa part ditaruh | **62** |
| port (selalu memakai jawaban benar dari `fillans`) | **105** |

Jadi panjang animasinya **bergantung pada apa yang ditaruh pemain**. Dua
aturan, keduanya dibaca dari `animvm.c` yang byte-identik:

1. **baris 222** — slot MEKANISME yang jawabannya salah:
   `failed = -1; ...; zcnt++; printf(msgmech, ...); **break**;`
   `break` itu keluar dari gelung part: animasinya BERHENTI, bukan sekadar
   menampilkan pesan.
2. **baris 433** — lemparan ke part yang jawabannya salah: gim MENGARANG
   skrip `{00, dx, dy, FF}` supaya bolanya tetap bergerak ke arah yang masuk
   akal, lalu menunjuk record part itu ke skrip karangan tersebut.

**Sudah dikerjakan dan TERUKUR.** Bingkai pertama turun dari **14.716 → 689
piksel**, jumlah bingkai dari 105 → 46 (gim 41). Empat hal yang membawanya ke
sana, semuanya diukur bukan diterka:

1. ⭐ **BUG PORT: `frames()` tidak meneruskan `lastgoal`/`lastvar`.** Tanpa
   keduanya gelung penghindar varian di `loadcon()` tidak berjalan, dan port
   menganimasikan varian yang SAMA SEKALI LAIN — 18.324 piksel. Jalur attract
   tidak memerlukannya (`lastgoal` masih 0), jadi ini tak pernah terlihat
   sampai jalur BERMAIN diadu. Sekarang diteruskan.
2. **Penjajaran bingkai = offset 2.** Tangkapan `f0000`/`f0001` jalur bermain
   masih layar SETENGAH GAMBAR (arena kosong); kontraption baru lengkap di
   `f0002`. Jangan pakai offset 1 seperti jalur attract.
3. **`clrbot()` @0x5911 mengosongkan dasar layar sebelum larian.** Baris pesan
   cyan yang digambar `setupscr()` untuk `sub == 1` TIDAK ada saat animasi —
   288x8 = **2.304 piksel**, persis. `frames(hias=)` dipakai untuk menirunya.
4. `vm.VM(berhenti_di=)` + `frames(jawaban_mech=)` memodelkan aturan 1.
   Penjaganya di `_pindah()`, bukan di cabang `end` saja — perpindahan part
   terjadi lewat DUA jalan (penutup skrip dan lemparan `op03`).
   ⚠ Indeksnya **indeks PART, bukan indeks `state`**: gelung pembangun `parts`
   melewati slot yang `base`-nya None.

Bawaannya `jawaban_mech=None` → perilaku lama persis, diverifikasi: animasi
attract tetap **1.565/1.565**, 23/23 uji lulus.

**Sisa 689 piksel itu sudah TERJELASKAN** (2026-08-02), dan jawabannya
mengubah bentuk pekerjaan yang tersisa:

- `fillans()` mengisi **jawaban BENAR untuk semua slot** lalu `place()`
  menggambarnya, SEBELUM `animvm` jalan. Jadi layar larian menampilkan part
  yang benar untuk slot yang TERISI, apa pun yang ditaruh pemain; yang dipakai
  memeriksa hanya `ord1`.
- Slot yang BELUM diisi tampil sebagai petak abu (`drawslot()`), dan model itu
  terbukti **EKSAK**: dgn urutan tombol yang tidak menaruh apa pun, dua dari
  tiga slot cocok **0 piksel**.
- Sisa satu slot ternyata TERISI: `SPACE` di dalam `review()` mengembalikan
  `cur | 0x8000`, dan karena `sel[curz]` awalnya berbeda, ia MENEMPATKAN part
  strip #0. Jadi bahkan "hanya menekan SPACE" pun menaruh satu part.

⇒ **Penempatan pemain menentukan DUA hal sekaligus**: gambar di layar dan
titik berhenti animasi. Maka pembandingnya tidak bisa memakai `frames()` dgn
`jawaban_mech` karangan — ia harus **menjalankan port lewat `main.Game` dgn
urutan tombol yang SAMA seperti yang diumpankan ke emulator**, supaya
penempatannya cocok BY CONSTRUCTION. Itulah pekerjaan berikutnya, dan ia
harness, bukan port.

**Harness-nya SUDAH ADA**: `work/test_anim_main.py` — menangkap animasi jalur
bermain (`OBSERVE=... CC_VRAMSEQ=26ae`) lalu mengadunya dgn port yang
dijalankan lewat `main.Game` + `key()`.

⭐ **BUG PORT yang ditemukannya:** `_anim_surfaces()` selalu membangun animasi
**DEMO** untuk larian bermain — seed 0, mode judul, TANPA `lastgoal`/`lastvar`,
dan dgn pembuka jam pasir. Untuk larian sesudah pemain menekan SPACE itu
semuanya salah. Sekarang ia memakai konteks bermain (seed/lastgoal/lastvar
ronde itu, `isi`/`isi_zany` menurut mode, `clrbot()`, tanpa pembuka).
Hasil: bingkai pertama **24.501 → 293 piksel**, jumlah bingkai **195 → 46**
(gim 34).

⭐ **SEMANTIK `SPACE` SUDAH DIBETULKAN (2026-08-02).** Di gim, `SPACE` punya
DUA tahap:

    review()  @0x3C4F : case ' ' -> `return cur | 0x8000`
    pickloop() @0x2E90: `v = r & 0x7fff; if (sel[curz] != v) {...taruh...}`
                        `curz++;` lalu gelung KELUAR (r < 0)
                        `switch (clrbot())` 0x20 jalan / 0x0d pilih lagi /
                                            0x1b batal

Jadi SPACE PERTAMA **menaruh** part yang sedang disorot lalu mengakhiri
pemilihan; SPACE KEDUA baru menjalankan. Port lama langsung menjalankan.
Sekarang `_play_key()` memakai bendera `pilih_selesai` yang meniru
`clrbot()`.

**Buktinya penempatan kini cocok BY CONSTRUCTION:** dgn urutan tombol yang
sama (SPACE, SPACE), gim dan port sama-sama berakhir dgn slot 0 terisi part
`141` dan dua slot lain kosong. Sebelumnya port berakhir di keadaan lain.

⚠ Sembilan uji mengunci semantik lama dan ikut dibetulkan (`test_mixup`
menekan SPACE dua kali; `test_bantuan` menyatakan `pilih_selesai = True`
karena skenarionya sengaja menyisakan slot salah).

**Larian GAGAL sudah bisa ditangkap** (`CC_SALAH=1` mematikan paksaan cocok):
goal 1 mode 2 dgn tombol SPACE,SPACE → **8 bingkai** (2 di antaranya redraw),
`zcnt` 0→1. Aturan berhenti di VM juga TERBUKTI bekerja: dgn
`berhenti_di={7,8}` part 8 dan 9 tidak lagi dikunjungi.

⚠ **TAPI PENEMPATANNYA MASIH BEDA, dan sebabnya sudah terlokalisasi.** Gim
berhenti sesudah ~6 bola, port sesudah 46 — artinya gim berhenti di mekanisme
PERTAMA (indeks rantai 2), bukan di indeks 7. Jadi part yang ditaruh gim di
slot 0 BUKAN jawaban benarnya.

Sebabnya bukan `cur_part` (keduanya 0), melainkan **URUTAN PALET**: masing-
masing menaruh part di posisi 0 paletnya sendiri, dan isi palet mode 2 belum
pernah diadu. Terukur: gim `idtab` = `[4, 0, 2]` (indeks ke `base`), port
palet = record `[26, 2, 17]` (id `[141, 110, 132]`). Uji strip yang lulus
64.000/64.000 TIDAK membuktikan ini — ia menggambar strip dari `idtab` GIM,
bukan dari palet port. Yang pernah diadu lewat palet port hanya Mix Up.

**Sudah diperiksa, dan DUA dugaan TERBANTAH** (2026-08-02) — dicatat supaya
tidak diulang:

1. ❌ "urutan palet mode 2 berbeda" — **SALAH**. Diadu langsung: gim
   `idtab`→record `[26, 2, 17]`, port palet `[26, 2, 17]`. **Cocok persis.**
   (Mode 3 memang berbeda, tapi itu soal lain: strip mode 3 berisi objek
   GRAPH di port sementara `idtab` gim menunjuk mekanisme — belum diselidiki.)
2. ❌ "gim hanya menaruh kalau `sel[curz] != v`, dan `sel[]` mulai dari 0,
   jadi SPACE pertama tidak menaruh apa pun" — **SALAH**. Pengukuran
   menunjukkan gim JUSTRU menaruh part di slot 0 (terlihat jelas di
   tangkapan, 284 piksel di petak itu). Jadi `sel[]` TIDAK mulai dari 0;
   nilai awalnya belum diukur.

**Yang sempat dicoba lalu DIKEMBALIKAN**: mengganti jalur gagal port dari
`_jalur()` ke VM (+ `_hias_bermain` yang menggambar part yang sudah ditaruh).
Ia membuat `test_bantuan` gagal — uji itu menunggu `running` dgn lintasan
bola, sementara jalur baru berakhir di `PLAYANIM`, dan menyesuaikannya tidak
membuat pencacah gagalnya naik. Karena manfaatnya juga belum terbukti
(bingkai pertama justru 293 → 369 piksel), perubahan itu dikembalikan.
Pohon kerja tetap 23/23.

**Keadaan terukur sekarang** (goal 1 mode 2, `CC_SALAH=1`, tombol SPACE,SPACE):
gim **6 bingkai**, port **46**; bingkai pertama beda **293 piksel**, seluruhnya
di petak slot 0 — gim menampilkan part yang ditaruh, port menampilkan petak
abu.

**Langkah berikutnya yang tepat, berurutan:**
1. Ukur nilai AWAL `sel[]` di gim (mis. `CC_VSMEM` pada alamat larik itu),
   supaya aturan "menaruh hanya kalau berubah" bisa dimodelkan dgn benar.
2. Ukur MENGAPA gim berhenti sesudah 6 bola padahal slot 0 terisi benar —
   apakah `ord1[0]` memang tidak tertulis, atau rantainya berbeda.
3. Baru sesudah keduanya jelas, ganti jalur gagal port ke VM (kodenya sudah
   ada di `vm.VM(berhenti_di=)`), lalu aturan skrip karangan.

## Jebakan yang sudah pernah menggigit (jangan ulangi)

- **Sprite di-render OPAQUE, bukan colorkey cyan.** Blitter asli `672f` menulis semua piksel;
  cyan = warna latar, bukan transparansi. Colorkey bikin piksel cyan di dalam sprite hilang.
- ~~**Indeks varian `draws_goalN_vI.json` TIDAK sejajar dengan `goalN_vI.dat`**~~ — jebakan
  ini SUDAH TIDAK ADA. `_match_anim()` (yang mencocokkan animasi ke layar design lewat isi
  frame-0) sudah dibuang: adegan dan animasi kini lahir dari data yang sama, oleh undian
  yang sama, jadi tidak ada yang perlu dicocokkan. Bug "layar design ≠ layar run" tidak
  bisa terjadi lagi **secara konstruksi**, bukan karena diperbaiki.
- **⭐ "TERHALANG EMULATOR" SEBELAS KALI TERNYATA "TERHALANG HARNESS SENDIRI".**
  Enam yang terbaru (2026-08-02), semuanya menyembunyikan layar/animasi utuh:
  (6) `ticks` @0x2e4 dihitung mundur ISR timer yang tidak dijalankan emulator,
  jadi gelung jam pasir `animvm` tak berujung — dan `CC_NOWAIT` "mengatasinya"
  dengan MELEWATI gelungnya, jadi pembukanya memang tak pernah dijalankan
  sekali pun. `sndisr` @0x670E ternyata mengurangi `ticks` (`keyio.asm`
  baris 40), jadi `CC_SNDISR=1` sudah cukup: pewaktu sungguhan, tanpa stub.
  (7) `CC_SNDISR` itu sendiri cacat — pelepas penjaganya terdaftar di 0x5D98,
  alamat yang SAMA dengan pemicunya, jadi `IRET` memicu ISR lagi, selamanya;
  tumpukannya seimbang sehingga buntunya DIAM. Pelepasnya kini di `vbend`
  @0x5DA1. (8) `menu9()` @0x30BB **di-stub tanpa syarat**, jadi layar
  instruksi mode 2 memang tak pernah digambar — sementara `menu11()`/
  `menu12()` tidak pernah di-hook dan sudah menggambar sendiri sejak dulu.
  (9) memaksa `keyhit()` selalu ENTER membuat `kbflush()` @0x36EF menguras
  antrean yang tak pernah habis. (10) dgn antrean berhingga pun `kbflush()`
  MEMAKAN satu tombol, jadi urutannya bergeser dan `credits()` menolak `Y`
  sampai antrean habis. (11) — paling licik — stub `delay()` @0x2692 dgn
  `force_ret_near()` memungut **ARGUMEN** `delay(5)` sebagai alamat balik dan
  melompat ke IP=5; gejalanya menyerupai bug ALUR GIM ("askopts kembali ke
  awal"), bukan bug harness.
  ATURAN BACANYA: sebelum menulis "emulator tidak bisa", cari dulu STUB, HOOK,
  dan URUTAN TOMBOL milik sendiri — **sebelas dari sebelas kali** di situ
  penyebabnya. Cara mendiagnosisnya selalu sama: catat SIAPA PEMANGGILNYA
  (alamat balik di tumpukan, `CC_DBGSP`), jangan menyimpulkan dari alur.
  ⚠ Dan alat ukurnya sendiri bisa berbohong: `CC_DBGSP` mula-mula didaftarkan
  SESUDAH `hook_waitn` pada alamat yang sama, jadi yang terbaca keadaan
  SESUDAH `force_ret_near`. Daftarkan penyelidik di DEPAN.
  Lima yang lebih dulu. Keempat: gelung "jam pasir" `animvm` menunggu `ticks`
  yang tak pernah turun karena ISR timer tidak berjalan. Kelima:
  `hook_mechmatch`/`hook_zanymatch` MEMAKSA IP ke jalur "cocok", jadi cabang
  ber-`printf` dilewati tanpa syarat (`CC_SALAH=1` mematikannya). Tiga yang
  lebih dulu: Pertama:
  tangkapan `drawpal` diambil di alamat MASUK, bukan RET. Kedua: `work/emu.py` sengaja
  mem-bypass gelung penempatan part (`hook_2e90`) dan `drawpal` hidup di dalamnya —
  saklar `CC_NOSKIP=1` menyelesaikannya. Ketiga: di mode Mix Up penghalangnya urutan
  tombol OBSERVE bawaan yang diakhiri **ESC**, yang membuat `runplay()` mengembalikan
  -1 sebelum strip sempat digambar. Sebelum menyimpulkan "emulator tidak bisa",
  periksa dulu hook, stub, dan urutan tombol milik sendiri.
- **`VARIANT=` TIDAK BISA DIPAKAI untuk menyamakan varian.** Hook-nya memaksa SEMUA
  `rnd()` yang dipanggil dari dalam `loadcon`, dan gelung
  `do { pick = rnd(cnt) } while (... pick == lastvar)` jadi tak berujung — gejalanya
  "0 frame", yang mudah salah dibaca sebagai "emulator tak mencapai titik itu".
  Cara yang benar: BACA keadaan RNG gim (seed @0x71a, lastgoal @0x1e2e,
  lastvar @0x1e30) lalu berikan ke `susun()`.
- **⭐ SEKALI SATU KASUS DIUKUR, JANGAN ANGGAP SISANYA IKUT TERBUKTI.** Dan
  ini terbukti LAGI pada 2026-08-02: menutup tiga celah cakupan (varian
  animasi, goal 2..6, sapuan suara) langsung memunculkan tiga kesalahan, dua
  di antaranya di kode port. Semuanya di jalur kode yang "sudah cocok" —
  yang berbeda hanya DATA-nya. Aturan turunannya: kalau sebuah pembenaran
  berbunyi "jalur kodenya sama", itu ARGUMEN, bukan pengukuran.
- **SEKALI SATU MODE DIUKUR, JANGAN ANGGAP MODE LAIN IKUT TERBUKTI.** Fill in
  Mechanisms cocok 64.000/64.000 sementara Fill in Zany masih meleset 12.194
  piksel dan Mix Up 10.784 — dan yang membongkarnya LIMA bug berbeda, termasuk
  dua yang tak mungkin terlihat di mode pertama (`setzany`/`setmark` memakai
  RNG, dan cabang `lvl2 == 2 && mark[i]` di `pickpart` yang dicatat "belum
  diperlukan"). Aturan bacanya: satu mode terukur = satu mode terukur.
- **KECOCOKAN PIKSEL TIDAK SELALU MEMBUKTIKAN RANTAI RNG.** Layar Fill in Zany
  cocok 64.000/64.000 bahkan sebelum `setzany()` ditambahkan — karena yang
  tampak di sana cuma mekanisme (deterministik lewat `fillans`) dan objek zany
  TERAKHIR (dipaksa `row == sub`). Yang membuktikan rantai adalah mode 4.
- **UJI LEWAT MODUL INTI TIDAK MELIHAT BUG DI `main.py`.** Layar bermain cocok
  64.000/64.000 lewat modul inti sementara jalur pemain masih meleset 738 piksel:
  `start_play()` mengocok palet DUA KALI — kocokan gim yang benar, lalu
  `random.shuffle` peninggalan lama di atasnya. Uji jalur user itu aturan kerja
  no. 7, dan inilah contoh kenapa.
- **`open(p, "w")` MEMOTONG BERKAS SEBELUM `write()` DIJALANKAN.** Satu koma
  nyasar di akhir ekspresi membuat `write()` menerima tuple, gagal, dan
  `port/main.py` tinggal 0 baris. Diselamatkan `git checkout --`. Untuk sunting
  berpola, pakai Edit; kalau memang harus lewat skrip, tulis ke berkas baru lalu
  ganti nama.
- **UJI YANG BASI GAGAL DIAM-DIAM, ATAU LEBIH BURUK: TETAP LULUS.** `test_fill`,
  `test_zany`, `test_review` sudah lama gagal karena melewatkan layar LEVEL yang
  ditambahkan belakangan. `test_mixup` lebih licin: ia menavigasi lewat layar GOAL, dan
  sesudah layar itu dihapus untuk Mix Up ia TETAP "lulus" karena tombol berlebihnya
  cuma terserap gelung PLAY. Jalankan seluruh berkas `work/test_*.py`, jangan hanya
  yang sedang dikerjakan.
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
