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
   untuk status faktual (jangan percaya angka di dokumen, percaya alatnya).

Arsip percakapan mentah ada di folder memory Claude Code (`*.jsonl`, 9,3 MB).
Pakai HANYA kalau perlu menelusuri satu detail spesifik; jangan dibaca utuh dan
jangan dipakai sebagai sumber status. Path lengkapnya ada di `src_c/JOURNAL.md`.

**Pekerjaan berikutnya, urutan disarankan (per 2026-07-31, sesudah sesi semalaman):**

⚠ **BACA DULU: cara mengukur sudah BERUBAH.** Metrik "byte cocok per POSISI"
hanya sahih kalau panjang draf sudah persis sama dengan aslinya. Untuk fungsi
yang belum pas panjangnya, pakai:
```
python src_c/verify/aligncmp.py <nama>                    # ringkasan + daftar geseran
python src_c/verify/aligncmp.py <nama> --sbs <addr> <n> <geser>   # berdampingan
```
`pickvar` sempat menunjukkan POSISI 368 padahal 1.616 byte benar-benar
sejajar. Satu perubahan menurunkan POSISI 392->386 tapi menaikkan penjajaran
684->704 — kalau percaya angka posisi, perubahan yang BENAR akan dibuang.

1. **`main` (0x0082, 4.219 B) — SUDAH DIMULAI, `src_c/src/main_.c`.**
   Peta bingkai sudah TERVALIDASI (lokal persis; `sub sp` kita 0x6F90 vs
   0x6F96, selisih 6 = temp yang belum tumbuh). 229 byte pembuka ditulis.
   Teruskan blok demi blok dari 0x0179.
2. **`pickvar` (0x42ca) — 93,4% sejajar, tiga titik geseran tersisa**
   (`+3 @0x43B8`, `+1 @0x4515`, `+4 @0x495A`). Daftar "sudah dicoba & gagal"
   ada di ujung berkasnya.
3. Dua near-miss lama: `place` (sisa 2 byte, SI vs DI) dan `nvar` (551/566).
4. VM animasi (0x18db, 3.040 B) dan `0x498c` (fungsi tepat sesudah pickvar).

**DUA KEPUTUSAN MENUNGGU USER:**
- `gendata.py` membuang alamat DGROUP 0..3 (penyaring `START <= a`, START=4).
  Akibatnya `mov bx,[0]` di `main` belum bisa ditulis (biaya 7 byte).
  Memperbaikinya menyentuh DGROUP yang sekarang 100% cocok — perlu izin.
- 0x846 bernama `mode_` padahal isinya pegangan berkas dari `open()`.
  Ganti nama atau biarkan?

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

Dokumen: `CODE_MAP.md` (paling akurat & terkini), `ARCHITECTURE.md`, `GAME_GUIDE.md`,
`DECOMPILE_PLAN.md`, `TARGET_LANGUAGE.md`, `RESUME_EXACT.md` (peta jalur pixel-exact).
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

## Status decompile→source (per 2026-07-31)

- **LINK berhasil**: 61 `.OBJ` + `MC.LIB` → `src_c/out/CONTRAP.EXE`, tanpa error.
- **Segmen DATA 9.556/9.556 byte, 0 beda** vs biner asli (diukur dari .EXE hasil link).
- **Kode C+ASM: 68/72 fungsi COCOK byte-per-byte, 14.149 byte**; TOTAL 64,5%.
  `pickvar` dan `main` kini punya SUMBER NYATA (bukan stub) dan ikut di-link,
  tapi belum byte-exact jadi belum dihitung COCOK:
  `pickvar` 1.616/1.730 sejajar (93,4%), `main` 229/4.219 ditulis.
  Stub tersisa **1**: `setup` (0x5f90), dipanggil `main`.
- ✅ Tabrakan nama `put()` sudah dibereskan: `put`=0x65e0, `putmsk`=0x6524.
- Dua near-miss: `place` (503 byte tepat, 2 byte beda = register SI/DI) dan
  `nvar` (551/566, 2 temp kelebihan). Peta slot & daftar gagal ada di berkasnya.
- Batas keras pertama ditemukan: 1 byte di `load` (0x53ff+134) adalah artefak
  kompiler yang bergantung NAMA BERKAS, bukan sumber C — lihat `src_c/README.md`.
- Batas wilayah pustaka MC.LIB TERBUKTI di 0x69d7 (`src_c/verify/libmatch.py`),
  jadi target rekonstruksi = 27.095 byte kode game, bukan 36.976.
- ⚠ `.EXE` itu **belum bisa dijalankan** — `main` + 21 fungsi lain masih stub kosong.
- Aturan & jebakan lengkap: **`src_c/README.md`** (baca sebelum menyentuh `src_c/`).

## Status port (per 2026-07-21)

**Selesai & terbukti:**
- Unpack PKLITE, decompile 144 fungsi, format aset & CONTRAP tervalidasi.
- Render 6 contraption **100% pixel-match** vs game asli.
- **"Fisika bola" = VM animasi ber-skrip** (`FUN_1000_18db`, 17 opcode, tabel `CS:0x23D4`,
   skrip dari file ANIMATE) — BUKAN physics engine. Parser 100%, interpolator parabola
   `2823` **42/42 eksak**.
- **Ke-4 mode jalan**: Review Mechanisms (ensiklopedia + demo goal 7), Fill in Mechanisms
   (multi-varian acak), Fill in Zany Objects, Contraption Mix Up (timer + bonus).
- Layar judul beranimasi (rantai Rube-Goldberg custom), palet part dikocok, skoring, navigasi
   sesuai hierarki asli (selesai/ESC → pilihan GOAL, bukan menu depan).

**Berikutnya untuk jalur PORT (JEDA — hanya kalau user minta khusus):**
1. Interpreter generate part-frame sendiri (op 01/07/09 → record ANIMATE) — agar lepas dari
   data capture emulator.
2. Turunkan transform logis→layar `FUN_1000_5e3b` (syarat interaktif penuh + bola sub-pixel).
3. Render mandiri yang sync (mesin composite + erase jejak bola).
4. Status bar/skor lengkap + suara PC-speaker (op 0x04 sudah diparse).
5. Harness frame-diff vs DOSBox-X (bukti pixel-identical).

## Jebakan yang sudah pernah menggigit (jangan ulangi)

- **Sprite di-render OPAQUE, bukan colorkey cyan.** Blitter asli `672f` menulis semua piksel;
  cyan = warna latar, bukan transparansi. Colorkey bikin piksel cyan di dalam sprite hilang.
- **Indeks varian `draws_goalN_vI.json` TIDAK sejajar dengan `goalN_vI.dat`.** Animasi run
  dipilih lewat **pencocokan konten frame-0** (`Game._match_anim`, `port/main.py:507`), bukan
  indeks. (Bug 2026-07-21: layar design ≠ layar run.)
- **`0x260`(x)/`0x25e`(y) = koordinat LOGIS per-part, BUKAN posisi layar.** Drawer `5e3b`
  menerapkan transform + sub-pixel. Untuk render, ambil posisi layar dari VRAM.
- **Urutan slot CONTRAP ≠ urutan draw** — cocokkan by-POSISI, bukan by-indeks.
- Emulator merender sprite (`672f`) tapi **tidak** teks font (`6453`/`381a`) → untuk layout
  teks, ekstrak tabel `381a`/`3769` dari DGROUP.
- Ekstraksi sub-sprite dari latar berwarna membawa piksel latar → filter hanya piksel objek;
  hapus base (fill cyan) sebelum overlay reaksi.
