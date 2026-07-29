# Creative Contraptions — Port Python (pygame)

Port modern dari game DOS 1985, dibangun di atas hasil reverse-engineering
(lihat `../CODE_MAP.md`, `../ARCHITECTURE.md`).

## Prinsip
- **Baca aset ASLI saat runtime** (GRAPH/MECHS/MISC/ANIMATE/CONTRAP) — tanpa re-encode,
  jadi grafis setia *by construction*.
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
✅ **Pemilihan sprite BENAR & deterministik** — bukan lagi ditebak/dicocokkan; daftar draw
   `(arch, idx, x, y)` di-capture dari eksekusi game asli via emulator Unicorn (`work/emu.py`,
   hook blitter `672f`) → `cc/draws/draws_goal*.json`. Render 6 contraption **100% pixel-match**.
✅ **KE-4 MODE JALAN**: Review Mechanisms (ensiklopedia 9 mekanisme + demo goal 7),
   Fill in Mechanisms (varian acak tiap load), Fill in Zany Objects (kandidat berputar di dalam
   kotak), Contraption Mix Up (mekanisme + zany, timer + bonus waktu). Level Apprentice /
   Master Builder tersedia.
✅ **Animasi run per-varian** dari eksekusi game asli (`cc/anim/goalN_vV.dat`): MENANG → animasi
   varian yang benar; GAGAL → bola berhenti di titik gagal.
✅ **Layar judul beranimasi** (rantai Rube-Goldberg) + palet part dikocok tiap load.
✅ **Navigasi sesuai hierarki asli**: selesai/ESC di contraption → kembali ke pilihan GOAL
   (bukan menu depan); hanya GOAL-ESC yang ke menu depan.
✅ **Fix design≠run (2026-07-21)**: animasi dipilih lewat pencocokan konten frame-0
   (`_match_anim`), bukan indeks varian — indeks `draws_*` dan `*.dat` ternyata tidak sejajar.

## Belum (roadmap)
- [ ] **Interpreter generate part-frame sendiri** (op 0x01/0x07/0x09 → record ANIMATE) agar
      animasi run tak bergantung data capture emulator. ← BERIKUTNYA
- [ ] **Transform logis→layar `FUN_1000_5e3b`** (posisi bola sub-pixel eksak; kini pakai posisi
      layar hasil capture VRAM karena transform belum diturunkan).
- [ ] **Render mandiri yang sync** — butuh mesin composite + erase jejak bola seperti game asli.
- [ ] Fase roll-in pada run GAGAL (bola kini langsung muncul di titik pertama).
- [ ] Status bar/skor lengkap + suara PC-speaker (op 0x04 sudah diparse).
- [ ] (opsional) harness frame-diff vs DOSBox-X = bukti pixel-identical.
