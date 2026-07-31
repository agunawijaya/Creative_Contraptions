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

**Pekerjaan berikutnya (per 2026-07-31 pagi, sesudah sesi semalaman):**

⚠ **Cara mengukur:** metrik **GLOBAL** yang memutuskan.
`python src_c/verify/gapprof.py --semua` untuk PANJANG (profil celah),
`python src_c/verify/shapediff.py <nama> <addr> <ukuran>` untuk BENTUK.
Jangan pakai "byte cocok per posisi" maupun metrik serakah — keduanya
menyesatkan begitu panjang draf bergeser.

⭐ **URUTAN KERJA yang terbukti** (menaikkan `main` 80,1% → 99,6%):
   1. Perbaiki **PANJANG** dulu — lacak di mana offset (KITA−ASLI) BERUBAH.
      Selama panjang masih bergeser, metrik apa pun akan MENGHUKUM bentuk yang
      BENAR dan memberi HADIAH pada bentuk yang kebetulan menambal geseran.
   2. Sesudah panjang lurus, **UJI ULANG SEMUA PENOLAKAN LAMA**. Dua perbaikan
      terbesar `main` adalah hal yang sebelumnya sudah ditolak (satu bahkan dua
      kali). Daftar "dicoba & gagal" KEDALUWARSA — begitu pula "dicoba &
      berhasil": satu perbaikan lama di `animvm` ternyata cuma menambal geseran.
   3. Baru garap BENTUK lokal.

**Sisa pekerjaan — SELURUHNYA kelas alokasi register**, tidak ada lagi struktur
yang belum ditulis dan tidak ada stub:
1. `main` 4.201/4.219 (99,6%) — 18 byte, gugusan terbesar 8 byte di 0x0126.
2. `pickvar` 1.654/1.730 — panjang −3; asli menumpahkan `si` ke `[bp+2]`.
3. `loadcon` 687/739 — dua situs (0x5115, 0x527e).
4. `place` (2 byte) + `f498c` (3 byte) — murni pilihan register SI vs BX/DI.
⭐ Sasaran paling berharga: memahami apa yang menentukan **WAKTU SIMPANAN ke
memori**. Itu satu sebab yang sama di EMPAT situs berbeda; kalau ketemu, ia
menutup keempatnya sekaligus.

**TIGA KEPUTUSAN MENUNGGU USER:**
- `gendata.py` membuang alamat DGROUP 0..3 (penyaring `START <= a`, START=4),
  memblokir 13 byte di `main`. Perbaikannya menyentuh DGROUP yang kini 100%.
- `mode_` (0x846) dan `seed` (0x72a) namanya menyesatkan — keduanya PEGANGAN
  BERKAS. Ganti nama atau biarkan?
- **Angka target perlu dikoreksi**: 1.200 byte di 0x5F93..0x6442 ternyata NOL,
  bukan kode. Semua persentase "kode game" selama ini terlalu kecil.

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

## Status decompile→source (per 2026-07-31 pagi)

- **LINK berhasil**: 61 `.OBJ` + `MC.LIB` → `src_c/out/CONTRAP.EXE`, tanpa error.
- **Segmen DATA 9.556/9.556 byte, 0 beda** vs biner asli (diukur dari .EXE hasil link).
- **Kode C+ASM: 78/81 fungsi COCOK byte-per-byte, 18.851 byte**; TOTAL 77,3%,
  kode C game 72,5%. **TIDAK ADA stub tersisa** — `animvm` (3.040 B) SELESAI
  2026-07-31, dan `nvar` (566 B) juga.
  Empat fungsi belum byte-exact tapi sudah sangat dekat (metrik GLOBAL):
  `main` 4.203/4.219 (99,6%), `place` 501/503, `loadcon` 687/739 (93,0%),
  `pickvar` 1.654/1.730 (95,6%). `f498c` SELESAI 2026-07-31.
  ⚠ Sisanya SELURUHNYA kelas alokasi register — bingkai semua fungsi sudah cocok
  dan tidak ada lagi struktur yang belum ditulis.
  ⚠⚠ Dari 71 byte sisa, **~60 byte TERBUKTI di luar jangkauan alat sekarang**:
  pilihan register yang diwarisi SE-FUNGSI, bukan dari bentuk sumber lokal
  (dibuktikan `src_c/probes/probeC.c` — lima varian semuanya memberi hasil
  sama). `loadcon` 52 byte seluruhnya kaskade dari SATU keputusan di 0x5115.
  Yang masih punya peluang nyata cuma ~11 byte di `main`.
- TIGA fungsi selesai 2026-07-31 lewat DUA aturan baru (keduanya di `src_c/README.md`):
  - `f2823` (397 B, interpolator parabola) — `probes/probe19.c`: slot bingkai berisi
    konstanta `long` menandakan VARIABEL, dan cor `(long)` yang mubazir secara
    semantik tetap mengubah kode.
  - `f278e` (149 B) + `f2714` (122 B) — **`extern char *p` ≠ `extern int p` + cor
    `*(char *)p`**. Tipe penunjuk asli dimuat langsung ke SI dan DIMUAT ULANG tiap
    rujukan; bentuk cor lewat AX dan ditahan di register. Aman untuk DGROUP:
    gendata.py memancarkan simbol bukan-larik sebagai `int` apa pun tipe externnya.
- ✅ Tabrakan nama `put()` sudah dibereskan: `put`=0x65e0, `putmsk`=0x6524.
- `nvar` SELESAI: dua `if` bersarang harus digabung `&&` — bentuk bersarang
  memaksa CSE bertahan melintasi cabang sehingga bingkai membesar 2 kata.
- `animvm` SELESAI: gelung yang keluar lewat JATUH-TEMBUS harus ditulis dengan
  dua `goto` ke satu label, bukan `for`/`do-while`.
- `place` tinggal 2 byte (register SI vs BX/DI murni).
- Batas keras pertama ditemukan: 1 byte di `load` (0x53ff+134) adalah artefak
  kompiler yang bergantung NAMA BERKAS, bukan sumber C — lihat `src_c/README.md`.
- Batas wilayah pustaka MC.LIB TERBUKTI di 0x69d7 (`src_c/verify/libmatch.py`),
  jadi target rekonstruksi = 27.095 byte kode game, bukan 36.976.
- ⚠ `.EXE` itu **belum tentu bisa dijalankan** — tidak ada stub lagi, tapi empat
  fungsi belum byte-exact sehingga perilakunya belum terverifikasi.
- ⭐ URUTAN KERJA yang terbukti (lihat `src_c/README.md`): perbaiki PANJANG dulu,
  lalu UJI ULANG semua penolakan lama, baru garap bentuk lokal. Selama panjang
  masih bergeser, metrik apa pun akan menghukum bentuk yang BENAR. Disiplin ini
  menaikkan `main` dari 80,1% ke 99,6% — dua perbaikan terbesarnya adalah hal
  yang sebelumnya sudah DITOLAK.
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
