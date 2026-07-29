# Peta Kode — CONTRAP.EXE (Fase 3)

Hasil disassembly + decompile Ghidra atas `CONTRAP_UNPACKED.EXE`. Ini dokumen hidup;
akan bertambah seiring analisis.

## Deliverable
- `work/unpack/CONTRAP_UNPACKED.EXE` — EXE hasil unpack (47.044 byte), terverifikasi jalan.
- `work/ghidra_out/decompiled.c` — pseudo-C **seluruh 144 fungsi** (164 KB).
- `work/ghidra_out/functions.txt` — daftar fungsi + alamat + ukuran.
- `work/ghidra_proj/` — proyek Ghidra (bisa dibuka di GUI untuk navigasi).

## Tata letak memori
Ghidra memakai basis segmen `1000:` — jadi `1000:XXXX` = CS offset kita.

| Wilayah | Isi |
|---|---|
| CS `1000:000E` | Entry point crt0 (MS-C startup) |
| CS `1000:0082` | **main() game** (4183 byte) — buka file aset, kemungkinan game loop |
| CS `1000:70e8` | Runtime MS-C: parser argv + redirect (`>`,`<`,`=`), lalu panggil main |
| CS `1000:5C00–6C00` | **Subsistem render CGA** (16 fungsi) |
| CS `1000:7700–7A60` | I/O file tingkat rendah (klaster INT 21h) |
| DGROUP | seg `0x907` → file 0x9270; string & tabel data |

## Fungsi kunci yang sudah teridentifikasi

### `FUN_1000_5cbb` — primitif gambar CGA ⭐
Menggambar span/garis ber-XOR langsung ke memori video. Parameter `(x1,y1,x2,y2,warna)`.
**Mengonfirmasi model CGA Fase 2 secara independen:**
- Interleave bank: `alamat ^= 0x2000` (ganti genap/ganjil), `+= 0x50` (80 byte/baris).
- Tabel lookup: pola warna di **`0x1F30`** (4 entri), mask tepi di **`0x1F10`**.
- Gambar dengan XOR — inilah kenapa bola/garis bisa "dihapus" dengan menggambar ulang.

> **Penting untuk port:** koordinat sambungan (mis. tali antar-komponen) yang digambar
> sebagai garis **eksplisit** di sini sebagai (x1,y1,x2,y2). Ini sumber sah komposisi —
> bukan tebakan. Sebagian sambungan lain "dipanggang" ke dalam sprite (mis. puntung tali
> magenta pada sprite katrol); keduanya perlu dibedakan saat rekonstruksi.

### `FUN_1000_5d98` / `FUN_1000_5da1` — sinkronisasi vertical retrace ⭐
`in(0x3DA) & 8` — tunggu/tunggu-selesai vertical blank. **Game terikat ke refresh CGA
(~60 Hz).** Ini jawaban untuk pertanyaan timing di rencana port: frame rate harus dipin
ke retrace, bukan timer bebas.

### `FUN_1000_70e8` — runtime MS-C (argv/redirect)
Parser command-line standar MS-C (bukan logika game). Berguna untuk mengenali batas
antara runtime library dan kode game asli.

### `entry` (`1000:000E`) — crt0
Setup DS/SS ke seg 0x907, baca command tail PSP, bangun argv, panggil runtime → main.

## Katalog subsistem render (0x5C00–0x6C00)

Semua fungsi gambar terverifikasi memakai interleave CGA yang sama (`^0x2000`, `+0x50`).
**Poin kunci untuk komposisi: setiap fungsi menerima koordinat penempatan EKSPLISIT
sebagai parameter.** Tidak ada penempatan implisit/tersembunyi.

| Fungsi | Peran | Parameter penting |
|---|---|---|
| `FUN_1000_5cbb` | **Garis/span ber-XOR** | `(x1,y1,x2,y2,warna)` — untuk tali/garis penghubung |
| `FUN_1000_6453` | **Teks** (font 8×8 diperbesar jadi blok) | `(string,x,y,skala_w,skala_h,...)` |
| `FUN_1000_6524` | Blok kecil bermasker 8×12 (pointer/kursor?) | `(mask,data)` + posisi di var 0x266/0x26a |
| `FUN_1000_657c` | Blok kecil bermasker (varian) | `(mask,data,dst)` + posisi var 0x260/0x268 |
| `FUN_1000_6869` | Pengisi blok tingkat-rendah (dipanggil 6453) | dipakai text renderer |
| `FUN_1000_5d98/5da1` | Tunggu vertical retrace | — |

