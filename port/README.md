# Creative Contraptions — Port Python (pygame)

Port modern dari game DOS 1985, dibangun di atas hasil reverse-engineering
(lihat `../CODE_MAP.md`, `../ARCHITECTURE.md`).

## Aset: sekali impor, lalu mandiri
Port **tidak** membaca folder game asli saat dijalankan. Sekali saja:

```
python port/import_assets.py                 # cari folder game otomatis
python port/import_assets.py <folder_game>   # atau tunjuk manual
python port/import_assets.py --check         # periksa bundel
```

Skrip itu menyalin 4 berkas yang benar-benar dipakai (`GRAPH`, `MECHS`, `ANIMATE`,
`CONTRAP`) ke `port/cc/data/`. Setelah itu **folder `port/` berdiri sendiri** — folder game
asli boleh dipindah, di-rename, atau dihapus. `run_port.bat` menjalankan impor ini otomatis
kalau bundelnya belum ada.

`port/cc/data/` **tidak ikut ke git** — repo berisi kode, bukan berkas game. Pengguna
menyediakan salinan game miliknya sendiri.

## Prinsip
- **Baca aset ASLI saat runtime** (GRAPH/MECHS/ANIMATE/CONTRAP) — tanpa re-encode,
  jadi grafis setia *by construction*. Bundel di atas adalah salinan mentah, bukan
  konversi, supaya prinsip ini tetap berlaku.
- **Framebuffer CGA 320×200** internal (sumber kebenaran) → tampil dengan
  **integer-nearest scaling** + DPI-aware (tajam, tidak berantakan; lihat diskusi scaling).
- **Komposisi dari data** — posisi tiap komponen `(x,y,tipe)` dibaca dari file CONTRAP,
  bukan ditebak (tervalidasi terhadap game asli).

## Struktur
```
port/
  main.py            # aplikasi: state machine TITLE→MENU→LEVEL→GOAL→PLAY→PLAYANIM, 4 mode
  montage_goals.py   # render 6 contraption -> montage (bukti)
  anim_full.py       # rakit animasi run jadi GIF (bukti)
  cc/
    cga.py           # palet CGA-1 low-intensity bg-biru (EKSAK), framebuffer, scaling
    assets.py        # decoder RLE 0xE4, arsip record, parser CONTRAP
    text.py          # teks 8×8
    animvm.py        # port VM animasi: parser 17 opcode + interpolator parabola (2823)
    anim.py          # pemutar waypoint (jalur lama)
    draws/           # daftar draw per goal/varian (capture emulator) — layar DESIGN
    anim/            # frame run ter-pack goalN_vV.dat + ballN_vV.json + reachN_vV.json
```

## Jalankan
```
python port/main.py            # jendela (ESC/Q keluar)
python port/main.py --shots    # render tiap layar ke PNG (headless)
python port/montage_goals.py   # montase keenam goal
python work/test_allgoals.py   # regresi: semua goal × varian bisa dimenangkan
python work/test_nav.py        # regresi navigasi menu
```

## Status saat ini
✅ Muat aset asli, decode RLE+CGA, parser CONTRAP.
✅ Render statis **keenam contraption** dari data (cocok dgn game asli — `montage_goals.png`).
✅ Scaling integer-nearest, DPI-aware, toggle aspek 4:3.
✅ **Alur menu** (state machine): TITLE → MENU(4 mode) → LEVEL → GOAL → PLAY,
   string asli, navigasi Up/Down/ENTER/ESC (`menu_flow.png`).
✅ **Mode "Fill in Mechanisms" BISA DIMAINKAN**: slot kosong (A/B/C), pemilih part
   (←/→ cycle 9 mekanisme), tempat (ENTER), cek vs jawaban benar, feedback
   "Mechanism X does not work", **skoring sesuai game** (10000/5000/2500 + bonus 100000).
   In-game controls: ←/→ pilih part, ↑/↓/TAB pindah slot, ENTER tempat, ESC keluar.

