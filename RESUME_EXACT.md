# Titik Mulai untuk "Persis Sama Seperti Game Asli"

> ⚠ **DOKUMEN SEJARAH (per 2026-08-02).** Tujuannya sudah tercapai: port-nya kini
> terukur identik dengan gim asli, dan rekonstruksi source C-nya byte-identical.
> Isi di bawah adalah catatan kerja dari saat hal itu masih terbuka — beberapa
> bagian "yang MASIH belum diturunkan" sudah lama selesai. Untuk keadaan faktual,
> percayai alatnya: `work/test_*.py`, `src_c/verify/execmp.py`, dan ringkasan di
> `CLAUDE.md`.

> **Untuk Bapak / sesi mendatang:** kalau tujuan bergeser dari "port Python modern" ke
> **reproduksi pixel-exact yang setia pada game asli**, JANGAN mulai dari nol. Sebagian
> besar fondasinya sudah ada. Dokumen ini adalah peta "mulai dari sini".

## Apa yang SUDAH selesai (tidak perlu diulang)

| Aset kerja | Lokasi | Guna untuk jalur exact |
|---|---|---|
| EXE ter-unpack | `work/unpack/CONTRAP_UNPACKED.EXE` | sumber kebenaran kode |
| Decompile penuh 144 fungsi | `work/ghidra_out/decompiled.c` | logika asli tiap fungsi |
| Proyek Ghidra | `work/ghidra_proj/` | navigasi/anotasi lanjutan |
| Peta kode | `CODE_MAP.md` | tahu fungsi mana ngapain |
| Format aset + decoder | `work/*.py` (RLE 0xE4, CGA) | baca aset persis |
| Format CONTRAP tervalidasi | `parse_contrap.py` | tata letak level |
| Compiler teridentifikasi | MS-C V 1.04 (model **SMALL**) | semantik int 16-bit dll |
| Multi-varian starting screen | `port/cc/draws/draws_goalG_vV.json` (19 file) | Fill Mech acak per load |
| Layar judul (=goal 128) | `port/cc/draws/draws_title.json` | judul beranimasi |

### Status port (Python/pygame) — fitur baru selesai
- **Multi-varian Fill in Mechanisms**: `start_play` pilih varian ACAK tiap load (`_pick_variant`,
  hindari-ulang spt `5035`), pakai `draws_goalG_vV.json`. Semua 6 goal × semua varian terbukti
  bisa dimenangkan (`work/test_allgoals.py`). Varian per goal: g1/3/4/6=2, g2/5=1 (g7=9 tersedia).
- **Palet part dikocok** tiap load (`random.shuffle`, meniru Fisher-Yates `3909`).
- **Layar judul beranimasi**: sprite goal 128 + teks "CREATIVE CONTRAPTIONS" + prompt kedip +
  bob halus (`work/final_title.gif`). Bukti visual: `work/final_g1_variants.png`.
- **Animasi run PER-VARIAN SELESAI** (dari eksekusi game asli, bukan tebakan): `emu.py` env
  `VARIANT=n` + `VCAP=1` menangkap frame VRAM + jalur bola untuk tiap varian (semua output
  ber-suffix `_vN`). `gen_anim.ps1` (batch 10 varian×6 goal) → `pack_anim.py` (per-varian) →
  `port/cc/anim/goalN_vV.dat` + `ballN_vV.json` + `reachN_vV.json`. Port memuat per-varian:
  MENANG → animasi run varian yg benar; GAGAL → bola varian jalan di atas build (reach dicocok
  by-POSISI krn urutan slot CONTRAP ≠ urutan draw). Bukti: `work/final_g1v1_win.gif`,
  `work/final_g1v1_fail.gif`.

## Kalau mau BYTE-identical (recompile == biner asli)
Titik mulai: `DECOMPILE_PLAN.md` §Fase 3A + §3.0.
- Butuh **Microsoft C 1.04** (Lattice-derived). Ini rintangan #1 — cari dulu sebelum
  investasi besar. Kalau tak dapat → turun ke "setara semantik + verifikasi per-instruksi"
  pakai mzretools terhadap `CONTRAP_UNPACKED.EXE`.
- Target pembanding = image ter-unpack, BUKAN file .EXE di disk (PKLITE tak perlu ditiru).

## Kalau mau PIXEL-identical (tampilan sama persis, bahasa bebas termasuk Python)
Ini jalur yang paling mungkin diminta. Titik mulai konkret:

1. **Renderer CGA eksak** — port fungsi-fungsi ini apa adanya (sudah dianalisis):
   - `FUN_1000_5cbb` — line/span XOR; tabel warna `0x1F30`, mask `0x1F10`.
   - `FUN_1000_6453` — teks font 8×8 diperbesar.
   - `FUN_1000_6524/657c/6869` — blit blok bermasker (transparansi).
   - Interleave: `addr ^ 0x2000`, `+0x50`/baris. Palet CGA-1 high-intensity.
   - Timing: sync ke vertical retrace (`in 0x3DA & 8`), ~60 Hz.
2. **Baca aset asli saat runtime** (jangan re-encode) — decoder RLE 0xE4 sudah ada.
3. **Tata letak dari CONTRAP** — record `(f2=tipe, f1=x, f0=y)`; recB=mekanisme (MECHS id),
   recC=zany (GRAPH id_major). Sudah tervalidasi (`overlay_goal1.png`).