**Kesimpulan tentang kekhawatiran "gambar berantakan":** koordinat komposisi bukan
tebakan — semuanya parameter eksplisit ke fungsi-fungsi ini. Yang perlu dilacak
berikutnya adalah **siapa yang memanggil fungsi-fungsi ini dan dengan koordinat apa** —
yaitu main() + parser `contrap`. Sumber koordinatnya ada; tinggal diikuti.

Catatan: konstanta `0xE4` (escape RLE) tidak muncul di kode render → aset **didekode saat
dimuat** ke buffer, lalu di-blit mentah. Konsisten dgn string error "E4s in animate" yang
berada di konteks loader (bukan render).

## ⭐ Format file CONTRAP — TERVALIDASI (loader `FUN_1000_5035`)

Ini menjawab langsung "di mana tiap komponen ditempatkan". Loader membaca directory 216
byte, mencari goal terpilih, memilih varian (acak jika >1), lalu membaca blob contraption.
**Struktur diverifikasi terhadap data asli: keenam goal parse dengan checksum cocok.**

```
Directory (216 byte): 36 x { u16 id, u32 offset }
   id 1..6 = enam contraption; id berulang = varian (dipilih acak → replayability)
   (id 7 punya 9 varian, id 128 = penanda akhir)

Per contraption @offset:
   u16  goal_id                     ; validasi (== goal terpilih)
   u16  countA ; u32[countA]        ; (fungsi arrA belum dipastikan)
   u16  countB ; rec6[countB]       ; <- KOMPONEN: {u16 id, u16 x, u16 y}
   u16  countC ; rec6[countC]       ; <- kelompok kedua (mekanisme vs zany?)
   u16[countB+countC]               ; (dugaan: id jawaban benar / status slot)
```

### Makna record 6-byte — TERKONFIRMASI terhadap game asli

Record = `{ u16 f0, u16 f1, u16 f2 }` di mana:
- **f1 = X, f0 = Y** (koordinat layar, top-left sprite)
- **f2 = tipe** — untuk kelompok-1 (recB) = **id mekanisme MECHS** (100=Ramp, 110=Pulley,
  150=Spring, dst.); untuk kelompok-2 (recC) = **id_major GRAPH** (zany object/pemandangan).

Dua kelompok:
- **recB (countB) = SLOT MEKANISME** yang harus diisi pemain.
- **recC (countC) = ZANY OBJECT / pemandangan tetap.**
- **arrD** (u16 × (countB+countC)) = status per-part (1 / -1); dugaan: penanda slot kosong.

**Validasi visual (overlay ke screenshot asli, `work/overlay_goal1.png`):** untuk goal 1
"Up and At Em", marker mekanisme dari data mendarat **tepat** di komponennya di layar asli:
Ramp→kotak B, Spring→kotak D, Pulley→katrol H. Zany object juga pas (seesaw, ayam, orang
tidur). **Konvensi (x=f1,y=f0) dan makna f2 CONFIRMED end-to-end.**

> **Kesimpulan komposisi (final):** penempatan sprite sepenuhnya **data-driven** dari file
> CONTRAP berupa `(tipe, x, y)`, dan sudah **terbukti cocok dengan game asli pixel-region
> per pixel-region**. Tidak ada koordinat yang perlu ditebak — menjawab tuntas kekhawatiran
> "gambar berantakan". Rantai bukti: loader dekompilasi `FUN_1000_5035` → parser
> `work/parse_contrap.py` → overlay `work/overlay_goal1.png`.
>
> Sisa: pemetaan tepat f2→sprite varian mana (mis. mekanisme punya beberapa frame/varian di
> MECHS), dan f0/f1 = titik acuan sprite (top-left) vs. penyesuaian kecil offset.

### ⭐ Hierarki menu / navigasi ESC — TERVALIDASI 🔬