✅ **"Jalankan contraption" (SPACE)**: bola beranimasi HALUS (interpolasi kontinu) melewati
   mesin, mengikuti waypoint dari file ANIMATE asli (skrip per-part, id_major=tipe, relatif
   ke posisi part). Interpreter VM di `cc/anim.py`.

✅ **Palet warna EKSAK** (CGA palette-1 low-intensity, bg biru — disampel dari game asli).
✅ **Scaler = pygame.SCALED** (integer nearest-neighbor, DPI-aware — logika sama dgn DOSBox 3x/4x).
✅ **TIDAK ADA LAGI DATA TANGKAPAN DI JALUR PORT.** Layar, animasi, slot, palet, jalur
   bola — semuanya dibangkitkan dari berkas aset oleh `cc/core/`. `cc/draws/*.json` dan
   `cc/anim/*.dat` tidak dibaca sama sekali; keduanya kini hanya PEMBANDING.
✅ **Layar diam PIXEL-IDENTIK**: 7 layar (goal 1..6 + judul 128) = **448.000/448.000
   piksel** vs tangkapan VRAM emulator, diukur dari dalam port lewat `pygame.Surface`.
✅ **Animasi dibangkitkan mesin `animvm()`** (`cc/core/vm.py`): **381/402 bingkai
   byte-identik**, 99,9988% piksel. Goal 4, 5, 6 dan layar judul **100% bingkai**.
✅ **Varian dipilih lewat RNG yang sama dengan gim** (`cc/core/pick.py`) — LCG
   `seed*0x3E85 + 0x3619`, termasuk undian yang ditolak lalu diulang.
✅ **KE-4 MODE JALAN**: Review Mechanisms (ensiklopedia 9 mekanisme + demo goal 7),
   Fill in Mechanisms (varian acak tiap load), Fill in Zany Objects, Contraption Mix Up
   (timer + bonus waktu). Level Apprentice / Master Builder tersedia.
✅ **Layar judul ASLI dan bergerak**, termasuk teks "CREATIVE CONTRAPTIONS" — teks itu
   digambar opcode `0x11` di dalam skrip animasi, bukan oleh layar statis.
✅ **Bilah status, skor, timer, petunjuk, dan pesan akhir goal** dari fungsi aslinya
   (`cc/core/hud.py`). Skoring dibetulkan: satu penilaian per kontraption dari penghitung
   kesalahan, dan **hanya di Contraption Mix Up** — dua mode isian lain memang tanpa skor.
✅ **Navigasi sesuai hierarki asli**: selesai/ESC di contraption → kembali ke pilihan GOAL
   (bukan menu depan); hanya GOAL-ESC yang ke menu depan.

## Belum (roadmap)
- [ ] **21 bingkai animasi** (goal 1, 2, 3) belum byte-identik. Record dan posisinya sudah
      terbukti benar; yang belum diturunkan adalah `prep`/`blend`/`putmsk`/`draw` —
      interaksi hapus-bola dengan blit yang datang sesudahnya.
      ⚠ Enam percobaan di sumbu itu sudah gagal; hipotesis "salinan latar basi" bahkan
      menurunkan hasil 381/402 → 57/402. Baca catatan di `cc/core/adegan.py` dulu.
- [x] Suara PC-speaker — `cc/core/bunyi.py`; nada = frekuensi Hz, not 3 byte.
- [ ] Dua sisa data tangkapan, keduanya ANTARMUKA bukan render kontraption:
      `cc/anim/review_layout.json` (tata letak Review Mechanisms) dan `cc/anim/icons/`.

> Catatan sejarah: jebakan lama *"indeks varian `draws_*` tidak sejajar dengan `*.dat`"*
> sudah tidak ada. `_match_anim()` yang mencocokkan animasi ke layar design lewat isi
> bingkai-0 sudah dibuang — adegan dan animasi kini lahir dari data yang sama, oleh undian
> yang sama, jadi tidak ada yang perlu dicocokkan.
