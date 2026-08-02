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

- ⭐ **ANIMASI 100% IDENTIK** (2026-08-01): mesin `animvm()` di `port/cc/core/vm.py`
  menjalankan skrip dari berkas aset. Terukur vs tangkapan VRAM emulator, animasi
  PENUH ketujuh layar dari frame pertama sampai habis:
  **1.210/1.210 frame byte-identik, 77.440.000/77.440.000 piksel (100,000000%)**.
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
- ⭐ **LAYAR INSTRUKSI ADA** (2026-08-02): `menu9`/`menu11`/`menu12`
  (tabel DGROUP @0x1634 9 entri, @0x1796 11, @0x18f8 12). Gim menampilkannya
  SEKALI per mode (`if (k == 1)` di main_.c), dan port lama TIDAK PUNYA
  layar ini sama sekali — pemain tak pernah diberi tahu aturan modenya.
  Alur sekarang: MENU → LEVEL → **INSTRUKSI** → GOAL (atau langsung main di
  Mix Up). ⚠ Byte 0x80..0x83 di dalam stringnya GLYPH PANAH, bukan huruf.
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
1. ~~Frame animasi yang belum byte-identik~~ — **SELESAI**: 1.210/1.210 frame,
   100,000000% piksel (`python work/test_anim_vs_gim.py`). Catatan panjang tentang
   sembilan percobaan yang gagal tetap disimpan di `port/cc/core/adegan.py`: yang
   akhirnya membuka semuanya adalah MEREKAM (`CC_TRACEWR`) lalu MENYAPU kombinasi
   secara terukur, bukan menafsirkan assembly.
2. ~~Suara PC-speaker~~ — **SELESAI**: `port/cc/core/bunyi.py`. Angka di skrip adalah
   **frekuensi dalam Hz** (dari `1193182 / CX` di `snd2.asm`), bukan pembagi PIT.
   Tiap not 3 byte: `u16 frekuensi + u8 durasi` (tik INT 1Ch, ~18,2/detik), diakhiri
   `FFFF`; mode 2 sekali jalan, mode 3 BERULANG, mode 1 sapuan tiga word.
   Diuji `python work/test_bunyi.py`. 117 not terdekode dari skrip goal 1.
3. **Layar yang MASIH belum ada di port** (semuanya tabel DGROUP, polanya sama
   dgn layar instruksi yang sudah dikerjakan):
   - `askopts()` @0x31DA — dua pertanyaan Y/N saat mulai (monitor berwarna,
     lalu suara). Tabel @0x1AD2 (3 entri) dan @0x1AF6 (2 entri; entri
     pertamanya MENIMPA pertanyaan sebelumnya dgn warna 1 — itu cara gim
     menghapusnya). Tabelnya sudah ada di `menu.py` sebagai `MTAB_SETUP1/2`.
   - `credits()` @0x312A — empat tabel (@0x1A2A, 0x1A42, 0x1A5A, 0x1A72)
     ditumpuk berurutan dgn `pause(100)` di antaranya. Sudah ada sebagai
     `MTAB_CREDITS`.
   Keduanya BELUM dipasang ke alur dan belum diadu piksel.
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

## Jebakan yang sudah pernah menggigit (jangan ulangi)

- **Sprite di-render OPAQUE, bukan colorkey cyan.** Blitter asli `672f` menulis semua piksel;
  cyan = warna latar, bukan transparansi. Colorkey bikin piksel cyan di dalam sprite hilang.
- ~~**Indeks varian `draws_goalN_vI.json` TIDAK sejajar dengan `goalN_vI.dat`**~~ — jebakan
  ini SUDAH TIDAK ADA. `_match_anim()` (yang mencocokkan animasi ke layar design lewat isi
  frame-0) sudah dibuang: adegan dan animasi kini lahir dari data yang sama, oleh undian
  yang sama, jadi tidak ada yang perlu dicocokkan. Bug "layar design ≠ layar run" tidak
  bisa terjadi lagi **secara konstruksi**, bukan karena diperbaiki.
- **"TERHALANG EMULATOR" LIMA KALI TERNYATA "TERHALANG HARNESS SENDIRI".**
  Keempat: gelung "jam pasir" `animvm` menunggu `ticks` yang tak pernah turun
  karena ISR timer tidak berjalan (`CC_NOWAIT=1`). Kelima:
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