Dari decompiled main: **main menu `341a`** (pilih mode) → **level `32bb`** (Apprentice/Master)
→ **goal `3322`** (pilih tema/contraption) → **play**. Contraption selesai/ESC → `goto
switchD_0509_default` → **`3322` lagi** (kembali ke pilihan GOAL/tema, BUKAN main menu). ESC di
goal (`3322`==-1) → `switchD_10e0_default` = `341a` (main menu). Port meniru: `_back_to_goal()`
dipakai saat menang (PLAYANIM win-ESC) & ESC saat PLAY → state=GOAL; GOAL ESC → MENU. Tes
`work/test_nav.py`.

### ⭐ Dua sumber pengacakan "starting screen" (Fill in Mechanisms) — TERVALIDASI 🔬

Untuk goal yang sama, layar awal berbeda tiap load karena **dua** pengacakan (bukan satu):

1. **Varian kontraption acak — `FUN_1000_5035` baris 2990–3009.** Hitung entri direktori
   `id==goal` → `FUN_1000_5a5b(local_3a)` pilih acak, hindari ulang varian terakhir (`0x1e30`).
   Jumlah varian per goal: **1:2, 2:1, 3:2, 4:2, 5:1, 6:2, 7:9** (dump `work/dump_dir.py`).
2. **Palet part dikocok (Fisher–Yates) — `FUN_1000_3909` baris 2082–2091** (saat `0x794==1`),
   dipanggil via `3f0f` (2250) & `2e90` (1485) dalam loop Fill Mech (278–279). Mengocok array
   indeks part `0x2ea` + urutan tampil `0x7fa`, termasuk pengecoh.

Pemisah mode (jangan tertukar): `10fd` (subset part salah) = **Mix Up saja** (baris 381);
`1200` (acak zany, `0x836/0x838`) = **Fill Zany saja** (baris 236). Fill Mech tak pakai keduanya.
Detail naratif: lihat `GAME_GUIDE.md` §3 "Bagaimana starting screen di-generate".

### ⭐ Review "how it works" = DEMO CONTRAPTION goal 7 (per-mekanisme) — TERVALIDASI 🔬

Alur Review (main baris 433–481): `2fde`(intro) → `3c4f`(browse pilih mekanisme, set `0x51c`)
→ `3020`(detail: judul+sprite@144,48+teks). Di 3020, SPACE→`3734` (animasi kecil) lalu RETURN
0x20 → **main memuat CONTRAPTION lalu menjalankannya**: `5035` + loop `498c`+`3f0f`+`18db`
(baris 454–481), non-interaktif (ESC=menu, ENTER=kembali browse, SPACE=ulang). Contraption-nya
dari **`0x3b2=7`** (baris 198) = **CONTRAP goal 7**, yg punya **9 varian = 9 mekanisme
BERURUTAN** (var0=Inclined Plane 101 … var4=Pendulum 130 … var8=Spring 150; cocok 1:1 dgn
urutan MECH_CATEGORIES). Jadi demo selalu memuat mekanisme terpilih. **Inilah alasan goal 7
punya 9 varian.**

BUG lama port (2×): (1) SPACE putar contraption goal biasa → pendulum tak muncul; (2) "fix"
salah ke-2 = animasi sprite mekanisme di tempat. BENAR: `start_review_demo(rev_i)` putar
`goal7_v{rev_i}.dat` (animasi contraption). Animasi 9 varian goal 7 ditangkap `VCAP=1 VARIANT=v
emu.py 7 2` → `pack_anim.py` (VARIANTS incl 7) → `port/cc/anim/goal7_vV.dat`. Bukti
`work/proof_pendulum_demo2.gif` + mapping 9/9 OK (`work/proof_review_demo2.py`).

### ⭐ Sprite di-render OPAQUE (bukan colorkey) — TERVALIDASI 🔬

Blitter asli `FUN_1000_672f` (baris 4219/4227) menulis SEMUA byte sprite langsung ke VRAM —
**tanpa mask/colorkey**. Sprite = persegi OPAQUE; area "kosong" kebetulan cyan = warna latar,
jadi menyatu; saat bertumpuk, sprite belakangan MENIMPA yg depan. BUG lama port: `_sprite_surface`
pakai `set_colorkey(cyan)` → piksel cyan jadi transparan → saat sprite di atas kotak abu/sprite
lain, cyan HILANG ("cyan menghilang", gambar berantakan). FIX: hapus colorkey (opaque). Diverifikasi
vs VRAM emulator: goal1 v1 beda hanya 2530/64000 piksel (status-bar emulator). Lihat
`work/cmp_vram.py`, `work/cmpvram_g1_v1.png`. Bilah status Fill dipindah ke y=166 (spt game clear
`6869(0,0xa8,..)`=168) agar tak menutupi slot.