4. **Simulasi bola/fisika** — ✅ **SUDAH DIPECAHKAN & TERVALIDASI** (2026-07-18).
   Ternyata BUKAN physics engine, melainkan **animation VM ber-skrip** di `FUN_1000_18db`:
   - Interpreter bytecode: baca opcode dari `[0x3ae]`, dispatch via tabel `CS:0x23D4`
     (17 opcode + 0xFF), skrip per-part dari file **ANIMATE**. Detail lengkap di
     `CODE_MAP.md` §Animation VM.
   - **Gerak bola diskret** (op 0x00/08/0a → `FUN_1000_2714`): bola di `base+(dx,dy)`,
     tanda pakai ambang 0xC8.
   - **Gerak parabola/proyektil** (op 0x03/0x0c → `FUN_1000_2823`): interpolasi
     `NA=-A; XBASE=(tx-fx)+tdiv(NA*N*N,100); x_i=fx+tdiv(XBASE*i,N)-tdiv(NA*i*i,100);
     y_i=fy+tdiv((ty-fy)*i,N)` (tdiv=truncate-toward-zero). Di-port di
     `port/cc/animvm.py:interp_2823`, **42/42 panggilan EKSAK** vs emulator.
   - **JEBAKAN KOORDINAT (penting) — SUDAH TERPECAHKAN 2026-08-01.** Nama kedua
     global itu TERTUKAR di dekompilasi: **`0x25e` ("bally") memegang X, `0x260`
     ("ballx") memegang Y.** Buktinya dari pemakaian, bukan tebakan:
     - `setball(0, i*10)` memasang ikon bola yang berjajar **mendatar** di pita
       atas, dan yang bertambah adalah argumen yang disimpan ke `bally`;
     - `setball()` menghitung `ballrow = y / 4` — 4 piksel per byte di CGA 2 bpp,
       jadi itu **kolom byte**, yang hanya masuk akal untuk sumbu mendatar;
     - `blend()` mengulang 8× pada `ballx` (baris) dan 3× pada `ballrow`
       (3 byte = 12 piksel), persis bentuk sprite 8 baris × 12 piksel;
     - `xform()` memilih fase pra-geser dengan `tblA[bally % 4]` — pra-geser
       4 fase di CGA memang harus **mendatar**, dan sekarang konsisten.

     Konsekuensinya: sprite bola = 4 salinan pra-geser mendatar (fase = `X % 4`,
     kolom byte = `X // 4`). Sudah diperiksa dari datanya: fase 1 memang fase 0
     yang digeser 1 piksel ke kanan, dan render fase 0 cocok EKSAK dengan VRAM
     asli (ikon pita atas). Lihat `port/cc/core/render.py:ikon_bola`.

     **Dan transform logis→layar itu TIDAK ADA.** Selama ini dicatat bahwa
     `FUN_1000_5e3b` "menerapkan transform per-part + sub-pixel, jadi posisi
     layar harus dibaca dari VRAM". Itu keliru, dan sebabnya justru nama yang
     tertukar tadi: begitu @0x25e dibaca sebagai X dan @0x260 sebagai Y,
     keduanya ternyata **koordinat layar langsung**. `xform()` hanya memilih
     fase pra-geser lalu memanggil penggambarnya.

     Diukur, bukan disimpulkan: pada frame rujukan `f0008` goal 1, VRAM berbeda
     52 piksel dari frame sebelumnya; menggambar bola di `(x=51, y=24)` — persis
     isi @0x25e dan @0x260 saat itu — membuat bedanya **nol**. Lihat
     `port/cc/core/render.py:bola` dan `CC_VRAMSEQ` di `work/emu.py`.

     Yang MASIH belum diturunkan: `prep`/`blend`/`putmsk`/`draw` (assembly +
     `blend.c`) yang menghapus jejak bola lewat halaman ganda, dan pergantian
     frame part yang dijalankan `animvm()`.
   - Parser opcode & interpolator tervalidasi 100% (`port/cc/animvm.py`,
     `work/validate_interp.py`); jalur bola per-goal cocok dgn game.
5. **Harness verifikasi frame-diff** vs DOSBox-X (lihat `DECOMPILE_PLAN.md` §Fase 3B) —
   inilah yang mengubah "mirip" jadi "terbukti pixel-identical".

## Urutan yang disarankan kalau lanjut ke exact
```
sudah ✅  unpack → decompile → format aset → format CONTRAP → render model
sudah ✅  [1] render contraption 100% pixel (draws_goal*.json via emulator)
sudah ✅  [2] animation VM + fisika bola dipecahkan (18db/2714/2823), parser+interp 100%
sudah ✅  [2b] jalur bola per-goal benar (koord layar via VRAM), GIF port_full_goal*.gif
berikut   [3] interpreter generate part-frame sendiri (op01/07/09→record ANIMATE)
          [4] turunkan transform logis→layar 5e3b (utk interaktif penuh)
          [5] integrasi SPACE di main.py + 4 mode + status bar/skor + suara
          [6] harness frame-diff vs DOSBox-X (bukti pixel-identical)
```

**Intinya:** contraption + gerak bola sudah terbukti setia pada game asli. Sisa besar =
buat interpreter mandiri (tak bergantung capture emulator) untuk interaktivitas penuh,
lalu integrasi UI/mode. Fondasi analitik (bagian tersulit) sudah berdiri.