### ⭐ Katalog komponen (referensi) — `work/gen_catalog.py`
`work/catalog_mechs.png` (15 sprite mekanisme + nama + id) & `work/catalog_zany.png` (67 objek
zany/pemandangan GRAPH + id). Dipakai untuk menyebut komponen saat diskusi.

### ⭐ Palet Fill & pencocokan — TERVALIDASI 🔬

- **Palet part = STRIP horizontal semua opsi** (bukan satu-per-satu). Dibangun `3909`
  (dedup (major,minor) dari katalog `0x73a`, dikocok Fisher-Yates saat `0x794==1`), digambar
  `FUN_1000_4e3e` (baris 2892: tiap entri di x menaik += lebar sprite `53ff`). Port meniru:
  `_palette_strip()` gambar semua opsi berjajar + penunjuk MENGHADAP ATAS pd yg terpilih.
- **Pencocokan = EXACT TYPE**, `FUN_1000_18db` baris 976:
  `param_5[slot] (tipe pilihan pemain) != param_3[slot*6+4] (tipe benar dari CONTRAP)` → GAGAL,
  set `0x842=0xffff`, `0x844`=indeks kotak salah. (Port pakai 9 IKON kategori = 9 mekanisme
  spt Review; cocok by-kategori sehinga sub-varian tipe mis. 112→Pulley tetap solvable.)
- CATATAN bug (diperbaiki): palet satu-per-satu `< Screw >` bikin user tak menemukan yg cocok
  → diganti STRIP semua opsi (terlihat & bisa dipilih). Segitiga penunjuk Review dibalik ke ATAS.
- CATATAN bug (diperbaiki): ikon palet tampil `first_of_major(id_kategori)` (mis. 100) padahal
  yg ditempatkan tipe spesifik slot (101) → ikon ≠ gambar hasil. FIX: entri palet = 4-tuple
  `(nama, ids, arch, sprite_idx)`; sprite_idx = gambar EKSAK dari slot contraption ini
  (`catspr[kategori]`), dan `_place` menaruh `s["sprite"]=pidx`. Jadi ikon palet == hasil taruh.
  Diverifikasi `work/proof_palette.py`: 0 mismatch semua goal/varian; bukti `proof_g3_palette.png`.

### ⭐ LAYAR JUDUL = CONTRAP goal 128 — TERVALIDASI 🔬

Layar judul ("CREATIVE CONTRAPTIONS") **bukan** gambar layar-penuh terpisah: komposisi
sprite-nya adalah entri **CONTRAP id=128** (ayam di sarang, gajah, tumpukan kaleng, kotak
lever + spring, tiga per). Render goal 128 cocok **persis** dengan `sceenshots/Title.png`
(lihat `work/render_128.png`). Teks judul digambar oleh font-drawer (`6453`) — TIDAK dirender
emulator — jadi port menumpuk teksnya sendiri. Tak ada draw 672f sebelum contraption pertama
(`title672`=0), memastikan judul dibuat lewat mekanisme contraption yang sama.
**ANIMASI judul**: rekaman goal-128 asli janggal → diganti animasi bola CUSTOM Rube-Goldberg
(`build_title_anim` di main.py, sesuai deskripsi user). Dua jalur bergantian, loop:
- KIRI: ayam →(jatuh) 2 DRUM(id80, tiap pantul tulisan **BOOM!**) → LEVER(id141) → lever
  MELONTAR bola ke atas → GAJAH.
- KANAN: gajah →(jatuh) 3 CANGKIR di atas tiga per(id79) → SPRING box(id150) → spring
  MELONTAR bola ke atas → AYAM.
Titik kontak selaras draws_title. Reaksi: swap frame lever 26↔27, spring box 28↔29, gajah
465↔466, ayam bob; bola tersembunyi saat "ditelan" hewan. BOOM! hanya di drum (kiri).
Bukti `work/title_rg.gif`, `work/rg_*.png`.

### Pipeline capture per-varian (emulator) — cara pakai

`work/emu.py` sekarang: env `VARIANT=n` → hook `5a5b` (dipanggil dari `5035`) balikan n →
loader muat varian n deterministik. Tangkapan adegan statis (`scene672`, dedupe posisi ambil
pose pertama) → `work/emu_caps/draws_goalG_vV.json`. Layar judul → `title_sprites.json` (via
goal 128). Batch: `work/gen_variants.ps1` (19 varian), pasang: `work/install_variants.ps1`
(v0 = referensi terverifikasi, v1+ = tangkapan) → `port/cc/draws/draws_goalG_vV.json`.

**Animasi run per-varian**: `VARIANT=n VCAP=1` → semua output ber-suffix `_vN` (vframes,
ballscreen, anim, draworder). `gen_anim.ps1` batch → `pack_anim.py` (per-varian) →
`port/cc/anim/goalN_vV.dat` (frame VRAM 2bpp+zlib) + `ballN_vV.json` (jalur bola layar) +
`reachN_vV.json` (indeks reach per slot, dicocok by-POSISI di port). Semua dari eksekusi
game asli, tanpa tebakan.

## Rekonstruksi dari aset (opsi #1) — BERHASIL sebagian

`work/render_contraption.py` merekonstruksi goal 1 dari aset kita di posisi data →
`work/reconstruct_goal1.png`, perbandingan di `work/compare_goal1.png`.

**Cocok dgn asli:** orang tidur, katrol, kotak ramp/pegas, seesaw, spiral, sarung tangan,
ayam — posisi semua tepat. Pipeline (decode aset + posisi CONTRAP + blit) TERBUKTI.

**Belum cocok:** figur kiri-atas & elemen menggantung → salah pilih frame. Penyebab:
kode ambil `GRAPH[id_major][0]` (frame pertama), padahal varian statis yang benar mungkin
id_minor lain. **Refinement berikutnya: pemilihan frame/varian yang tepat** (mungkin
dari field lain di record CONTRAP, atau id_minor default). Ball physics juga belum.

## Logika gameplay (dalam main `FUN_1000_0082`) — teridentifikasi
Loop utama mengiterasi semua part (mekanisme + zany):
- Jawaban benar tiap slot = **field2 record** (`param_3 + i*6 + 4`).
- Pilihan pemain dibandingkan; kalau salah → set flag, tampilkan huruf slot
  (`i + 0x41` = 'A','B',...) + string `0x9dd`/`0xa01` = "... does not work".
- Skor dinaikkan (mis. +500 di 0x730) sesuai mode (0x792) & kondisi.
- Sprite diambil dari **direktori grafis di memori**: zany dari tabel `@0xC`, mekanisme
  dari tabel `@0x1B0`, di-index lewat tabel indireksi (param_4/param_8/param_10).

## ⚠️ Pemilihan frame/varian — sebagian terpecahkan
`id_major` = KATEGORI; `id_minor` = objek/varian berbeda (mis. id1: minor1=burung,
minor2=orang-treadmill, minor3=lain). Jadi memilih record `[0]` SALAH. Sprite yg benar
dipilih via tabel indireksi (@0xC / @0x1B0). **Aturan pasti pembangunan tabel indireksi
belum ditelusuri** — ini polish untuk jalur pixel-exact, bukan blocker jalur port Python.

## Fungsi I/O aset (dipakai loader)
- `FUN_1000_6b57(nama, mode)` — buka file (return handle / -1)
- `FUN_1000_6d31(handle, buf, n)` — baca n byte
- `FUN_1000_6e8b(handle, off_lo, off_hi, whence)` — seek
- `FUN_1000_6fb6(handle)` — tutup
- `FUN_1000_5a5b(n)` — random 0..n-1 (pemilih varian)

## ⭐ "Fisika bola" = VM animasi ber-skrip (BUKAN simulasi fisika)

Temuan besar: bola yang "berjalan melewati mesin" bukan physics engine, melainkan
**interpreter bytecode** atas skrip animasi (file `ANIMATE`). Loop interpreter ada di
`FUN_1000_18db` (~baris 1052-1069 decompiled.c):
```
ptr = animasi_script            // 0x3ae
while (*ptr != -1 && *ptr != 0) {
    op = *ptr++; 
    cari op di tabel dispatch; panggil handler-nya
}
```
Manual bilang "gerakan mendekati hukum fisika" — ternyata itu **animasi yang dibuat
tangan per contraption**, bukan fisika hidup. Menjelaskan file `ANIMATE` (241 skrip).

### Tabel opcode VM @ CS:0x23D4 (file 0x25D4) — 17 opcode + terminator
Tabel `{u16 opcode, u16 handler}` di segmen KODE (const, khas MS-C). Handler = near offset:

| op | handler | op | handler | op | handler |
|----|---------|----|---------|----|---------|
| 0x00 | 0x1F11 | 0x07 | 0x1F70 | 0x0E | 0x2334 |
| 0x01 | 0x1F49 | 0x08 | 0x1F3B | 0x0F | 0x233C |
| 0x02 | 0x1F8D | 0x09 | 0x1F79 | 0x10 | 0x1D09 |
| 0x03 | 0x1FAC | 0x0A | 0x1F32 | 0x11 | 0x1E85 |
| 0x04 | 0x2280 | 0x0C | 0x21E1 | 0xFF | 0x23D1 (term) |
| 0x05 | 0x2305 | 0x0D | 0x2321 | | |
| 0x06 | 0x2315 | | | | |

(0x0B tidak ada.)

### Semantik opcode (dari disassembly handler) — behavioral decode
| op | perilaku | operand |
|----|----------|---------|
| 0x00 | gambar DAFTAR sprite (loop s/d 0xff) via draw `0x2714` (x=bp+22,y=bp+24) | list |
| 0x01 | gambar DAFTAR sprite (loop s/d 0xff) via draw `0x278e` (+bp+4a,+20) | list |
| 0x02 | suara/delay via `0x2692`; byte<0 → kembali | 1 byte |
| 0x03 | gerak/posisi, koordinat bertanda (>=0xc8 → −0x100) | ≥2 byte |
| 0x05 | gambar kursor/pointer via `0x6524` (string 0x9c5) | — |
| 0x06 | reset kursor (0x266=0x262=0x140) | — |
| 0x07 | reset kursor + gambar 1 sprite via `0x278e` | — |
| 0x08 | gambar 1 sprite via `0x2714` | — |
| 0x09 | gambar 1 sprite via `0x278e` | — |
| 0x0A | reset kursor + gambar via `0x2714` + loop | — |
| 0x0C | gerak/posisi (mirip 0x03), koordinat bertanda | ≥2 byte |
| 0x0D | **MULAI LOOP** — simpan posisi skrip (bp+58), reset counter | word |
| 0x0E | set flag loop (bp+5c=1) | — |
| 0x0F | kontrol loop + tunggu vertical-retrace (`0x1791`) | — |
| 0x10 | (0 operand) | — |
| 0x11 | timer/skor via `0x2504`, operand 4-byte (2 word) | 4 byte |
| 0xFF | terminator skrip | — |

### ✅ UPDATE 2026-07-18 — GRAMMAR & FISIKA BOLA TERVALIDASI 100% (via emulator)
Grammar opcode & panjang operand kini **terbukti 68/68 skrip cocok EKSAK** di keenam goal,
diverifikasi lewat emulator Unicorn (`work/emu.py` → true_len saat dispatch baca 0xFF) vs
parser Python (`port/cc/animvm.py`). Koreksi/penajaman atas dugaan lama:
- **op0x0C & op0x03 = 2 byte** (diukur via probe `0x3ae`, bukan variabel).
- **op0x0F = 1 byte** (hitungan loop). op0x0D/0E/0F = **LOOP TERHITUNG**: op0D tanda awal
  body, op0F+byte-hitungan ulang body N kali; bila mode-tunggu (op0E) aktif → tunggu tombol
  (SPACE/ENTER/ESC maju). Tabel key-dispatch @0x235a.
- **op0x04**: mode1=6 byte; mode2/3=stream s/d **0xFF 0xFF** ganda; lainnya=0 byte.
- **op0x00/08/0A → `FUN_1000_2714`** (bola diskret): baca 2 byte `(dx,dy)` bertanda
  (ambang 0xC8) → bola di `base+(dx,dy)`.
- **op0x03/0x0C → `FUN_1000_2823`** (gerak PARABOLA/proyektil): interpolasi fixed-point,
  `A=operand[0], N=operand[1]`, from=posisi kini, to=chaining antar-part. Formula EKSAK
  (port `interp_2823`, 42/42 cocok): `NA=-A; XBASE=(tx-fx)+tdiv(NA*N*N,100);
  x_i=fx+tdiv(XBASE*i,N)-tdiv(NA*i*i,100); y_i=fy+tdiv((ty-fy)*i,N)` (tdiv=trunc-to-zero).
  `FUN_1000_29b0` = versi linear sederhana (tanpa A).
- **JEBAKAN KOORDINAT ⚠️:** `0x260`(x)/`0x25e`(y) = koord LOGIS PER-PART, BUKAN posisi
  layar. Drawer `FUN_1000_5e3b` menerapkan transform per-part + sub-pixel (tabel 0x2cc/0x2d4,
  buffer 0x29c/0x2b4). Mem-plot koord logis sbg layar → jalur bola ZIGZAG (bug, sudah
  diperbaiki). Untuk RENDER: baca posisi layar SEBENARNYA dari VRAM (diff sebelum/sesudah
  26ae) → `ballscreen_goal*.json`. Bukti visual: `work/ballpath_screen_g*.png`.
- Skrip per-part & param terekstrak: `work/emu_caps/scripts_goal*.json`, `interp_goal*.json`,
  `ballbases_goal*.json`, `ballscreen_goal*.json`, `anim_goal*.json`. Render port:
  `port/anim_full.py` → `work/port_full_goal*.gif` (contraption + part + bola, per-frame).

### GRAMMAR ANIMATE — (catatan lama) tervalidasi 213/240 (89%) statis; kini 100% via emulator
Sub-fungsi gambar sudah dibedah:
- `0x2714` = konsumsi **2 byte (dx,dy)** → gambar/gerak BOLA di posisi relatif (koordinat
  bertanda: byte ≥0xc8 → −0x100). Dipakai op 0x00/0x08/0x0A.
- `0x278e` = konsumsi **1 byte (indeks sprite)** → gambar frame dari direktori grafis.
  Dipakai op 0x01/0x07/0x09.
- `0x2692` = **delay** (busy-wait `while(*0x2e4>0)`, di-countdown timer ISR) → op 0x02.

Grammar operand per opcode (untuk parser/interpreter port):
| op | konsumsi byte |
|----|---------------|
| 0x00 | daftar item **2-byte (dx,dy)** s/d 0xff (BOLA bergerak) |
| 0x01 | daftar item **1-byte (sprite idx)** s/d 0xff (animasi frame) |
| 0x02 | 1 (delay N tick) |
| 0x03, 0x0C | 2 (posisi bertanda) |
| 0x04 | **variabel per mode**: mode0=0, mode1=6, mode2/3=daftar s/d **0xff 0xff** (SUARA) |
| 0x05, 0x06, 0x10 | 0 |
| 0x07, 0x09 | 1 (1 sprite) |
| 0x08, 0x0A | 2 (1 gerak bola) |
| 0x0D, 0x0E, 0x0F | kontrol loop — **stateful** (0x0D simpan posisi, 0x0F loop-back); konsumsi bergantung state |
| 0x11 | 4 (2 word; timer/skor) |
| 0xFF | terminator skrip |

Parser: `work/validate_anim3.py`. **27 skrip sisa (11%) gagal di opcode kontrol-loop
(0x0D/0E/0F)** yang konsumsinya bergantung iterasi runtime — paling pas dituntaskan saat
interpreter dijalankan (amati titik desync), bukan parsing statis.

## STATUS: arsitektur game TERPETAKAN LENGKAP + VM animasi TERPORT & TERVALIDASI
Boot/menu → load aset → load contraption (posisi+tipe) → gambar slot (kotak/sprite) →
pilih part (UI kursor) → cocokkan vs jawaban + skor + feedback huruf → timer bar + suara →
**jalankan = VM animasi ber-skrip**. Tidak ada subsistem besar yang tersisa tak dikenal.

**Port (Python) — status:** contraption render 100% pixel (6 goal); parser VM 17 opcode
100%; interpolator bola 100%; jalur bola benar (koord layar VRAM); animasi run sinkron
(`work/port_true_goal*.gif`). **KE-4 MENU JALAN & BERBEDA** (`python port/main.py`):
(0) **Review Mechanisms** = ENSIKLOPEDIA (intro `2fde` → browse 9 mekanisme dgn panah `3c4f`
→ detail `3020`: judul+sprite@144,48+definisi+contoh, TEKS & POSISI EKSAK diekstrak dari
tabel DGROUP 0x14f6[idx]/0x1508[idx] via 3769; layout di `port/cc/anim/review_layout.json`);
SPACE=demo. (1) **Fill in Mechanisms** = isi kotak mekanisme (9 KATEGORI, cocok by-kategori),
salah→bola gagal di kotak, benar→"IT WORKS!"; (2) **Fill in Zany Objects** = isi kotak zany
dgn kandidat berputar DI DALAM kotak (`2d11`/`4094`/`42ca`, bukan strip bawah); (3) **Mix Up**
= LEVEL→GOAL, isi mekanisme+zany, TIMER + bonus waktu.
CATATAN emulator: render sprite (672f) tapi TIDAK teks font (6453/381a) → utk layout teks,
EKSTRAK tabel 381a/3769 dari DGROUP (work/emu.py OBSERVE=review|zany|mixup). 36ef=flush kbd.
Kode: `port/main.py` (MECH_CATEGORIES, REVIEW_DATA/review_layout, start_play fill=mech|zany|both).
Frame ter-pack `port/cc/anim/goal*.dat`. SISA: render mandiri interaktif (composite+erase);
interpreter generate part-frame sendiri (op01→record ANIMATE); transform logis→layar 5e3b;
status bar/skor + suara. Kode kunci: `port/main.py`, `port/cc/animvm.py`, `port/anim_full.py`,
`work/emu.py` (emulator+capture), `work/validate_interp.py`, `work/pack_anim.py`.

### FIX VARIAN-MISMATCH (2026-07-21) — design ≠ run
Gejala: layar DESIGN dan layar RUN (setelah SPACE) menampilkan contraption BERBEDA
(`sceenshots/Error_01.png` vs `Error_02.png`). Akar: **indeks varian `draws_goalN_vI.json`
(design) TIDAK sejajar dengan `port/cc/anim/goalN_vI.dat` (animasi run)**. Untuk goal 1:
`draws_v0` (seesaw) sebenarnya berpasangan dengan `goal1.dat` legacy (198 frame), `draws_v1`
dengan `goal1_v1.dat`, sedangkan `goal1_v0.dat` (monyet-roket) **orphan** — tak punya draws.
FIX: pilih animasi lewat **pencocokan KONTEN frame-0**, bukan indeks varian —
`Game._match_anim(gid, design_draws)` (`port/main.py:507`), dipanggil dari
`start_review(..., from_play=True)`; `decode_dat(fp, maxframes=1)` agar cek frame-0 murah.
Bukti: diff seluruh goal/varian = 316–320 (baseline match ketat), `TOTAL bad = 0`
(sebelumnya goal1 v0 = 1365, goal4 v0 = 936); diverifikasi juga via navigasi keyboard normal.
**Pelajaran:** dua sumber data ber-indeks sama belum tentu sejajar — buktikan lewat isinya.

## Target analisis berikutnya
1. **`FUN_1000_0082` (main)** — alur puncak: urutan menu, pemuatan aset, game loop.
2. **Sprite blitter** — fungsi di 0x5C00–0x6C00 yang menyalin sprite `MECHS`/`GRAPH`
   ke layar (beda dari line-drawer 5cbb). Di sinilah koordinat penempatan sprite.
3. **Loader `contrap`** (sekitar CS 0x5240) — parser definisi level: memetakan record
   6-byte `CONTRAP` ke tata letak contraption. **Ini kunci komposisi.**
4. **Simulasi bola/fisika** — "gerakan bola mendekati hukum fisika" (manual); cari loop
   yang meng-update posisi bola + deteksi tumbukan dengan komponen.
5. **Dekoder RLE 0xE4** — fungsi yang membaca aset (konfirmasi silang dengan Fase 2).
