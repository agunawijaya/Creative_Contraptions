# src_c — rekonstruksi source C yang bisa dikompilasi ulang

Tujuan: menulis ulang kode game sebagai **source C asli** yang, dikompilasi dengan
Microsoft C 1.04 (kompiler yang dipakai tahun 1985), menghasilkan **byte yang sama persis**
dengan `CONTRAP_UNPACKED.EXE`.

Ini BERBEDA dari `work/ghidra_out/decompiled.c` — berkas itu keluaran Ghidra untuk dibaca
manusia (862 tipe `undefined`, 217 variabel `in_*`, 0 `#include`), tidak bisa dikompilasi.

## Isi
```
src/      berkas .c hasil rekonstruksi (satu fungsi/kelompok per berkas)
          gdata.c  — DIBANGKITKAN (build/gendata.py), rekonstruksi segmen DATA
          stubs.c  — DIBANGKITKAN, definisi kosong untuk fungsi yang belum digarap
asm/      berkas .asm untuk fungsi ASSEMBLY tulisan tangan (tidak bisa jadi C)
build/    compile.ps1 — kompilasi satu berkas lewat MS C 1.04 di dalam DOSBox-X
          masm.ps1    — rakit satu .asm lewat MASM 1.27 (1984) di DOSBox-X
          buildall.ps1 — lint + kompilasi semua
          link.ps1    — LINK semua .OBJ + MC.LIB -> out/CONTRAP.EXE
          gendata.py  — bangkitkan src/gdata.c dari DGROUP biner asli
verify/   objcode.py  — banding byte .OBJ kita vs biner asli
          symcheck.py — VERIFIKASI IDENTITAS SIMBOL (target call + alamat
                        global). objcode.py mem-wildcard slot relokasi, jadi
                        fungsi bisa "COCOK" padahal memanggil fungsi yang
                        SALAH. WAJIB dijalankan bersama verifyall.py.
          verifyall.py — tabel status semua fungsi + segmen DATA
          dgroup.py   — alat segmen DATA (dump, string, banding)
          symbols.py  — PUBDEF vs EXTDEF, cari simbol yang belum ada
          truesize.py — ukuran fungsi sebenarnya (functions.txt sering kurang)
          lintsrc.py  — deteksi kode tertelan komentar blok
out/      keluaran build (.OBJ, .EXE, .MAP, log) — tidak diversikan
```

## Cara pakai
```
pwsh src_c/build/compile.ps1 -Name delay          # -> src_c/out/delay.OBJ
python src_c/verify/objcode.py src_c/out/delay.OBJ 2692 28

pwsh src_c/build/buildall.ps1                     # semua .c -> .OBJ
pwsh src_c/build/link.ps1                         # -> src_c/out/CONTRAP.EXE
python src_c/verify/verifyall.py                  # tabel status
```
Argumen ke-2 dan ke-3 = alamat & ukuran fungsi di biner asli (lihat
`work/ghidra_out/functions.txt`, tapi cek ulang dengan `truesize.py`).

## Status
**Status terkini dihasilkan oleh alat, bukan ditulis tangan** — jalankan
`pwsh src_c/build/buildall.ps1`, `pwsh src_c/build/link.ps1`, lalu
`python src_c/verify/verifyall.py`.

Ringkasan per 2026-07-30 (sesi ke-3):
- **LINK BERHASIL, tanpa error** — 59 `.OBJ` + `MC.LIB` → `out/CONTRAP.EXE`.
- **Segmen DATA 9.556/9.556 byte, 0 beda** vs biner asli.
- **Kode C: 55/57 fungsi COCOK, 10.771 byte (41,4%); TOTAL 20.327 / 36.756 (55,3%).**
  Dua near-miss, keduanya dengan
  peta slot dan daftar "sudah dicoba & gagal" di ujung berkasnya:
  - `place` (0x4e3e): panjang tepat 503, 2 byte beda (pilihan register SI/DI)
  - `nvar` (0x4094): 551 vs 566, bingkai 3ch vs 38h (2 temp kelebihan)
- Satu byte di `load` adalah artefak kompiler, dilaporkan terpisah.
- Stub sisa: 22 fungsi (BARU: `shftl`/`shftr` primitif geser layar assembly,
  `putmsk` @0x6524, `pickvar` @0x42ca).
- ✅ **`put()` yang bertabrakan SUDAH dipecah** (2026-07-30): `put` = 0x65e0
  (shuffle/askopts), `putmsk` = 0x6524 (xform/bounce). Keduanya rutin assembly
  berbeda — prolognya sama (`push bp; push es; mov bp,sp; mov ax,0b800h`) tapi
  alamatnya beda. Dulu satu nama, jadi LINK menyatukan dua alamat.

⚠ `.EXE` ini **belum bisa dimainkan**: `main` dan fungsi lain masih stub
kosong di `src/stubs.c`. Nilainya ada di dua hal — link membuktikan sumber kita
konsisten (tak ada simbol menggantung, tak ada definisi ganda), dan tata letak
DGROUP hasil link bisa dibanding langsung ke aslinya.

## ⚠ "COCOK BYTE-PER-BYTE" TIDAK memverifikasi IDENTITAS SIMBOL

Ini batas terpenting dari `objcode.py` dan harus dipahami sebelum mempercayai
angka mana pun: **slot relokasi diperlakukan sebagai WILDCARD**. Target `call`
dan alamat global tidak ikut dibandingkan. Akibatnya sebuah fungsi bisa
dilaporkan cocok byte-per-byte padahal:
  - memanggil fungsi yang SALAH (asal jumlah argumennya sama), atau
  - membaca/menulis variabel global yang SALAH (asal ukurannya sama).

Yang diverifikasi objcode.py: encoding instruksi, alokasi register, tata letak
bingkai, alur kendali, konstanta, jumlah & urutan argumen — semuanya eksak.
Yang TIDAK: identitas simbol di balik slot relokasi.

`symcheck.py` menutup lubang itu: ia membaca FIXUPP+EXTDEF dari .OBJ, membaca
BINER ASLI di posisi yang sama, menghitung alamat yang sebenarnya dituju, lalu
membandingkannya dengan alamat yang kita klaim untuk simbol itu.

Sekali dijalankan (2026-07-30) ia menemukan **57 ketidakcocokan nyata**, semua
lolos dari objcode.py:
  - **tabrakan nama**: `put` (0x6524/0x65e0), `pause` (0x2b11/0x31b0),
    `cur` (0x51c/0x522/0x2e6), `mark` (0x742/0x76a), `t1`/`t2`
    (0x1a2a/0x1ad2), plus `sel` dan `cur` = dua nama untuk 0x51c.
    LINK menyatukan nama yang sama, jadi salah satunya PASTI salah.
  - **nama callee salah**: `drawslot`/`fillans`/`pickloop` menulis `shuffle()`
    padahal memanggil 0x3909 (`mkpal`); `pickloop` menulis `waitkey()`
    padahal memanggil 0x5911 (`clrbot`).
  - **urutan store terbalik**: `setupscr` (prevtop/prevx) dan `timebar`
    (ta/tb) — sumbernya harus DIBALIK supaya emisinya cocok.

⚠ Jangan menamai dua alamat berbeda dengan nama yang sama, dan jangan
menamai satu alamat dengan dua nama berbeda. Keduanya lolos objcode.py.

## ⭐ SEGMEN DATA mulai di offset 4, bukan 0

Empat byte pertama DGROUP disumbang `C.OBJ` (crt0) yang selalu di-link paling
depan. Karena itu `gendata.py` punya `START = 4` dan `gdata.c` hanya memancarkan
offset 4..akhir. Kalau `gdata.c` ikut memancarkan offset 0..3, SELURUH DGROUP
bergeser 4 byte dan tiap alamat (`ticks @0x2e4`, dst) jadi salah — gejalanya:
`gdata.OBJ` sendiri cocok 100% tapi hasil link beda 5.821 byte mulai di
`DGROUP+0x2cc`. Bukti: peta link menunjukkan `DATA+0x0004` = `DGROUP+0x0000`.

Aturan turunannya: **ukur segmen DATA dari .EXE hasil link**, jangan dari
`.OBJ` tunggal. `.OBJ` bisa "cocok 100%" sementara hasil link-nya salah.

## ⭐ Alamat GANJIL wajib array byte

`int x[n]` dibulatkan ke atas ke batas kata. Simbol di alamat ganjil (kasus
nyata: `tune2 @0x1ddb`) harus dideklarasikan `char x[n]`, kalau tidak seluruh
sisa DGROUP bergeser satu byte. Sudah ditangani `gendata.py`.

## Menjalankan LINK: baris perintah DOS hanya 127 karakter

Daftar 44 objek jauh melewati batas itu. `link.ps1` menulis masukan ke berkas
lalu me-redirect: `y:\LINK < x:\link.in`. Format prompt LINK 1.10 = modul objek
/ run file / list file / pustaka; tanda `+` di ujung baris berarti lanjut.
`C.OBJ` (crt0) HARUS objek pertama.

⚠ Hapus `.OBJ` basi sebelum link. `rnd.OBJ` peninggalan probe yang berkasnya
sudah tak ada membuat LINK melaporkan "Symbol defined more than once" dan
menyembunyikan bahwa `rnd` sebenarnya belum direkonstruksi.

## Catatan penting: byte-identical ≠ source aslinya

Beberapa bentuk penulisan menghasilkan byte yang SAMA PERSIS. Yang kita bangun adalah
source yang *menghasilkan biner yang sama*, bukan tentu teks yang diketik penulis aslinya
tahun 1985. Untuk tujuan proyek ini (rebuild byte-identical) itu cukup — tapi jangan
menyebutnya "kode asli yang dipulihkan".

Contohnya variabel `unused` di beberapa fungsi: biner asli menyisihkan slot bingkai yang
tak pernah ditulisi. Kita mereproduksinya dengan variabel tak-terpakai. Penulis aslinya
mungkin menulis sesuatu yang lain yang kebetulan menghasilkan bingkai sama.

## ⭐ `&&` di syarat loop vs `if (...) return;` di badan

Dua bentuk ini punya arti yang SAMA tapi byte-nya beda jauh:

| bentuk | yang dipancarkan |
|---|---|
| `if (cond) return;` di dalam badan | epilog DIPANCARKAN ULANG di tempat (`add sp,N; pop bp; ret`) lalu dilompati `je` |
| `for (i=0; i<n && cond==0; i++)` | `jne` langsung ke epilog BERSAMA |

Cirinya di biner: kalau ada **satu epilog saja** dan **beberapa "jump false"**
(`jge`, `jne`, ...) semuanya menuju ke sana, itu tanda tangan `&&` — bukan
`return` di tengah badan. Kalau epilog muncul lebih dari sekali, memang ada
`return` di tengah. Kasus nyata: `pause` (0x31b0) turun 47 → 42 byte, langsung
cocok, hanya dengan memindahkan cek `keyhit()` dari badan ke syarat `for`.

## ⭐ DISPLACEMENT 8-BIT vs 16-BIT: field struct vs array global

Ini pembeda paling tajam yang ditemukan sejauh ini, dan gampang terlewat karena
alamatnya sama-sama kecil:

| biner | artinya |
|---|---|
| `8b 47 0a` — `mov ax,[bx+0ah]`, displacement **8-bit** | 0x0a = **offset field** di dalam struct |
| `8b 87 0a 00` — `mov ax,[bx+0000ah]`, displacement **16-bit** | 0x0a = **alamat global** yang direlokasi linker |

Kompiler memakai bentuk 8-bit kalau offsetnya konstanta kecil yang sudah pasti,
dan bentuk 16-bit kalau nilainya alamat simbol (belum diketahui saat kompilasi).
Jadi displacement 16-bit membuktikan ada **array/variabel global** di sana.

Kasus nyata `drawpair` (0x4a31): `8b 87 0a 00` semula dibaca sebagai
"`*(int *)(idx*0xc + 10)`" — offset field 10. Salah: itu **array global 12-byte
per entri di DGROUP 0x0a**, dan field yang dibaca adalah kata PERTAMA entri.
Ditulis `sprtab[k].spr` dengan `extern struct slot sprtab[]`, langsung cocok.

## ⭐ ARAH TERNARY ditentukan oleh cabang mana yang MEMUAT ULANG dari memori

`(v >= 0x80) ? v - 0x100 : v` dan `(v < 0x80) ? v : v - 0x100` sama artinya tapi
BEDA byte. Yang menentukan: kompiler menaruh cabang TRUE di fall-through dan
melompat ke cabang FALSE.

```
asli : cmp ax,80h / mov [bp+8],ax / jl +5 / sub ax,100h / jmp +3 / mov ax,[bp+8]
                                    └ cabang FALSE memuat ULANG dari slot
```
Cabang yang isinya "nilai apa adanya" dipancarkan sebagai **muat ulang dari
slot bingkai** (`mov ax,[bp+8]`), sedangkan cabang yang menghitung dipakai apa
adanya di AX. Jadi: **cari cabang yang berisi `mov ax,[bp+N]` — itu cabang
FALSE**, dan tulis ternary-nya supaya nilai-apa-adanya ada di posisi FALSE.
Menulis arah terbalik memberi 9 byte bukan 10 per pemulihan tanda; di
`drawpair` itu 4 tempat = 4 byte, cukup untuk menggagalkan seluruh fungsi.

Konstanta juga harus tepat: `>= 0x80` memberi `cmp ax,80h`, sedangkan
`> 0x7f` memberi `cmp ax,7fh`. Perhatikan mana yang ada di biner.

## ⭐ MS C 1.04 PUNYA `long` — dan itu terlihat di cara argumen didorong

Anggapan lama "1983 belum ada long" SALAH. Buktinya dua lapis:
- MC.LIB berisi modul pembantu aritmetika 32-bit: `CXM33` (kali), `CXD33` (bagi),
  `CXC33`, `CXVFD`/`CXVDF` (konversi). Lihat `python src_c/verify/libmatch.py`.
- Konstanta `long` didorong sebagai DUA kata yang masing-masing di-nol-kan
  SENDIRI, bukan satu register dipakai ulang:

```
0L  ->  xor bx,bx / push bx / xor bx,bx / push bx      (8 byte, 2 push)
0   ->  xor bx,bx / push bx                            (4 byte, 1 push)
0,0 ->  xor bx,bx / push bx / push bx                  (5 byte, 2 push)  <- CSE
```

Jadi kalau biner me-nol-kan register ULANG untuk push yang berurutan, itu satu
argumen `long`, bukan dua argumen `int`. Kasus nyata `loadarc` (0x531d):
`lseek(fh, 0L, 0)` (3 argumen) — bukan `lseek(fh, 0, 0, 0)` (4 argumen);
selisihnya tepat 4 byte dan itu byte terakhir yang menutup fungsi.

Konsekuensi lain: **jangan buru-buru menyimpulkan sebuah fungsi mustahil ditulis
di C 1983 hanya karena memakai 32-bit.** Yang benar-benar tak ada adalah
`unsigned long` (`rnd` di 0x5a5b mengambil kata tinggi dari DX setelah `mul` —
itu tetap assembly).

## ⭐ CSE: yang dipakai ulang itu PENUNJUK atau OFFSET?

`b[k*0xc + 1]` dan `(b + k*0xc)[1]` sama artinya, beda kode. Yang menentukan:
subekspresi mana yang jadi common subexpression.

```
(b + k*0xc)[1] ... (b + k*0xc)[0]      <- CSE PENUNJUK
   mov si,[b] / add si,ax / mov al,[si+1] / ... / mov al,[si]
   → penunjuk dihitung SEKALI, akses kedua pakai displacement

b[k*0xc + 1] ... b[k*0xc]              <- CSE OFFSET
   mov [bp],ax / inc ax / mov si,[b] / add si,ax / mov al,[si]
   ... mov si,[b] / add si,[bp] / mov al,[si]
   → offset yang dipakai ulang, penunjuk dihitung ULANG (+12 byte)
```

Ciri di biner: **`mov al,[si+1]`** (displacement) → CSE penunjuk.
**`inc ax` sebelum `add si,ax`** → CSE offset. Kasus nyata `pickpart` (0x131a):
selisihnya 12 byte, dan mengubah bentuknya saja menutup fungsi.

Terkait: kalau biner menyimpan sesuatu ke slot temp yang **tak pernah dibaca**
(`mov word ptr [bp],si` tanpa pembaca), itu temp CSE — BUKAN variabel lokal.
Menambah lokal untuk itu justru memperbesar bingkai dan menggagalkan fungsi.

## ⭐ `else` EKSPLISIT mencegah kompiler MELIPAT lompatan

Dua bentuk ini sama artinya — dan beda 2 byte:

```c
if (cond) goto X;              if (cond) goto X;
stmt;                          else { stmt; }
```
```
kita/dilipat : cmp .. / je X                    (2 byte)
asli/tak dilipat: cmp .. / jne stmt / jmp X     (4 byte)
```

Untuk suku TERAKHIR sebuah rantai `||` yang badannya cuma `goto`, kompiler
melipat lompatan bersyarat langsung ke label tujuan. Dengan `else` eksplisit ia
tidak melipat: ia memancarkan "lompat ke badan-else kalau salah" lalu
"jmp label" sebagai badan `if`-nya.

Ciri di biner: **`jne <alamat setelah jmp>` diikuti `jmp <target>`** — dua
lompatan berurutan yang bisa disederhanakan jadi satu. Kalau melihat pola itu,
sumbernya memakai `else`. Kasus nyata `getkey` (0x1814): byte TERAKHIR yang
menutup fungsi setelah 199 vs 197 bertahan lama.

## ⭐ `if` BERSARANG vs rantai `&&` rata: mempengaruhi pemuatan register

Rantai `&&` yang panjang dan rata membuat MS C 1.04 membandingkan **langsung
dari slot bingkai** (`cmp word ptr [bp+4],imm` = 5 byte per uji). Memecahnya
jadi `if` bersarang membuat kompiler memuat nilainya **sekali** ke AX lalu
memakai `cmp ax,imm` (3 byte per uji).

```c
if (a && b && c && d && e)   ->  cmp word ptr [bp+4], imm   x4   (20 byte)
if (a && b) { if (c && d && e) }  ->  mov ax,[bp+4] + cmp ax,imm x4 (15 byte)
```

Jadi kalau biner memakai `cmp ax,imm` untuk beberapa uji berturut, uji-uji itu
ada di dalam `if` bersarang — bukan satu rantai rata. Kasus nyata `getkey`:
selisihnya 5 byte.

## ⚠ BATAS KERAS PERTAMA: byte yang TIDAK ditentukan sumber C

`load` (0x53ff) cocok 261 dari 262 byte. Satu byte di +134 **tidak bisa
disamakan lewat bentuk sumber apa pun**, dan ini sudah dibuktikan, bukan
diduga.

**Apa byte itu.** MS C 1.04 salah memancarkan kode untuk `p == -1L` ketika `p`
bertipe long dan berasal dari panggilan fungsi:

```
3d ff ff    cmp ax,0ffffh      ; banding kata rendah
75 03       jne +3
05 49 94    add ax,9449h       ; <- SEHARUSNYA "cmp bx,-1"; ini SAMPAH
89 46 0c    mov [bp+0ch],ax
89 5e 0e    mov [bp+0eh],bx
75 12       jne ...            ; flag-nya sudah DIRUSAK oleh `add`
```
Karena `add` merusak flag, `jne` sesudahnya SELALU diambil, sehingga blok
`printf("...")` di 0x548e **tidak pernah tercapai**. Ghidra melaporkannya:
`WARNING: Removing unreachable block (ram,0x0001548e)`. Jadi pemeriksaan
gagal-seek di game asli memang mati sejak 1985 — jangan "diperbaiki".

**Buktinya bukan sumber C.** Sumber yang SAMA PERSIS, dikompilasi dengan nama
berkas berbeda, memberi imm yang berbeda:

| nama berkas | panjang | imm |
|---|---|---|
| `ab.c` | 2 | `0x3a49` |
| `abcd.c` | 4 | `0x3849` |
| `abcdef.c` | 6 | `0x3649` |
| `abcdefgh.c` | 8 | `0x3449` |

Yaitu byte tinggi = `0x3c - panjang_nama`. Isi berkas TIDAK berpengaruh: 60
fungsi dummy, 80 deklarasi extern, dan array lokal 1500 byte semuanya tidak
menggesernya. Aslinya `0x94` — di luar jangkauan nama 8.3 mana pun di
lingkungan kita, jadi selisihnya berasal dari lingkungan build 1985 (tata letak
memori DOS / direktori kerja), bukan dari sumbernya.

**Cara melaporkannya.** `manifest.txt` menerima kolom keempat `art=N` yang
menandai offset artefak. `verifyall.py` melaporkannya TERPISAH dan TIDAK
menghitungnya sebagai cocok:
```
load   0x53ff   262   COCOK kecuali 1 byte ARTEFAK KOMPILER (+134)
       1 byte di antaranya ARTEFAK KOMPILER yang TIDAK cocok
```
Pakai `art=` HANYA kalau sudah ada bukti seperti di atas — bukan untuk menutupi
byte yang belum dipahami.

## ⭐ STORE konstanta ter-hoist dipancarkan TERBALIK dari urutan sumber

Kalau beberapa penugasan berurutan memakai konstanta yang sama, MS C 1.04
mengangkat konstanta itu ke register SEKALI lalu memancarkan store-nya dalam
urutan **kebalikan** urutan sumber.

```c
cnt = 0; grp[1] = 0; grp[0] = 0; i = 0; ok = 1; last = 0xff; rp = recbase;
```
menghasilkan
```
xor ax,ax / mov [ok],1 / mov [last],0ffh / mov bx,[recbase]
mov [i],ax / mov [grp0],ax / mov [grp1],ax / mov [cnt],ax / mov [rp],bx
```
— perhatikan `i, grp0, grp1, cnt` adalah kebalikan dari `cnt, grp1, grp0, i`.

Konsekuensi praktis: **jangan urutkan penugasan awal menurut yang "masuk akal"**.
Baca urutan store dari biner, lalu BALIK untuk mendapat urutan sumbernya. Kasus
nyata `nvar` (0x4094): urutan yang tampak wajar (`ok, last, i, grp[0], grp[1],
cnt, rp`) membuat `xor ax,ax` jatuh SESUDAH dua store immediate dan urutan
grp tertukar; urutan terbalik memberi prolog yang cocok byte-per-byte.

Catatan: yang dibalik hanya store yang memakai register ter-hoist. Store
immediate (`mov [x],1`) tetap di urutan sumber dan dipancarkan lebih dulu.

## ⭐ `x[cnt++]`: bentuk TEMP vs `inc <memori>` ditentukan pemakaian nilai BARU

`cnt++` menghasilkan DUA bentuk kode yang berbeda, dan yang menentukan adalah
apakah nilai SESUDAH increment dipakai di dekatnya:

| konteks | kode |
|---|---|
| nilai baru dipakai (mis. langsung dibandingkan) | `mov ax,[cnt] / mov [bp],ax / inc ax / mov bx,[bp]` — nilai LAMA ke temp, baru di AX |
| nilai baru TIDAK dipakai | `mov ax,[cnt] / inc word ptr [cnt]` — increment langsung di memori |

Kasus nyata `nvar` — DUA fase, dua bentuk, dari sumber yang sama-sama `cnt++`:
```c
list[cnt++] = i;                    /* fase 1 */
if (cnt >= 0x32) ok = 0;            /* nilai baru dipakai -> bentuk TEMP */

out[cnt++] = list[r];               /* fase 2: nilai baru tak dipakai -> inc memori */
```
Jadi kalau biner memakai bentuk temp, JANGAN buru-buru menulis dua pernyataan
(`x[cnt] = v; cnt = cnt + 1;`) — itu memberi kode LAIN lagi. Yang benar tetap
`cnt++`; yang berbeda adalah apa yang datang sesudahnya.

## ⭐ Hanya perubahan TIPE yang mematahkan CSE nilai — teks tidak cukup

Kalau biner MEMUAT ULANG field yang sama dua kali sedangkan hasil kompilasi kita
memakai ulang nilai di AX (dengan spill `mov [bp],ax`), berarti sumber aslinya
membuat kompiler menganggap kedua pembacaan itu ekspresi BERBEDA. Yang
menentukan cuma satu hal: **tipe aksesnya**.

Diuji pada `place` (0x4e3e), `while (...)` lalu `if (sp->id == id ...)`:

| bentuk di `while` | hasil |
|---|---|
| `sp->id != 0` | di-CSE (nilai dipakai ulang) |
| `sp[0].id != 0` | di-CSE |
| `(*sp).id != 0` | di-CSE |
| `((struct slot *)sp)->id != 0` | di-CSE |
| **`*(char *)sp != 0`** | **TIDAK di-CSE** — memuat ulang, cocok dgn biner |

Jadi menulis ulang ekspresi yang sama dengan sintaks lain TIDAK ada efeknya;
hanya cast yang mengubah tipe akses (di sini `struct` → `char`) yang memisahkan
keduanya di tabel temp kompiler.

⚠ Efek sampingnya: cast `char *` menahan penunjuknya di SI, sehingga penunjuk
LAIN di pernyataan berikutnya jatuh ke DI. Di `place` itu menyisakan 2 byte beda
(`mov si,[bp+8]` vs `mov di,[bp+8]`). Jadi trik ini menutup satu masalah dan
membuka masalah lain — pakai sadar.

## ⭐ FUNGSI BER-SWITCH LEBIH PANJANG DARI YANG DILAPORKAN ALAT

`truesize.py` mencari epilog (`add sp,N; pop bp; ret`). Untuk fungsi yang
`switch`-nya jadi TABEL, masih ada kode SESUDAH epilog terakhir:

```
  <badan case terakhir: ... ret>
  jmp <atas loop>          <- back-edge, 3 byte
  <TABEL (nilai,label)>    <- 4 byte per entri, di SEGMEN KODE
  mov si,<4*(n-1)>         <- loop pencari
  cmp ax, cs:[si+tabel]
  jne +5
  jmp word ptr cs:[si+tabel+2]
  sub si,4
  jns ulang
  jmp <default>
```

Ukuran sebenarnya = sampai fungsi BERIKUTNYA, bukan sampai epilog. Kasus nyata:
`runmenu` 497 (truesize) / 430 (functions.txt) vs **547** sebenarnya;
`review` 650 / 362 vs **704**. Cara cepat: `alamat_fungsi_berikutnya - alamat`.

## ⭐ `default: break;` MEMANCARKAN back-edge loop sebagai jmp TERSENDIRI

`for (;;) { ... switch (k) { ... } }` — kalau semua badan `case` berakhir
`break`/`return`, ujung switch tak pernah tercapai. MS C 1.04 TETAP
memancarkan jmp back-edge di sana, TAPI hanya kalau ada `default:`:

| sumber | yang dipancarkan sebelum tabel |
|---|---|
| tanpa `default:` | (tidak ada) — back-edge dilipat ke jump default saja |
| **`default: break;`** | **`jmp <atas loop>` 3 byte, tepat sebelum tabel** |

Diuji `probes/probe8.c`: dari enam varian (tanpa default, `default: break;`,
`continue` di badan case, `while (1)`, `do {} while (1)`, pernyataan kosong
sesudah switch) HANYA `default: break;` yang menghasilkan pola itu. Ciri di
biner: **DUA** `jmp` ke alamat yang sama — satu sebelum tabel, satu di ujung
loop pencari. Kasus nyata: `runmenu` (3 byte terakhir) dan `review`.

## ⭐ Uji POSITIF berblok + `goto` menahan nilai di AX

Dua bentuk ini sama artinya dan menghasilkan LOMPATAN yang sama — tapi beda
dalam hal nilai yang tersimpan di register:

```c
if (g >= k) goto top;        if (g < k) {
<blok>                           <blok>
                             }
                             goto top;
```
```
keduanya : mov ax,[g] / cmp ax,[k] / jl +3 / jmp top
kiri     : mov si,[g]        <- DIMUAT ULANG dari memori
kanan    : mov si,ax         <- nilai DIPAKAI ULANG (AX jadi sibuk, jadi
                                muatan berikutnya jatuh ke BL: "mov bl,[si+..]"
                                lalu "mov ax,bx")
```

Lompatannya tetap bentuk dua langkah karena kompiler MERANTAI lompatan-salah
ke `goto` yang **langsung menyusul** blok. Kalau ada pernyataan lain di antara
blok dan `goto`, perantaian batal dan keluar lompat pendek (`jge +N`) — jadi
bentuk ini hanya berlaku saat `goto`-nya persis sesudah `}`.

Berlaku bersarang juga: `if (g >= 0) { if (g < 0x32) { ... } } goto top;`
memberi `test ax,ax / jns +3 / jmp top / cmp ax,0x32 / jl +3 / jmp top` —
KEDUA uji memakai AX yang sama.

Ciri di biner: **`mov si,ax` (atau register lain) sesudah `jmp` jauh** =
uji positif berblok. **`mov si,[alamat]`** = `if (...) goto`.
Dibuktikan `probes/probe9.c` (enam varian yang SEMUANYA gagal) dan
`probes/probe10.c` (yang berhasil). Kasus nyata `review`: 128 byte, dua tempat.

## ⭐ DUA bentuk tabel `switch`: RAPAT (indeks) vs JARANG (nilai,label)

MS C 1.04 memilih sendiri, dan bentuknya kelihatan jelas di biner:

| nilai case | kode dispatch | tabel |
|---|---|---|
| berurutan 0..n (`bounce`: 0,1,2,3) | `mov si,ax / cmp si,4 / jae default / shl si,1 / jmp cs:[si+tab]` | **1 kata per case**, urut nilai |
| jarang (`runmenu`: 0x1b,0x0d,0x250,…) | `mov si,4*(n-1) / cmp ax,cs:[si+tab] / jne +5 / jmp cs:[si+tab+2] / sub si,4 / jns` | **2 kata per case** (nilai,label) |

Konsekuensi praktis: kalau melihat `cmp si,<jumlah case>` + `shl si,1`, jangan
cari nilai case di tabel — tabelnya cuma alamat, dan nilainya = indeks. Kedua
bentuk sama-sama menaruh badan case LEBIH DULU dan dispatch-nya di BAWAH.
Untuk bentuk rapat, urutan tabel = urutan case di sumber (tidak dibalik);
untuk bentuk jarang, tabel muncul TERBALIK (lihat aturan 8f).

## ⭐ URUTAN PERNYATAAN: yang butuh REGISTER didahulukan, immediate menyusul

Untuk deretan penugasan ke global, MS C 1.04 memancarkan store dengan cara
berbeda tergantung asal nilainya, dan itu membocorkan urutan sumbernya:

```
nilai butuh register  -> nilai dihitung DI TEMPAT, store DITUNDA
                         (bisa sampai sesudah push argumen panggilan berikutnya)
nilai immediate       -> "c7 06 <alamat> <imm>" dipancarkan DI TEMPAT
```

Jadi urutan yang terlihat = pemuatan register (urut sumber), diselingi store
immediate (urut sumber), lalu semua store tertunda sekaligus di akhir.

⚠ Efek sampingnya nyata di UKURAN: store dari AX memakai bentuk akumulator
`a3 <alamat>` (**3 byte**), dari register lain bentuk umum `89 06 <alamat>`
(**4 byte**). Kalau satu penugasan immediate diselipkan lebih dulu, nilai yang
tadinya di AX pindah register dan fungsi jadi 1 byte lebih panjang. Kasus
nyata `bounce` (0x2504): menaruh `sndnull[2] = 8;` sebelum `sndnull[0] = 500;`
memberi 399 vs 398. Urutan yang benar dibaca dari **urutan pemuatan register**,
bukan dari urutan store.

## ⭐ MENULIS ULANG ekspresi (bukan memakai penampungnya) MEMESAN temp

Kebalikan dari aturan CSE yang lain, dan menambah byte:

```c
a = sel & 0x7fff;                a = sel & 0x7fff;
if (a != vsel[slot]) {           if (a != vsel[slot]) {
    vsel[slot] = a;                  vsel[slot] = sel & 0x7fff;   /* DITULIS ULANG */
```
```
kiri  : ... cmp ax,[si] / mov [bp+74],ax / mov [bp+0],si          (1 spill)
kanan : ... cmp ax,[si] / mov [bp+74],ax / mov [bp+0],ax
                                         / mov [bp+2],si          (2 spill, +3 byte)
```

Ekspresi yang SAMA muncul dua kali membuat kompiler memperlakukannya sebagai
common subexpression dan **memesan slot temp untuk NILAI-nya**, bukan cuma
untuk penunjuknya — meski nilai itu tetap dipakai dari register dan spill-nya
tak pernah dibaca. Memakai variabel penampung (`= a`) tidak memesan apa pun.

Ciri di biner: **dua `mov [bp+N],..` berurutan yang tak pernah dibaca**, satu
berisi nilai dan satu berisi penunjuk. Kasus nyata `runfill` (0x2d11): 380 vs
383 byte. Bandingkan dengan aturan sebaliknya di §"Hanya perubahan TIPE yang
mematahkan CSE nilai" — di sana yang dikejar adalah MEMISAHKAN dua pembacaan.

## ⭐ NILAI BOOLEAN yang DISIMPAN terlihat jelas di biner

`c = (a != b);` — hasil perbandingan ditugaskan ke `int` — dipancarkan sebagai:

```
cmp bx,ax / jne L1 / xor cx,cx / jmp L2 / L1: xor cx,cx / inc cx / L2:
```

Dua cabang yang SAMA-SAMA me-nol-kan register, satu di antaranya lalu `inc`.
Kalau melihat pola itu, sumbernya **menyimpan hasil perbandingan ke variabel**,
bukan memakai perbandingannya langsung di dalam `if`. Rantai `||` atas
variabel-variabel itu (`ok = (i == 0 || c1 || c2);`) memancarkan pola yang sama
sekali lagi untuk `ok`. Kasus nyata `mkpal` (0x3909), tiga kali.

## ⭐ STORE TERTUNDA yang DITIMPA akan GUGUR — pakai variabel yang SAMA

Dua pertukaran berurutan yang memakai variabel temp BERBEDA memancarkan dua
store; memakai variabel yang SAMA hanya memancarkan satu:

```c
t = a[r]; a[r] = a[i]; a[i] = t;        t = a[r]; a[r] = a[i]; a[i] = t;
u = b[r]; b[r] = b[i]; b[i] = u;        t = b[r]; b[r] = b[i]; b[i] = t;   <- SAMA
   -> mov [bp+12],cx / mov [bp+10],bx      -> mov [bp+10],cx saja
```

Sebabnya: store `t` yang pertama masih TERTUNDA (nilainya dipakai dari
register) dan keburu ditimpa penugasan kedua, jadi tidak pernah dipancarkan.
Ciri di biner: jumlah store ke slot lokal LEBIH SEDIKIT dari jumlah penugasan
di sumber. Kasus nyata `mkpal`: 3 store vs 2.

## ⭐ TURUNKAN pencacah LEBIH DULU kalau nilai barunya jadi indeks

```c
idtab[j] = idtab[cnt-1];        cnt = cnt - 1;
spr[j]   = spr[cnt-1];          idtab[j] = idtab[cnt];
cnt = cnt - 1;                  spr[j]   = spr[cnt];
   -> dec word ptr [cnt]           -> mov ax,[cnt] / dec ax / mov si,ax
      + indeks [si-1]                 ... / mov [cnt],ax   (store DITUNDA)
```

Kalau biner memuat `cnt` ke register, menguranginya, memakainya sebagai indeks
lewat `mov si,ax`, lalu menyimpannya kembali di AKHIR blok — itu tanda
`cnt = cnt - 1;` ditulis **sebelum** baris yang memakainya, bukan sesudah.

## ⚠ JANGAN beri nama KEDUA untuk alamat DGROUP yang sudah bernama

`gendata.py` memanen simbol dari komentar `@0xNNN` di semua `src/*.c`. Kalau
dua berkas memberi nama berbeda untuk alamat yang SAMA, simbol kedua dapat
ukuran NOL dan `gdata.c` memancarkan `int x[0] = { };` → MC1 menolak dengan
`Error 34: invalid initializer expression`, lalu MC2 gagal dengan pesan yang
menyesatkan: **`Can't open quad file`** (itu cuma akibat MC1 tidak menghasilkan
`.Q`, bukan masalah berkas sementara).

Sebelum menamai global baru, `grep` alamatnya dulu di `src/*.c`. Kasus nyata:
`0x3b6` sudah bernama `postab[]` di `hintmark.c`; menamainya `arrA` di
`loadcon.c` mematahkan seluruh build.

## ⭐ FUNGSI ASSEMBLY: MASM 1.27 sudah ada dan TERBUKTI byte-identical

`tools/masm/bin/MASM.EXE` — Microsoft MACRO Assembler 1.27 (1984), diekstrak
dari image floppy arsip `ms-masm-v127-840529` (FAT12, extractor ad-hoc). Dipilih
yang SEZAMAN supaya pilihan encoding-nya sedekat mungkin dengan 1985.

    pwsh src_c/build/masm.ps1 -Name vbio     # src_c/asm/vbio.asm -> out/vbio.OBJ

Modul pertama (`vbio`, 5 rutin, 54 byte) COCOK BYTE-PER-BYTE pada rakitan
pertama yang berhasil, tanpa error dan tanpa warning.

**Kerangka yang wajib dipakai** — segmen/grup HARUS sama dengan keluaran MC2,
kalau tidak modulnya tidak menyatu saat LINK (dibaca dari LNAMES/SEGDEF .OBJ
hasil MS C 1.04: `'', PROG, DATA, PGROUP, DGROUP`):

```asm
        NAME    modul
PGROUP  GROUP   PROG
DGROUP  GROUP   DATA
DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS
PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP
        PUBLIC  nama1, nama2
        ...
PROG    ENDS
        END
```

Nama publik TANPA garis bawah — MS C 1.04 (Lattice) tidak memberi prefiks.
Alamat segmen DGROUP ditulis `MOV AX,DGROUP` (jadi slot relokasi), bukan
konstanta `907h`.

## ⚠ MASM 1.27 butuh CRLF — gejalanya MENYESATKAN

Berkas `.asm` ber-akhir-baris LF dibaca sebagai SATU baris raksasa, dan MASM
melaporkan **"85:End of file, no END directive"** plus belasan "Syntax error"
— seolah-olah sintaksnya yang salah. `masm.ps1` sudah menormalkan ke CRLF saat
menyalin ke folder DOS; kalau merakit manual, jangan lupa.

## ⚠ `#define` bersambung backslash TIDAK didukung

MS C 1.04 menolak makro multi-baris: `Error 1: invalid pre-processor command`,
lalu MC2 gagal dengan `Can't open quad file`. Tulis makronya satu baris, atau
salin isinya manual.

## ⭐ METODE UTAMA: kejar DIVERGENSI PERTAMA, jangan menebak bentuk fungsi

Ini cara kerja yang paling ampuh, ditemukan setelah tiga putaran nyaris tanpa hasil.

**Salah** (boros): menebak satu bentuk penulisan untuk seluruh fungsi, kompilasi, lihat
"panjang beda", tebak lagi. Tiap siklus cuma menguji satu hipotesis besar dan sering
bergerak ke arah yang salah.

**Benar** (cepat): cari **byte pertama yang berbeda**, lihat instruksi di titik itu saja,
perbaiki tepat itu, kompilasi lagi. Divergensi berikutnya akan bergeser maju. Ulangi.
Tiap siklus menutup satu keputusan penulisan yang KONKRET.

```python
d = [k for k in range(n) if code[k] != orig[k] and k not in slots]
print('beda pertama +%d' % d[0])
print('kita:', code[d[0]-8 : d[0]+24])
print('asli:', orig[d[0]-8 : d[0]+24])
```

Contoh nyata: `drawpal` mandek di 192/204 setelah tiga tebakan buta (bahkan makin jauh:
186, 181). Dengan mengejar divergensi pertama, tiga siklus langsung menutupnya —
tiap siklus memberi satu fakta: (1) koordinat x ditampung lokal lalu dipakai `x+0x1f`,
(2) `nmech` tidak ditampung, (3) `lo+i` DIHITUNG ULANG di dalam cabang, slotnya cuma
sementara-kompiler. `timedrw` menyusul dua siklus: return awal, lalu urutan penunjuk.

## ⭐ RUMUS UKURAN BINGKAI (diturunkan lewat probe terkendali)

```
sub sp = 2 × (jumlah lokal) + 2 × (temp maksimum yang dibutuhkan ekspresi)
```

Diukur dengan `probes/probe5.c` (tiap faktor divariasikan satu per satu):

| bentuk | bingkai | catatan |
|---|---|---|
| tanpa lokal, hanya panggilan | **tak ada** | `ff(1,2,3)` tidak memesan bingkai sama sekali |
| tanpa lokal, `g = h + k` | 2 | satu temp |
| tanpa lokal, `(h+k)*(h-k)` | 4 | **dua** temp |
| tanpa lokal, `199-(h+(k*g)/3)` | 2 | satu temp — pola moveball |
| 1 lokal terpakai | 2 | |
| 1 lokal TIDAK terpakai | 2 | lokal tak terpakai TETAP dialokasikan |
| 2 lokal + `g = x + y` | 6 | 4 lokal + 2 temp |
| `x = ff(); g = x;` | 4 | 1 lokal + 1 temp |
| `g = ff() + 1;` | 2 | tanpa lokal |

**Batas rumus (ditemukan belakangan):** lokal `int` yang TIDAK dipakai kadang
dialokasikan (probe5/a4) dan kadang DIBUANG kompiler (askopts, loadarc) —
tampaknya tergantung apakah fungsi itu juga butuh temp. Kalau butuh satu slot
tambahan dan `int unused;` tidak menolong, pakai **array kecil** (`char pad[2];`)
— array selalu dialokasikan. Itu yang menutup `askopts`.

**Cara pakai saat bingkai meleset:** selisihnya selalu kelipatan 2. Kalau kita
KELEBIHAN satu slot, biasanya ada satu pernyataan yang menuntut dua temp — cari
ekspresi yang menghitung dua nilai hidup sekaligus, dan ubah jadi bentuk yang
memakai kembali hasil sebelumnya.

**Penugasan bersarang** adalah alat utamanya. `balltop = 199 - (ballx = expr);`
menahan nilai di register (store ke `ballx` ditunda) sehingga hanya butuh SATU
temp, sementara menulisnya sebagai dua pernyataan terpisah memaksa baca-ulang
dari memori, dan menghitung ulang ekspresinya memaksa temp kedua. Inilah yang
akhirnya menutup `moveball` setelah sepuluh percobaan gagal.

## ⚠ JANGAN percaya pseudo-C Ghidra untuk BENTUK kode

Ghidra bagus untuk memahami LOGIKA, tapi menyesatkan untuk bentuk penulisan.
Yang sudah terbukti salah tampil (masing-masing memakan beberapa putaran):

| Ghidra menampilkan | kenyataan di biner |
|---|---|
| `local_a = iVar3 + 1;` | tidak ada store sama sekali; nilai cuma diuji di AX |
| satu `local_a` | DUA variabel berbeda (pencacah loop dalam + penampung) |
| salinan lokal dari parameter | parameter dimajukan LANGSUNG (`add [bp+16h],0ch`) |
| `iVar1 = ...; balltop = 199 - iVar1;` | penugasan bersarang, nilai tetap di register |
| `a != 0 \|\| b != 0` | `or ax,[b]` — OR BITWISE, satu uji |

**Cara benar:** baca disassembly-nya. Petakan dulu slot yang dipakai
(`grep "bp + "` pada keluaran `show.py --asm`), tentukan variabel mana di slot
mana, BARU tulis C-nya. Pseudo-C dipakai hanya untuk menebak maksud fungsinya.

## ⭐ BENTUK AKSES TABEL menentukan kode — empat varian, empat hasil berbeda

Tabel yang sama bisa ditulis tiga cara, dan MS C 1.04 menghasilkan kode BERBEDA
untuk masing-masing. Cocokkan dgn instruksi di biner:

| tulis begini | biner yang dihasilkan | dipakai kalau biner… |
|---|---|---|
| `p[i]` dgn `int *p` (parameter) | skala x2, indeks dipakai ULANG dari akses sebelumnya | memakai ulang nilai i*2 yang sudah dihitung |
| `*(int *)(p + i*0xc)` | `imul 0ch` lalu **`add ax,OFFSET`** | menambahkan basis lewat register |
| `tab[i].field` dgn array STRUCT | `imul 0ch` lalu **`mov ax,[si+OFS]`** | memakai bentuk **displacement** |

Contoh nyata:
- `autofill`/`loadarc`: bentuk `*(int *)(t + i*2)` memaksa hitung ulang indeks;
  `t[i]` membuat kompiler memakai ulang temp — itu yang menutup `autofill`.
- `drawslot`: `sprtab[ans[i]*6]` (int[]) menambah `d1 e0`; penjumlahan penunjuk
  memberi `add ax,OFFSET`; hanya **array struct 12-byte** (`sprtab[ans[i]].w`)
  menghasilkan `mov ax,[si+1aeh]` — satu byte terakhir yang menutupnya.

### Varian ke-4: PENUNJUK struct (bukan array struct)

Kalau biner memuat basis **sekali** ke SI lalu memakai displacement dari SI untuk
byte MAUPUN kata dari record yang sama — `8a 44 07` (`mov al,[si+7]`) dan
`ff 74 02` (`push [si+2]`) — sumbernya adalah **penunjuk struct**, dan biasanya
penunjuk itu MAJU sendiri (`p++` → `add word ptr [bp+0ch], 0ch`).

| tulis begini | hasil |
|---|---|
| `*(int *)(p + 10)` dgn `char *p` | `mov ax,si; add ax,0ah; push [..]` — boros, +3 temp |
| `p->spr` dgn `struct item *p` | `ff 74 0a` (`push [si+0ah]`) — displacement langsung |

Kasus nyata `show` (0x381a): bentuk `*(int *)(p + n)` memberi **176 byte,
bingkai 0eh**; penunjuk struct memberi **108 byte, bingkai 8 — cocok persis**.
Selisihnya bukan satu-dua byte, jadi kalau bingkai kita kelebihan beberapa temp
dan record diakses campur byte+kata, CURIGAI struct lebih dulu.

Aturan praktis: lihat apakah biner memakai **displacement** (`[si+OFS]`) atau
**penjumlahan basis** (`add ax,OFFSET`). Displacement → subscript array/struct
atau penunjuk struct. Penjumlahan → aritmetika penunjuk.

## Hasil NEGATIF yang berguna (probes/probe7.c)

Untuk pola "uji lalu tulis elemen tabel yang sama" (`if (t[i] != v) t[i] = v;`),
lima bentuk diukur. Hasilnya: **penunjuk lokal eksplisit TIDAK menghemat bingkai** —
ia hanya memindahkan satu temp menjadi satu lokal, totalnya sama.

| bentuk | bingkai |
|---|---|
| `if (t[i] != v) t[i] = v;` | 4 (0 lokal + 2 temp) |
| `p = &t[i]; if (*p != v) *p = v;` | 4 (1 lokal + 1 temp) |
| `h = (t[i] = v);` (bersarang) | 4 |
| `old = t[i]; if (old != v) …` | 6 |
| indeks ditampung variabel | 6 |

Jadi kalau sebuah fungsi kelebihan satu slot, JANGAN cari jawabannya di pola
akses tabel ini — sumbernya di tempat lain.

## ⭐ URUTAN ALOKASI REGISTER PENUNJUK: BX dulu, SI/DI kalau perlu bersamaan

Ditemukan lewat probe 16–18 (2026-07-31), sesudah belasan iterasi tebak-tebakan
di `f498c` dan `place` gagal.

**Aturannya:** MS C 1.04 memakai **BX** untuk penunjuk sementara. **SI** (lalu
DI) baru muncul kalau **lebih dari satu penunjuk harus hidup bersamaan**.

```
nvar(tab[i*3+2], buf)                  -> BX saja
p = tab + i*3; nvar(p[2],buf); p[0]    -> BX, lalu SI sesudah panggilan
nvar(tab[i*3+2] + tab[i*3], buf)       -> BX dan SI bersamaan
```

**Yang TERBANTAH:** bentuk struct vs larik-int TIDAK menentukan pilihan
register — ketiga varian probe 16 sama-sama memakai BX.

**Konsekuensi untuk near-miss `f498c` (3 byte) dan `place` (2 byte):** aslinya
memakai SI di titik yang punya kita memakai BX, artinya di titik itu compiler
menganggap ada penunjuk LAIN yang masih hidup. Karena byte sebelum dan
sesudahnya sudah cocok persis, penyebabnya bukan bentuk ekspresi setempat —
jangan mengejarnya lewat menulis ulang ekspresi (sudah ~15 percobaan, nol).

⚠ Probe dikompilasi dari `src_c/src/` (itu yang dibaca `compile.ps1`), lalu
DIPINDAH ke `src_c/probes/` supaya tidak ikut terbangun tiap kali.

## Teknik: pakai PROBE, jangan iterasi fungsi penuh

Saat sebuah fungsi tidak cocok, JANGAN menebak lalu mengompilasi ulang fungsi utuh.
Tulis probe kecil berisi 2–3 varian penulisan dari potongan yang meragukan saja
(lihat `src/probe3.c`), kompilasi sekali, lalu bandingkan BENTUK kodenya. Satu putaran
probe menjawab pertanyaan yang bisa memakan sepuluh iterasi tebak-tebakan.

Contoh nyata: `goalmenu` meleset 18 byte. Probe dgn 3 varian langsung menunjukkan
varian mana yang benar, dan percobaan berikutnya langsung cocok.

## Aturan main (mahal dipelajari, jangan diulang)

1. **Gaya K&R, bukan C modern.** MS C 1.04 pra-ANSI: parameter dideklarasikan setelah
   baris nama fungsi, tanpa prototype, tanpa `void`.
2. **`unsigned long` TIDAK ADA.** Mencobanya → `Error 77: identifier expected`.
   Tipe yang tersedia: `char, int, unsigned, long, float, double`.
3. **Kompilernya tidak mengoptimasi.** Perkalian `long` jadi panggilan rutin + loop geser,
   bukan satu instruksi. Jangan menulis C "pintar" berharap keluar kode ringkas — tulis
   yang lugas, itu yang cocok.
4. **Nama berkas WAJIB 8.3.** DOS tidak mengenal nama panjang; kalau dilanggar, alat akan
   "berhasil" tanpa mengerjakan apa pun (gagal diam-diam).
5. **Tidak semua fungsi berasal dari C.** Lihat §Fungsi assembly di bawah — memaksakan
   rekonstruksi C untuk fungsi assembly hanya membuang waktu.
6. **Satu `.OBJ` memuat beberapa segmen** (kode DAN data). Menggabungkannya berdasar offset
   akan membuat data menimpa awal kode. `objcode.py` memisahkan per segmen.
7. **Slot relokasi dibaca dari record FIXUPP**, bukan ditebak dari "byte kita nol".
   Tebakan itu pernah menyamarkan 2 byte berbeda sungguhan jadi laporan "cocok".
8b. **Urutan deklarasi lokal = urutan slot.** Penampung hasil panggilan biasanya
   dideklarasikan LEBIH DULU (jatuh di `bp+2`), pencacah loop sesudahnya (`bp+4`).
   Kalau instruksinya benar tapi nomor slotnya tertukar, cukup tukar urutan deklarasi.
8c. **Operan pembanding tidak boleh dibalik.** Tulis `if (r > best)` — nilai yang sudah
   ada di AX di sebelah KIRI. Menulis `if (best < r)` memaksa kompiler memuat `best`
   ke register dulu (`mov bx,[best]; cmp bx,ax`) = 2 byte lebih panjang.
8d. **Alamat DGROUP bukan konstanta biasa.** Nilai seperti `0x1dd0` yang ternyata alamat
   harus ditulis sebagai simbol (`sndptr = tune1;`), karena alamat relokatabel dimuat
   lewat `mov ax,OFFSET x` lalu disimpan — bukan store-immediate. Penugasan penunjuk
   juga ditulis SEBELUM penugasan konstanta di sebelahnya, supaya pemuatan alamat
   muncul lebih dulu seperti di biner asli.
8. **Hasil panggilan fungsi ditampung variabel tersendiri**, jangan disarangkan.
   Tulis `h = f(...); y = y + h;` BUKAN `y = y + f(...)`. Bentuk bersarang membuat
   kompiler tidak mengalokasikan slot sementara dan memilih register lain
   (`mov ax,0eh` alih-alih `mov cx,0eh`) → kode beda. Ini pola menyeluruh di
   biner ini, bukan kebetulan satu fungsi.
8e. **Nilai yang di-`switch` TIDAK ditampung variabel** — pengecualian dari aturan 8.
   `switch (getkey())` biarkan hasilnya di AX. Menampungnya menambah slot bingkai dan
   mengubah tiap pembandingan jadi akses memori (`83 7e 04 ..` bukan `3d ..`).
8f. **Kenali `switch` dari tata letaknya**: badan tiap case ditaruh LEBIH DULU, lalu
   `jmp` ke rantai pembanding di BAWAH. Rantai if/else-if menaruh uji di depan.
   **Urutan `case` di sumber = urutan badan case di biner**; rantai pembandingnya
   muncul TERBALIK. Kalau instruksinya benar tapi urutannya tertukar, balik urutan case.
   (Untuk case yang banyak, kompiler beralih ke tabel — lihat `probes/probe4.c`.)
8g. **Uji batas bawah ditulis `x >= 0`, bukan `x > -1`.** Aslinya `test bx,bx; js`
   (uji tanda); `> -1` menghasilkan `cmp bx,-1; jle` yang 2 byte lebih panjang.
8h. **Jangan memberi nama lokal untuk nilai yang cukup hidup di register.** Kalau
   `sub sp,N` lebih besar dari aslinya, kemungkinan besar ada lokal yang tidak
   seharusnya ada (contoh: `timebar` — semuanya cukup di AX/BX).
8i. **Basis bingkai TIDAK selalu 2.** Rumusnya `sub sp = basis + 2×jumlah_lokal`,
   tapi basisnya berbeda antar fungsi (delay: 2, xform: 4). Cara pakai: kompilasi
   sekali, lihat selisih `sub sp` kita vs asli, lalu tambah/kurangi jumlah lokal
   sebanyak selisih/2. Jangan mencoba menghitungnya dari teori.
9. **Urutan deklarasi lokal menentukan tata letak bingkai.** Ukuran bingkai =
   `2 + 2×jumlah_lokal`, dan variabel dialokasikan sesuai urutan deklarasi
   (deklarasi pertama di `bp+2`). Kalau ukuran `sub sp,N` tidak cocok, jumlah atau
   urutan lokal masih salah — itu petunjuk paling cepat.

## ⚠⚠ METRIK SERAKAH BISA MELAPORKAN TURUN PADAHAL MEMBAIK — pakai GLOBAL

`aligned()` di `aligncmp.py` memindai serakah dengan jendela geseran ±24 dan
lari minimal 6/12 byte. Kalau POLA divergensinya berubah, ia bisa gagal
menyambung dan **melaporkan penurunan padahal kodenya membaik.**

Terjadi nyata di `pickvar` (2026-07-31). Satu perubahan urutan pernyataan:

| metrik | sebelum | sesudah | arah |
|---|---|---|---|
| TERJAJAR (serakah) | 1.616 | 1.583 | turun ❌ |
| POSISI | 368 | **1.333** | naik |
| panjang | −4 | **−3** | naik |
| **GLOBAL (difflib)** | 1.631 | **1.654** | **naik ✅** |

Tiga dari empat menunjukkan perbaikan; yang serakah salah. `aligncmp.py`
sekarang mencetak **GLOBAL** juga — pakai angka itu untuk MEMUTUSKAN, dan
angka serakah hanya untuk DAFTAR GESERAN-nya (yang tetap berguna menunjuk
LETAK masalah).

⚠ Ini juga berarti keputusan lama yang diambil hanya dari angka serakah layak
ditinjau ulang — beberapa "sudah dicoba & gagal" mungkin sebenarnya berhasil.

## ⚠⚠ LUBANG METRIK PENJAJARAN: ia BUTA terhadap identitas simbol

`aligncmp.py` memperlakukan slot relokasi sebagai wildcard (harus begitu —
alamatnya belum final di `.OBJ`). Akibatnya **penyimpanan ke simbol yang SALAH
tidak terdeteksi sama sekali**: `mov [hintshown],ax` dan `mov [both],ax`
menghasilkan byte yang identik (`a3 00 00`).

Dibuktikan 2026-07-31: membalik urutan enam penugasan nol di `main` memberi
byte yang **persis sama** dan TERJAJAR yang **persis sama**, padahal simbol
tujuannya berbeda total. Yang membedakan hanya rekaman **FIXUPP**.

Cara memeriksanya:
```python
from symcheck import read_obj
ext, fx = read_obj("src_c/out/main_.OBJ")
[nm for off, mb, nm in sorted(fx) if lo < off < hi]   # urutan simbol sebenarnya
```

**Konsekuensinya serius:** `symcheck.py` MELEWATI fungsi yang belum cocok
byte-per-byte (offsetnya tak sejajar, hasilnya sampah). Jadi untuk `main`,
`pickvar`, `place`, `nvar`, `loadcon` identitas simbol **belum terverifikasi
sama sekali** — TERJAJAR setinggi apa pun tidak membuktikan simbolnya benar.
Periksa manual lewat FIXUPP seperti di atas untuk blok-blok kritis.

Dengan cara itu pula aturan "urutan pancaran = KEBALIKAN urutan sumber"
akhirnya diverifikasi langsung, bukan disimpulkan dari panjang byte:
sumber `hintshown, g7e8, cursel, failed, sub, both` memancarkan
`both, sub, failed, cursel, g7e8, hintshown` — dan itu cocok dengan biner asli.

## ⚠⚠ CARA MENGUKUR: jangan pakai "byte cocok per POSISI"

Menghitung byte yang sama **di posisi yang sama** hanya sahih kalau panjang
draf SUDAH persis sama dengan aslinya. Begitu ada satu sisipan atau kekurangan,
seluruh sisa berkas bergeser dan byte yang sebenarnya benar terhitung salah.

Buktinya telak (2026-07-31, `pickvar`): satu perubahan menurunkan angka posisi
392 → 386 **tapi** menaikkan angka penjajaran 684 → 704. Kalau angka posisi
dipercaya, perubahan yang BENAR akan dibuang. Di akhir sesi `pickvar`
menunjukkan POSISI 368 padahal **1.616 byte benar-benar sejajar**.

```
python src_c/verify/aligncmp.py <nama>                          # ringkasan
python src_c/verify/aligncmp.py <nama> --sbs <addr> <n> <geser>  # berdampingan
```

Keluarannya juga menyebut **di alamat mana** panjang mulai menyimpang dan
sebanyak apa. Itu yang menunjuk blok berikutnya yang harus digarap — jauh lebih
berguna daripada satu angka total. Alur kerjanya: lihat geseran terbesar →
`--sbs` di situ → perbaiki → ukur lagi.

## ⭐ ATURAN dari `pickvar` (0x42ca) — semuanya terukur, bukan diteorikan

10. **Akses record SELALU bentuk PENUNJUK** `(idx * 0xc + basis)[n]`.
    - offset `((char*)basis)[idx*0xc+n]` → basis dimuat **DUA KALI** (+15 byte)
    - struct `((struct rec*)basis)[idx].f` → basis dimuat dini ke DX lalu
      di-spill (+6 byte, dan bisa membengkakkan bingkai sampai gagal)

11. **KOREKSI aturan lama.** Pernah tercatat "sisi kanan perbandingan harus
    bentuk struct supaya CSE atas `recbase` putus" — **itu KELIRU**. Kedua sisi
    bentuk penunjuk; yang membedakan hanya URUTAN OPERAN perkalian:
    | sumber | keluaran |
    |---|---|
    | `0xc * list[i]` | `mov ax,0Ch` / `imul word ptr [bx]` |
    | `k * 0xc` | `mov ax,cx` / `mov dx,0Ch` / `imul dx` |

12. **`if (--x < 0)` ≠ `x--; if (x < 0)`.** Yang kedua memakai ulang flag dari
    `DEC` (`jge`, 2 byte lebih pendek). Aslinya memancarkan `test ax,ax` lalu
    `jns` — dan itu HANYA keluar dari bentuk pre-decrement di dalam syarat.

13. **TIGA bentuk `switch`, dipilih menurut kerapatan nilai case.**

    | bentuk | pancaran | contoh |
    |---|---|---|
    | **jarang** | tabel pasangan NILAI+LABEL, dipindai **MUNDUR** dari entri terakhir (`mov si,18h` / `cmp ax,cs:[si+tab]` / `sub si,4` / `jns`) | `pickvar` 0x4975 |
    | **padat** | `si = v - k` / `cmp si,n` / `jae default` / `shl si,1` / `jmp cs:[si+tab]`, tabel berisi LABEL saja | `main` 0x0488, 0x04FB |
    | **rantai** | tanpa tabel sama sekali: `cmp ax,2` / `jne` / `jmp badan`, berurutan | `main` 0x05F1 |

    ⭐ Aturan urutan case berlaku di **ketiga** bentuk, termasuk RANTAI —
    terbukti 2026-07-31 di `main`: badan `case -1` (`jmp` keluar) ada di
    0x0B7A, **sebelum** badan `case 0` di 0x0B7D. Menukar urutannya di sumber
    menaikkan penjajaran 47 byte dan menghapus dua titik geseran.
    **Cara mendeteksinya:** `--sbs` di titik geseran memperlihatkan sebuah
    `jmp` yang ada di biner asli tapi tidak di posisi yang sama pada kita —
    itu badan case yang tertukar.

    Yang **sama di ketiganya**: blok ujinya diletakkan **SESUDAH** badan case
    dan dicapai lewat `jmp` ke depan — itulah yang membedakan `switch` dari
    rantai `if` biasa. Dan pada ketiganya, **urutan `case` di sumber = urutan
    ALAMAT badan case-nya**, bukan urutan nilainya. Di `main` 0x04FB misalnya
    `case 1` ditulis TERAKHIR walau nilainya terkecil. Tanpa aturan ini urutan
    case pasti tertukar.

14. **`idx == q` ≠ `q == idx`.** Operan KIRI dimuat lebih dulu ke AX dan sering
    dipakai ulang di perbandingan berikutnya; membaliknya memaksa muat ulang.

15. **Jangan menganggap slot yang belum dikenali itu "pengganjal".** Di
    `pickvar` LIMA kali berturut tebakan pengganjal ternyata variabel nyata
    (36/3A/3E/42, 2C..33, 18/1C/50, 20, 4A). Anggap calon variabel dulu.

16. **Kalau dua blok terlihat kembar, ukur DUA-DUANYA.** 0x4455 dan 0x46A0
    tampak identik tapi yang kedua menyimpan empat sudut ke slot sebelum
    memanggil `blit`. Sebaliknya 0x4713 memang duplikat byte-per-byte dari
    0x46CD — satu blok ditulis, 68 byte langsung terisi.

17. **Fungsi bisa TIDAK punya epilog di ujung.** Kalau semua jalur keluar lewat
    `return` di dalam `switch`, tidak ada `add sp,N / pop bp / ret` penutup.
    Jalur galat pun bisa melompat ke tengah fungsi, bukan ke `return`.

## ⚠ `symcheck`: nama BERKAS ≠ nama SIMBOL

Satu modul assembly bisa memuat beberapa fungsi, dan yang bernama sama dengan
berkasnya belum tentu ada di offset 0. Modul `text` mulai di **0x644a** (itu
pembungkus INT 10h, sekarang bernama `bios10`) sedangkan simbol `text` ada di
**0x6453**. Sebelum dibetulkan, `symcheck` melaporkan **18 BEDA PALSU**.
Alamat simbol sekarang diambil dari rekaman **PUBDEF** `.OBJ`, dan pemadanan
nama tidak peduli besar-kecil huruf (MASM memancarkan HURUF BESAR, `.c` huruf
kecil; LINK memadankan tanpa peduli kasus).

## ✅ DGROUP 0..3 milik crt0 — BUKAN bug gendata (koreksi 2026-07-31)

Saya sempat mencatat ini sebagai bug. **Itu keliru.** `START = 4` di
`gendata.py` memang disengaja: dua kata pertama DGROUP disumbang `C.OBJ`
(crt0) yang selalu di-link paling depan. Kalau `gdata.c` ikut memancarkannya,
seluruh DGROUP bergeser 4 byte.

Yang dibutuhkan bukan perubahan `gendata.py`, melainkan memakai simbol yang
**sudah diekspor crt0**:

| simbol | offset DGROUP |
|---|---|
| `_TOP` | 0x0000 |
| `_BASE` | 0x0002 |

`main` MENYIMPAN `_TOP` di awal dan MENGEMBALIKANNYA saat keluar (bingkai
tumpukannya sendiri 28.566 byte). Deklarasikan `extern int _TOP;` **tanpa**
komentar `@0x...` supaya `gendata.py` mengabaikannya dan LINK mengambilnya
dari `C.OBJ`. Menutup 12 byte di `main`.

**Pelajaran:** sebelum menyebut sesuatu bug, baca komentar kodenya dan cek
PUBDEF modul lain — alasannya sering sudah tertulis.

## (dulu dianggap bug) `gendata.py` membuang alamat DGROUP 0..3

Penyaringnya `START <= a` dengan `START = 4`, padahal `a` itu alamat **DGROUP**
sedangkan `START` offset **DATA**. Simbol di DGROUP:0000..0003 karena itu tidak
pernah terbit dan LINK melaporkan unresolved. Ini memblokir satu instruksi di
`main` (0x00B9 `mov bx,[0]`, biaya 7 byte). **Belum diperbaiki** — menyentuh
penataan DGROUP yang sekarang 100% cocok (9.556/9.556), jadi butuh keputusan.

## ⭐ TIPE deklarasi lokal menentukan BENTUK PENGALAMATAN, bukan cuma ukuran

Dua deklarasi berukuran sama memberi kode yang jauh berbeda:

| sumber | pancaran |
|---|---|
| `int arr[20];` lalu `arr[i] = -1` | `mov si,ax` / `mov [bp+si+0A8h],bx` |
| `char arr[0x28];` lalu `((int*)arr)[i] = -1` | `lea bx,[bp+0A4h]` / `add bx,ax` / `mov [bx],ax` |

Keduanya 40 byte, tapi yang pertama memakai **indeks langsung** dengan basis
larik sebagai displacement, yang kedua menghitung penunjuk lebih dulu.
Terbukti di `main` (2026-07-31): versi `char[]`+cast tidak menaikkan angka
penjajaran **sama sekali**; setelah diubah ke `int[20]` langsung naik.

**Cara mengenali dari disassembly:** lihat lebar aksesnya.
`mov word ptr [bp+si+off]` → larik `int`. `mov byte ptr [bp+si+off]` → larik
`char`. Jangan menebak dari ukuran penyangga saja.

## ⚠⚠ SATU NAMA untuk DUA ALAMAT — bug `sprtab` (ditemukan 2026-07-31)

Aturan "SATU alamat SATU nama" ternyata punya ARAH KEBALIKAN yang sama
berbahayanya: **satu NAMA tidak boleh dipakai untuk dua alamat.**

`sprtab` dideklarasikan di DUA berkas dengan alamat berbeda:

```
drawpair.c:  extern struct slot  sprtab[];   /* @0x0a  */
drawslot.c:  extern struct sprent sprtab[];  /* @0x1ae */   <-- SALAH
```

LINK memadankan **nama**, bukan alamat. `gdata.c` cuma mendefinisikan satu
`sprtab` (gendata memakai `setdefault`, jadi berkas pertama secara abjad
menang → 0x0a), sehingga rujukan drawslot ikut tertaut ke 0x0a dan **meleset
420 byte**. Terbukti dari EXE hasil link: slotnya berisi `0x0016` padahal
seharusnya `0x01ba` (= 0x01ae biner asli + geseran DGROUP build kita, +12).

**Kenapa lolos begitu lama — TIGA lapis verifikasi gagal sekaligus:**

1. `objcode.py` memperlakukan slot relokasi sebagai wildcard → tetap `COCOK`.
2. `verifyall.py` memakai objcode → tetap `COCOK`.
3. `symcheck.py` — yang justru dibuat untuk menutup lubang ini — menganggapnya
   **"akses ber-INDEKS"**: selisih 420 masih di bawah ambang lama 0x400.

Ambangnya sekarang `INDEX_MAX = 0x100`, dan apa pun di antaranya dilaporkan
sebagai baris `CURIGA`. Aman: selisih indeks SAH terbesar yang benar-benar ada
di seluruh proyek cuma **+94** (`mainmenu`/`mtabmn`), jadi 0x100 memisahkan
keduanya bersih tanpa satu pun positif palsu.

**Pemeriksaan yang layak diulang:** tiap kali menambah `extern ... /* @0xNNN */`,
pastikan namanya belum dipakai untuk alamat LAIN, bukan cuma bahwa alamatnya
belum punya nama. Yang kedua saja tidak cukup.

## ⭐ PENUGASAN DI DALAM SYARAT menahan nilai di register

`if ((v = <ekspresi>) >= 0) f(v);` memancarkan `push ax` — nilainya masih di
register sesudah uji tanda. Bentuk DUA PERNYATAAN memaksa muat ulang:

| sumber | pancaran argumen |
|---|---|
| `if ((v = *p++) >= 0) f(v);` | `push ax` (1 byte) |
| `v = *p++; if (v < 0) break; f(v);` | `push word ptr [bp+2Ah]` (3 byte) |

Terbukti di `animvm` `case 0x02` (2026-07-31): bentuk kedua membuat bloknya
meleset 2 byte; bentuk pertama membuatnya COCOK byte-per-byte.

## ⭐ TERNARY vs `if/else` — bedanya SATU SIMPANAN, dan pilihannya per-TEMPAT

Keduanya semantik sama, kodenya tidak:

| sumber | pancaran |
|---|---|
| `v = c ? a : b;` | hitung ke AX, **satu** simpanan, AX dipakai ulang sesudahnya |
| `if (c) v = a; else v = b;` | simpan di **kedua** cabang, lalu MUAT ULANG `v` |

Selisihnya 4 byte di `animvm` `case 0x03`. ⚠ Dan pilihannya **per-tempat, bukan
per-berkas**: di fungsi yang sama, pemilihan indeks (`u14 = c1+1 : c1`) memakai
`if/else`, sedangkan pemulihan tanda ambang 0xC8 tepat di bawahnya memakai
TERNARY. Jangan menyeragamkan — ukur tiap tempat.

## ⭐ SATU ekspresi `||` menahan penunjuk di register, dua `if` tidak

| sumber | uji kedua |
|---|---|
| `if (*p == 0xff \|\| p == 0) break;` | `test si,si` (2 byte) — SI dipakai ulang |
| `if (*p == 0xff) break; if (p == 0) break;` | `cmp [3AEh],0` (5 byte) — muat ulang |

Alur kendalinya IDENTIK; yang berbeda cuma apakah kompiler masih menganggap
penunjuknya hidup di register. Sepola dengan aturan penugasan-di-dalam-syarat.

## ⭐⭐ MUATAN REGISTER mengikuti urutan SUMBER; SIMPANANNYA ditata ulang

Aturan paling produktif yang ditemukan sejauh ini untuk membaca urutan
pernyataan dari biner. Untuk dua pernyataan berurutan yang satu menyimpan
KONSTANTA-immediate dan satunya menyimpan nilai yang perlu REGISTER:

```
mov ax, <nilai>        ← muatan register: mengikuti urutan SUMBER
mov [immediate], K     ← simpanan pernyataan LAIN, disisipkan kompiler
mov [register], ax     ← simpanan pernyataan pertama, DITUNDA
```

Jadi kalau di biner muatan `mov ax,X` muncul SEBELUM sebuah simpanan-immediate,
pernyataan yang memakai X ditulis **lebih dulu** di sumber — walau simpanannya
muncul belakangan.

Terbukti di `animvm`: menukar `sndmode = 2; sndptr = tune;` jadi
`sndptr = tune; sndmode = 2;` di EMPAT tempat plus `ticks`/`prevtop` menaikkan
penjajaran **2.799 → 2.860** tanpa mengubah satu byte pun panjangnya.

**Cara memakainya:** jangan membaca urutan pernyataan dari urutan SIMPANAN —
baca dari urutan MUATAN REGISTER.

## ⚠⚠ DERETAN SIMPANAN BERNILAI SAMA: urutan sumber TIDAK memberi sinyal apa pun

Dibuktikan di `main` 0x0686..0x069e (2026-07-31), lewat HASH, bukan lewat angka
agregat. Di sana biner menyimpan nol ke ENAM global berturut-turut dari satu
register (`mov [0x844],ax` … `mov [0x848],ax`).

Enam varian sumber dibuat — tiap kali SATU penugasan nol yang berbeda dipindah
ke depan blok. Keenam `.OBJ` keluar **byte-identik** (SHA1 `af9b4ad4637d0cf8`,
4.214 B) dan GLOBAL-nya sama persis (3.270). Jadi:

* Untuk deretan simpanan bernilai SAMA dari SATU register, urutan pernyataan
  sumber tidak memengaruhi kode sama sekali. Mencocokkan urutan simpanannya
  MUSTAHIL lewat penataan ulang sumber — pengungkitnya harus yang lain
  (kemungkinan urutan alokasi/deklarasi simbol).
* Ini menajamkan aturan "MUATAN mengikuti sumber, SIMPANAN ditata ulang": kalau
  tidak ada muatan pembeda, sumbernya bukan cuma sinyal lemah — ia BUKAN sinyal.

Sekaligus mengoreksi catatan lama di `main_.c` yang menyalahkan "memindah enam
pernyataan". Biayanya (−108 GLOBAL) datang dari SATU akibat: membuat nol itu
HIDUP lebih awal, sehingga `0x140` terusir dari BX ke AX dan seluruh blok
memilih register berbeda. Satu penugasan pun sudah cukup memicunya.

⚠ Jangan pakai daftar geseran untuk memutuskan di sini: varian yang ditolak ini
memendekkan geseran 4 → 2 dan menaikkan TERJAJAR, sambil menurunkan GLOBAL 108.

## ⭐ `a[i].f` dan `(a+i)->f` IDENTIK — sebuah kelas probe yang tertutup permanen

Diuji di `nvar` (2026-07-31), ketiga akses record sekaligus diganti bentuk
penunjuk. `.OBJ` keluar BYTE-IDENTIK (SHA1 `09a5d68cccfbb83b`, 551 B).

MS C 1.04 meruntuhkan indeks larik-of-struct dan aritmetika penunjuk ke pohon
yang sama sebelum memilih kode. Jadi memindah-mindahkan antara kedua bentuk itu
TIDAK PERNAH mengubah keluaran — jangan buang probe ke sana lagi. Ini berbeda
dari `*(char *)p` vs `*p`, yang mengubah TIPE dan karenanya memang berpengaruh.

## ⭐⭐ PROFIL CELAH — pisahkan "kurang DITULIS" dari "murni REGISTER" lebih dulu

Alat: `python src_c/verify/gapprof.py --semua`. Memakai difflib yang SAMA dengan
metrik GLOBAL, jadi pasti konsisten. Ia mendaftar celah tak-tercocokkan menurut
UKURAN, bukan menurut jumlah.

Bacanya:
* celah TERBESAR >= 20 B  -> masih ada STRUKTUR yang belum ditulis; garap volumenya
* rata-rata celah 1-2 B   -> kelas ALOKASI REGISTER; JANGAN diperlakukan sbg volume

Sapuan pertama (2026-07-31) mengubah urutan prioritas seluruh sisa pekerjaan:

```
nvar     411/566  (72,6%)  155 B / 92 celah  terbesar 22 B  -> VOLUME
animvm  2900/3040 (95,4%)  140 B /114 celah  terbesar  3 B  -> REGISTER
pickvar 1654/1730 (95,6%)   76 B / 47 celah  terbesar 10 B  -> REGISTER
loadcon  687/739  (93,0%)   52 B / 41 celah  terbesar  7 B  -> REGISTER
place    501/503  (99,6%)    2 B /  2 celah  terbesar  1 B  -> REGISTER
f498c    162/165  (98,2%)    3 B /  3 celah  terbesar  1 B  -> REGISTER
main_   3378/4219 (80,1%)  841 B /514 celah  terbesar 14 B  -> REGISTER
```

`nvar` adalah SATU-SATUNYA yang masih berprofil volume, dan gumpalannya rapat:
0x41b4=12 B, 0x4216=16 B, 0x4228=22 B — 50 dari 155 byte dalam jendela 0x41b4..0x423e.
Semua fungsi lain, termasuk `main` yang angkanya paling rendah, sudah lengkap
secara struktur. Persentase RENDAH tidak berarti "masih banyak yang belum
ditulis" — itu keliru yang dipegang berminggu-minggu.

## ⭐⭐⭐ LITERAL ALAMAT BISA JADI SIMBOL — CEK SEBELUM MENERIMANYA

`main_` 4.205 -> **4.215/4.219 (99,9%)**, celah 14 -> **4 byte**. Satu perubahan.

`page = 0x26c; page2 = 0x284;` ternyata bukan literal sama sekali: 0x26c dan
0x284 adalah `pbufA` dan `pbufB`, dua penyangga halaman yang SUDAH dideklarasikan
di `drawball.c`. Bentuk yang benar:

```c
extern char pbufA[], pbufB[];
page  = (int)pbufA;
page2 = (int)pbufB;
```

`&larik` memancarkan `mov reg,offset` (slot relokasi) lalu simpanan yang
DITUNDA — persis bentuk asli `mov bx,26ch / mov cx,284h` dengan kedua simpanan
sesudah `push`. Bentuk literal memancarkan simpanan-immediate 6 byte dan
menggeser seluruh fungsi.

⚠ INI MENJELASKAN KENAPA DUA ITERASI SEBELUMNYA MELESET. `page2 = page + 0x18`
memberi PANJANG yang benar (dan karenanya +329 waktu itu) tapi kodenya salah;
ia bertahan dua kali uji-ulang justru karena panjangnya kebetulan pas. Yang
membongkarnya bukan pengukuran lagi, melainkan satu pertanyaan yang belum
pernah ditanyakan: "apakah angka ini simbol?"

⭐ ATURAN: sebelum menerima literal heksa 3-4 digit di rentang DGROUP sebagai
literal, CEK apakah ia alamat simbol yang sudah dikenal (grep `@0xNNN` di
seluruh `src_c/src/`). Satu grep, dan ia menjelaskan bentuk kode sekaligus.

## ⚠ BX vs SI: BAWAAN kompiler adalah BX — dan probe TIDAK bisa memaksanya

`probes/probeC.c` (lima varian) menguji apa yang membuat MS C memakai ULANG
register yang baru mati (SI) alih-alih mengambil BX. Semua variasi yang masuk
akal dicoba:

```
C1 buf LOKAL (indeks [bp+si+K], persis main_)   -> mov bx
C2 buf PARAMETER (penunjuk)                     -> mov bx
C3 ada nilai lain HIDUP melintasi uji           -> mov bx
C4 hasil indeks dipakai LAGI sesudah gelung     -> mov bx
C5 penunjuk record dipakai DUA kali di syarat   -> mov bx (dua kali)
```

KELIMANYA memakai BX. Jadi bawaan MS C untuk bentuk ini memang BX, dan tak satu
pun faktor tingkat-pernyataan mengubahnya.

⭐ ARTINYA: pilihan SI di biner asli BUKAN akibat bentuk sumber lokal, melainkan
keadaan alokator SE-FUNGSI yang tidak bisa direproduksi oleh probe kecil. Untuk
situs seperti ini (`main_` 0x0c83, `place` 0x4fd4), probe TIDAK akan menjawab —
yang dibutuhkan pemahaman tentang bagaimana MS C mewariskan keadaan register
antar-blok, dan itu belum ada.

⚠ Ini BATAS TEKNIK PROBE yang pertama ditemui. Probe menjawab pertanyaan
"faktor apa di sekitar sini?", TAPI tidak menjawab "keadaan apa yang diwarisi
dari jauh". Kalau semua varian probe memberi jawaban SAMA, itu tandanya
pertanyaannya salah tingkat — naikkan cakupannya, jangan tambah varian.

## ⭐⭐ PEMETAAN LEWAT PENANDA — pastikan blok sumbernya SEBELUM mendiagnosis

Cara: sisipkan pemanggilan unik tanpa argumen (`f2fde();`) di blok kandidat,
kompilasi, lalu DIFF `.OBJ`-nya terhadap build dasar. Titik `insert` di difflib
adalah alamat tempat blok itu benar-benar dipancarkan. Hapus penandanya lagi.

⚠ JANGAN mencari penandanya dengan menebak pola `call` di disassembly — terlalu
banyak kandidat. DIFF terhadap build dasar memberi alamatnya TEPAT.

Ini memecahkan `main_` 0x0b39 sesudah dua iterasi analisis yang berputar. Dugaan
"blok sebelum `again2:`" SALAH: penandanya mendarat di **0x0ab2**, jadi `again2`
ada di sana dan `cmp` di 0x0b3c sebenarnya milik `if (cursel == -1) goto ...`
JAUH di bawahnya. Begitu pemetaannya pasti, perbaikannya jelas dalam satu
percobaan.

## ⭐⭐ `goto` KE LABEL YANG BENAR — MS C meruntuhkan rantai, jadi PILIH sasarannya

`main_` 4.203 -> 4.205. Sumber kita `goto endcase2` (label yang badannya cuma
`break`); MS C meruntuhkannya jadi lompatan LANGSUNG ke `restart`. Asli melompat
ke UJI EKOR (`if (cursel == -1) goto restart; goto again2;`) yang letaknya tepat
sebelum `endcase2`.

Keduanya SETARA secara semantik — lewat uji ekor, `cursel == -1` tetap berakhir
di `restart`. Yang beda cuma sasaran `jmp`-nya. Perbaikannya: beri LABEL pada
uji ekor (`tail2:`) dan lompat ke sana.

⭐ POLANYA: kalau `jmp` kita menunjuk sasaran yang lebih JAUH ke hilir daripada
asli, kemungkinan besar kita melompat ke label yang badannya kosong/`break` dan
kompilernya meruntuhkan rantai. Cari titik ANTARA yang setara, beri label di
situ, dan lompat ke sana.
⚠ per-TEMPAT: padanannya di `case 3` (`goto endcase3` -> label uji ekor)
DITOLAK, 4.205 -> 4.204 — di sana ujinya justru SESUDAH label.

## ⭐⭐ RANTAI PERBANDINGAN `switch` = KEBALIKAN urutan `case` di sumber

Dibuktikan dengan `probes/probeB.c` (lima varian, satu kompilasi):

```
sumber case 3,2      -> rantai  cmp 2 , cmp 3
sumber case 2,3      -> rantai  cmp 3 , cmp 2
sumber case 3,2,1    -> rantai  cmp 1 , cmp 2 , cmp 3
```

Berlaku juga kalau badan cuma `break` (tanpa `continue`) dan kalau switch-nya
dibungkus `if` — jadi ini sifat murni urutan label.

⚠ JANGAN dikacaukan dengan aturan "urutan `case` = urutan ALAMAT BADAN".
KEDUANYA benar dan mereka BERGERAK BERLAWANAN: badan mengikuti urutan sumber,
rantai perbandingan membalikkannya. Karena itu kalau case punya badan MASING-
MASING, menukar urutannya memperbaiki rantai TAPI merusak badan (diukur di
`main_`: 4.201 -> 4.199, ditolak).

⭐ YANG BISA DIPERBAIKI: kelompok label yang BERBAGI badan
(`case 2: case 3: <badan>`). Di situ urutan label tidak memengaruhi tata letak
badan sama sekali, jadi ia bebas ditukar untuk mencocokkan rantai. `main_`
baris 403: `case 2: case 3:` -> `case 3: case 2:`, GLOBAL 4.201 -> 4.203.

## ⭐⭐⭐ PENJAGA POSITIF + `if/else` vs `continue` — memilihkan REGISTER

Menyelesaikan `f498c` (162/165 -> **165/165**). Ketiga byte itu ukurannya SAMA
(cuma field register `bx` vs `si`), jadi TIDAK ADA bentuk yang mengubah panjang
— yang berubah cuma pilihan alokator.

```c
/* SALAH — dua `continue`, tiga blok dasar terpisah */
if (sel[i] < 0) continue;
n = nvar(...);
if (n <= 0) { printf(...); continue; }
drawpair(...);

/* BENAR — penjaga POSITIF, badan bersarang, `if/else` */
if (sel[i] >= 0) {
    n = nvar(...);
    if (n <= 0) printf(...);
    else        drawpair(...);
}
```

Dengan `continue`, alokator memilih **BX** untuk penunjuk `tab`; dengan bentuk
bersarang ia MEMAKAI ULANG **SI** seperti asli. Jadi bentuk penjaga menentukan
pilihan register, bukan cuma tata letak lompatan.

⭐ INI PENGUNGKIT PERTAMA YANG TERBUKTI untuk kelas "beda register murni".
Sebelumnya kelas itu dianggap tak terkendali. Kalau sebuah fungsi cuma beda di
field register dan panjangnya TEPAT, periksa apakah ada `continue`/`break` yang
bisa ditulis ulang sebagai penjaga positif bersarang.

⚠ TIDAK BERLAKU UMUM. Bentuk setara di `place`
(`while (j < n) { i = flag[j]; if (i < 0) break; ... }` ->
`while (j < n && (i = flag[j]) >= 0)`) memberi **501 -> 473**. DITOLAK.
Seperti biasa: per-TEMPAT, dan harus DIUKUR.

## ⭐⭐⭐ WAKTU SIMPANAN: bawaannya DITUNDA — simpanan SEGERA itu gejala
## TEKANAN REGISTER, bukan bentuk sumber (probeA, 2026-07-31)

Empat situs tersisa (`nvar` 0x41b2, `loadcon` 0x5115, `pickvar` 0x43a5,
`main_` 0x0126) semuanya soal KAPAN sebuah nilai disimpan ke memori. `probeA.c`
menguji lima varian sumber dari bentuk yang sama untuk mencari pemicunya.

**Hasilnya menutup satu jalur penyelidikan penuh.** Untuk bentuk
"hitung `q`, lalu uji `idx + 1 < n`", MS C **SELALU MENUNDA** simpanan `q`
sampai sesudah uji — apa pun bentuk sumbernya:

```
pa1  q; sel = -1; if (idx+1<n)          -> DITUNDA
pa2  q; if (idx+1<n) ... else ...       -> DITUNDA   (jarak ke uji: tidak berpengaruh)
pa3  q dipakai LAGI di dalam badan       -> DITUNDA   (pemakaian ulang: tidak berpengaruh)
pa5  q juga jadi nilai balik             -> DITUNDA
pa4  uji memakai `q`: `if (q + 1 < n)`   -> SEGERA!   <- satu-satunya yang beda
```

`pa4` memancarkan `mov [bp+2],bx` lalu `inc bx / cmp bx,[n]` — menyimpan dulu
supaya REGISTERNYA bisa dipakai ulang seketika.

⭐ KESIMPULAN: simpanan-segera muncul kalau register itu DIBUTUHKAN SEGERA
sesudahnya. Di biner asli `pickvar`, DX satu-satunya register bebas (AX/CX
memegang `list[idx]`, SI memegang penunjuknya), jadi kompiler menyimpan `q`,
memakai ulang DX untuk uji, lalu MEMUAT ULANG `idx` ke DX yang sama.

⚠ ARTINYA: mencari "bentuk sumber yang benar" di keempat situs itu SIA-SIA —
bentuknya sudah benar. Yang harus diubah adalah TEKANAN REGISTER di blok itu,
yaitu membuat nilai LAIN tetap hidup. Ini juga menjelaskan kenapa tiga permutasi
urutan pernyataan di `pickvar` dan sepuluh varian probe di `loadcon` semuanya
gagal: semuanya menyerang faktor yang memang tidak berpengaruh.

## ⭐⭐ KONSTANTA yang dipakai >1 KALI dimaterialisasi di PUNCAK BLOK

Berlaku untuk nilai APA PUN, bukan cuma nol. Empat kali membayar di `main_`
(+203, +4, +2, lalu +5 dan +5 untuk nilai `1`).

```
ASLI  mov ax,1 / mov [sub],80h / ... / mov [lvl],ax
KITA  mov [sub],80h / mov ax,1 / ...
```

Kalau sebuah konstanta dipakai LEBIH DARI SEKALI (dua global, atau satu global
plus argumen panggilan), MS C menaruhnya di register dan memuatnya di PUNCAK
blok — SEBELUM simpanan-immediate lain di blok yang sama. Kalau dipakai sekali,
ia memancarkan `mov [glob],imm` (6 byte).

⭐ PERBAIKANNYA: pindahkan penugasan yang MEMAKAI konstanta itu ke DEPAN
penugasan lain di blok yang sama. Simpanannya sendiri tetap ditata ulang, jadi
jangan menilai dari urutan simpanan.

⭐ GEJALA: celah 3 byte tepat di batas antara `mov [glob],imm` dan `mov reg,imm`
yang bertukar tempat.

## ⭐⭐ ARAH SYARAT + BADAN DITUKAR: semantik sama, byte BEDA

Bentuk `if (A) X; Y;` dan `if (!A) Y; X;` menghasilkan kode yang SETARA tapi
TIDAK identik. Yang pertama memancarkan lompatan-syarat untuk `!A`, yang kedua
untuk `A` — dan kedua `jmp` sesudahnya ikut TERTUKAR.

```
KITA  je  L / jmp X / L: jmp Y        ASLI  jne L / jmp Y / L: jmp X
```

Tiga situs di `main_` diperbaiki dengan ini (2026-07-31): +5, +4, +5 -> 99,3%.
Semuanya berbentuk "uji lalu dua lompatan" di ekor sebuah `case`.

⭐ GEJALANYA MUDAH DIKENALI: celah 3-4 byte tepat di `jcc` yang diikuti DUA
`jmp` berurutan, dengan sasaran yang sama tapi TERBALIK urutannya. Kalau
melihat itu, balik syaratnya dan tukar badannya.

⚠ ARAHNYA per-TEMPAT, bukan aturan global. Di `main_` dua situs perlu `== -1`
(dari `!= -1`) dan satu situs perlu justru `!= -1` (dari `== -1`). UKUR.

## ⭐⭐⭐ GELUNG yang keluar lewat JATUH-TEMBUS harus ditulis dengan `goto`

Ini menyelesaikan `animvm` (3.040 byte, fungsi terbesar yang tersisa):
2.921 -> 2.961 dari satu bentuk, lalu 3.040/3.040 sesudah satu penghapusan.

Biner sering memancarkan gelung yang KELUAR lewat jatuh-tembus dari uji terakhir:

```
22c6: (puncak)
  ...
  jne 0x22c6        <- uji 1 gagal -> ulang
  mov ax,[3AEh]     <- MEMUAT ULANG (batas blok)
  ...
  jne 0x22c6        <- uji 2 gagal -> ulang
  inc word ptr [3AEh]  <- JATUH-TEMBUS keluar, tanpa jmp apa pun
```

Tidak ada bentuk gelung C yang memberi itu:
* `for(;;)` + `break`   -> keluar lewat `jmp` MUBAZIR ke instruksi berikutnya
* `do {} while (A || B)` -> jatuh-tembus BENAR, tapi satu blok jadi uji kedua
                            MEMAKAI ULANG SI alih-alih memuat ulang
* `for` + `continue`    -> muat-ulang BENAR, `jmp` mubazirnya tersisa

Yang memberi KEDUANYA adalah **dua `goto` ke satu label**:

```c
sndloop:
    scrptr++;
    if (*scrptr != 0xff) goto sndloop;
    if (*++scrptr != 0xff) goto sndloop;
    scrptr++;              /* jatuh-tembus, tanpa jmp */
```

Tiap `goto` adalah batas blok (jadi operan kedua memuat ulang), dan keluarnya
jatuh-tembus alami. Lima bentuk gelung sudah diukur di tempat ini; hanya ini
yang benar. ⭐ Kalau biner menunjukkan gelung tanpa `jmp` di jalan keluarnya,
JANGAN mencari bentuk gelung — tulis `goto`.

## ⚠⚠ PERBAIKAN YANG BENAR BISA BERUBAH JADI SALAH — ukur ulang sesudah tiap fix

Pelajaran (c) selama ini berbunyi "daftar dicoba & gagal hanya berlaku untuk
keadaan blok saat itu". Kebalikannya juga benar dan baru terbukti mahal:

`default: break;` di switch UTAMA `animvm` memberi **+13** saat gelung bunyi
masih salah — ia mengompensasi geseran 3 byte dengan menambah `jmp` kedua.
Begitu gelung bunyi diperbaiki jadi bentuk `goto`, `default:` yang sama justru
MENAHAN fungsi di 2.961. Menghapusnya -> **3.040/3.040**.

⭐ Karena itu: sesudah setiap perbaikan yang mengubah PANJANG, uji ulang
perbaikan-perbaikan sebelumnya di fungsi yang sama — terutama yang dulu hanya
memberi kenaikan KECIL. Kenaikan kecil sering berarti "menambal geseran",
bukan "benar".

⚠ Gejalanya terbaca dari data, bukan dari firasat: panjang KITA 3.043 vs 3.040
dan deretan celah 1-byte yang SEMUANYA displacement lompatan +3. Kalau semua
selisih displacement seragam, cari SATU sisipan sebesar itu — jangan
memperbaiki lompatannya satu per satu.

## ⭐⭐⭐ `default:` EKSPLISIT MEMANCARKAN `jmp` — dan letaknya menentukan

Dua kali membayar di `animvm` (2026-07-31): GLOBAL 2.901 -> 2.908 -> **2.921**.

MS C 1.04 meruntuhkan rantai lompatan (aturan lama), tapi sebuah `default:`
memaksa satu `jmp` TAMBAHAN yang tidak diruntuhkan:

1. **Switch BERSARANG, `break` dalam lalu `break` luar.** Tanpa `default:`
   keduanya runtuh jadi SATU `jmp`. Aslinya memancarkan DUA `jmp 0x1cd5`
   berturut di 0x21b4/0x21b7 — tepat sebelum tabel pindainya di 0x21ba.
   Menambah `default: break;` di switch DALAM memulihkannya (+7).

2. **Badan `case` terakhir yang KOSONG.** `case 0xff: break;` sebagai label
   TERAKHIR tidak memancarkan apa pun (jatuh keluar switch). Aslinya ada `jmp`
   di 0x23d1, tepat sebelum tabel utama 0x23d4. Menambah `default: break;`
   SESUDAH-nya memulihkan (+13).

⚠ LETAKNYA PENTING: `default:` di DEPAN `case 0xff` tidak berpengaruh sama
sekali (tetap 2.908). Yang bekerja hanya `default:` SESUDAH label terakhir —
karena yang dibutuhkan adalah badan `case` terakhir berhenti menjadi yang
terakhir.

⭐ GEJALA yang harus dicari: diff instruksi kasar melaporkan `insert @asli`
berupa satu `jmp` TEPAT SEBELUM tabel switch. Itu hampir selalu `default:` yang
hilang, bukan salah badan case.

## ⭐⭐ KAPAN `&&` vs BERSARANG BERPENGARUH — syaratnya SUBEKSPRESI BERSAMA

Aturan `&&` di bawah TIDAK berlaku di mana-mana. Empat titik data (2026-07-31):

```
nvar         syarat & badan berbagi `list[r]`,`list[r-1]` -> MERGE MEMPERBAIKI (+155, exact)
pickvar 207  berbagi `list[idx+1]`                        -> MERGE MEMPERBURUK (-87)
place   129  `sp->id`/`sp->row` vs badan `sp->spr`        -> BYTE-IDENTIK (b3ae839b60d6fec7)
pickvar 317  cuma skalar `idx` yang sama                  -> GLOBAL SAMA
```

PREDIKAT: pertukaran `&&` <-> bersarang hanya mengubah kode kalau syarat dan
badan (atau kedua syarat) berbagi SUBEKSPRESI MAJEMUK — muatan ber-indeks atau
lewat penunjuk seperti `list[r]`. Variabel SKALAR yang sama TIDAK cukup; field
BERBEDA dari penunjuk yang sama juga TIDAK cukup.

Konsisten dengan mekanismenya: yang jadi masalah adalah CSE yang harus BERTAHAN
melintasi cabang, dan hanya subekspresi majemuk yang layak di-CSE. Kalau tidak
ada yang perlu bertahan, kedua bentuk runtuh ke pohon yang sama.

⚠ ARAHNYA TIDAK BISA DITEBAK, hanya DIUKUR. `nvar` dan `pickvar` sama-sama
memenuhi predikat dan bentuk sumbernya nyaris identik (keduanya `- 100 ==`),
tapi jawabannya BERLAWANAN. Predikat menyaring MANA yang layak diprobe; ia tidak
menentukan hasilnya.

## ⚠ DIFF TINGKAT INSTRUKSI: slot relokasi memancing beda PALSU

Perbandingan byte men-wildcard slot relokasi, tapi DISASSEMBLY tidak — operannya
masih placeholder. Di `loadcon` itu membuat 44 situs terlihat beda padahal yang
NYATA cuma DUA; sisanya `call 0xffffdc92` vs `call 0x6e8b`, `mov ax,[0x5003]` vs
`mov ax,[0x3b4]`, dan sejenisnya.

Kalau memakai diff instruksi, ABAIKAN operan yang jatuh di slot relokasi, atau
bandingkan mnemonic + register saja.

## ⭐⭐⭐ `if (A) { if (B) ... }` vs `if (A && B)` — BUKAN sekadar gaya

Ini menyelesaikan `nvar` SEKALIGUS: GLOBAL 411/566 -> **566/566 byte-per-byte**,
dari satu perubahan. Aturan yang paling mahal-terlambat-ditemukan sejauh ini.

Bentuk BERSARANG memberi kompiler dua blok dasar. Karena alokasi register MS C
1.04 bekerja PER-BLOK-DASAR, ia lalu meng-CSE subekspresi yang dipakai di syarat
DAN di badan (`list[r]`, `list[r-1]`) lalu MENYIMPANNYA di temp supaya bertahan
melintasi cabang. Dua temp tambahan itu membesarkan bingkai 38h -> 3ch, dan
karena SEMUA lokal ikut bergeser +4, tiap rujukan `[bp+N]` di SELURUH fungsi
meleset satu byte.

Bentuk `&&` menjadikannya satu blok: tidak ada nilai yang perlu bertahan
melintasi cabang, temp kembali 3 kata, bingkai kembali 38h, dan seluruh fungsi
langsung cocok.

⚠ GEJALA YANG HARUS MEMICU KECURIGAAN — persis profil `nvar` sebelum diperbaiki:
* bingkai KITA lebih besar 2 kata dari asli, DAN
* deretan panjang celah SATU BYTE yang merata di seluruh fungsi (48 buah di
  `nvar`, semuanya cuma displacement `[bp+N]` yang bergeser), DAN
* satu gumpalan pekat di satu blok — di situlah `if` bersarangnya.

⚠ JANGAN mendiagnosis dari instruksi pertama yang beda. Di `nvar` gejala yang
paling menonjol adalah `cnt++` yang dipancarkan sebagai tumpahan temp alih-alih
`inc word ptr [mem]` — dan itu SESAT. Biner asli memakai KEDUA bentuk: bentuk
tumpahan di fase 1 (0x4100/0x4119) dan `inc word ptr` di fase 2 (0x41b2). Kita
pun sudah memancarkan `inc word ptr` di 0x4223. Bentuk `cnt++` tidak pernah jadi
soal; ia cuma AKIBAT dari tekanan temp yang disebabkan `if` bersarang. Empat
probe dihabiskan ke arah yang salah sebelum diagnosis ini benar.

## ⚠ PERCOBAAN YANG GAGAL BISA BENAR — cek ulang sesudah perbaikan LAIN

Memecah `u4c = *++u54;` jadi `u54++; u4c = *u54++;` di `animvm` `case 0x0c`
dicoba di tahap 9 dan **gagal**: panjang melonjak +10 tanpa menaikkan
penjajaran, jadi dibatalkan. Percobaan yang SAMA PERSIS dicoba lagi satu
iterasi kemudian — setelah perbaikan yang TIDAK BERHUBUNGAN di blok yang sama
(pemulihan tanda yang hasilnya dibuang) — dan kali ini **berhasil**:
penjajaran 2.748 → 2.753 dan satu geseran lunas.

Sebabnya: alokasi register se-BLOK. Selama masih ada bentuk yang salah di blok
itu, bentuk yang BENAR di tempat lain bisa terlihat memburuk. **Daftar "sudah
dicoba & gagal" hanya berlaku untuk keadaan blok saat itu.** Kalau blok yang
sama kemudian berubah, percobaan yang tercatat gagal layak diulang.

## ⭐ NILAI YANG DIBUANG tetap memancarkan kode — dan itu bisa BUG ASLINYA

Di `animvm` `case 0x0c` biner menghitung pemulihan tanda 0xC8 lalu **membuang
hasilnya**: AX ditimpa `mov ax,si` tanpa pernah disimpan balik, dan fungsi di
hilirnya menerima nilai MENTAH. Bentuk C-nya adalah pernyataan-ekspresi tanpa
penugasan:

```c
u44 = *scrptr++;
(u44 >= 0xc8) ? u44 - 0x100 : u44;      /* hasil DIBUANG */
```

Kelihatannya bug di gim aslinya (penulisnya lupa menugaskan balik), tapi
rekonstruksi byte-identical harus menirunya. Penjajaran naik 2.700 → 2.748.

⚠ **PER-CASE, bukan pola umum.** `case 0x03` beberapa baris di atasnya
melakukan hal yang SAMA persis TAPI menyimpan hasilnya balik. Sudah diuji:
membuangnya di sana justru menurunkan penjajaran 2.748 → 2.722 dan memunculkan
geseran baru. Dua tempat, dua perilaku — jangan diseragamkan.

Ini varian ketiga dari pola yang sama (lihat juga TERNARY vs `if/else`):
**bentuk yang benar ditentukan per-TEMPAT dan harus diukur, bukan disimpulkan
dari tempat lain di fungsi yang sama.**

## ⚠⚠ DIVERGENSI BISA JAUH DARI SEBABNYA — alokasi register itu se-BLOK

Kasus paling mahal sesi ini, dan pelajarannya berlaku umum.

`animvm` @0x1afd berbeda: asli `mov ax,3 / imul word ptr [bp+10h]` (5 byte),
kita `mov ax,var / mov bx,3 / imul bx` (8 byte). Divergensinya terlokalisasi
sempurna ke SATU instruksi. Tiga probe menguji tiga hipotesis tentang bentuk
perkalian itu — **ketiganya gagal**, dan kesimpulannya sempat ditulis sebagai
"tidak bisa dihasilkan dari perkalian yang ditulis programmernya".

Sebab sebenarnya ada **30 instruksi lebih jauh**: dua pernyataan
(`slot = c2; curz = c1;`) ditaruh SESUDAH `printf(...)` padahal aslinya
SEBELUM. Begitu diperbaiki, kompiler memuat `c1`/`c2` ke register di AWAL
blok, tekanan registernya berubah, dan `imul word ptr [mem]` **plus** pemilihan
`DI` muncul sendiri — tanpa menyentuh ekspresi perkaliannya sama sekali.

Hasilnya: 8 geseran jadi 4, penjajaran 2.642 → 2.700, dan EMPAT geseran yang
sudah dicap "buntu" lunas sekaligus.

**Aturannya:** kompiler ini mengalokasikan register **per-BLOK DASAR**, bukan
per-pernyataan. Instruksi pertama yang berbeda menunjukkan DI MANA akibatnya
terlihat, **bukan di mana sebabnya**. Kalau probe atas bentuk lokal semuanya
gagal, berhentilah menguji bentuk itu — periksa URUTAN PERNYATAAN di seluruh
blok, terutama yang menyentuh variabel yang sama.

## ⚠ Hasil NEGATIF (KONTEKS DIKOREKSI): `imul word ptr [mem]`

`animvm` @0x1afd memancarkan `mov ax,3 / imul word ptr [bp+10h]` (5 byte),
sedangkan semua bentuk C yang wajar memberi `mov ax,<var> / mov bx,3 / imul bx`
(8 byte). TIGA probe menutup tiga hipotesis sekaligus — semuanya GAGAL:

| hipotesis | probe | hasil |
|---|---|---|
| urutan operan (`3 * a` vs `a * 3`) | probe21a/b | IDENTIK, tidak berpengaruh |
| konteks indeks larik / dua penunjuk hidup | probe20a-d | selalu `imul bx` |
| skala indeks larik STRUCT (`t[a].id`) | probe22a-c | `mov bx,6 / imul bx`, tanpa `shl` |

Ketiga probe itu benar: **bentuk perkalian memang tidak menentukan.** Yang
salah adalah kesimpulan yang sempat ditarik darinya ("sumbernya tidak
diketahui"). Sumbernya adalah TEKANAN REGISTER di blok itu, dan itu diatur
oleh urutan pernyataan yang jauh di bawahnya — lihat bagian di atas.
Ketiga probe tetap berguna sebagai bukti bahwa bentuk lokalnya bukan jawabannya.

## ⭐ CAST PENUNJUK ≠ TIPE PENUNJUK — `*(char *)p` bukan `*p`

Kalau sebuah global dipakai sebagai penunjuk, **deklarasikan tipenya penunjuk**.
Mendeklarasikannya `int` lalu mengecor di tiap pemakaian menghasilkan kode lain:

| sumber | pancaran |
|---|---|
| `extern char *p;` … `*p` | `mov si,[p]` (4 byte) — langsung ke SI |
| `extern int p;` … `*(char *)p` | `mov ax,[p]` + `mov si,ax` (5 byte) — lewat AX |

Efeknya bukan cuma satu byte per pemakaian. Bentuk cor membuat kompiler
**menahan nilainya di register** dan memakainya ulang, sedangkan tipe penunjuk
asli **MEMUAT ULANG dari memori tiap kali dirujuk**. Di fungsi yang membaca
kursor beberapa kali, itu mengubah seluruh bentuk kode, bukan panjangnya saja.

Terbukti 2026-07-31 pada dua fungsi sekaligus, keduanya langsung COCOK penuh:
`f278e` 141/149 → **149/149**, `f2714` 76/122 → **122/122**. `f2714` sempat
salah didiagnosis sebagai soal URUTAN PERNYATAAN dan tiga bentuk sudah dicoba
dan gagal; yang benar soal TIPE.

**Aman untuk DGROUP:** `gendata.py` memancarkan tiap simbol BUKAN-larik sebagai
`int` apa pun tipe yang tertulis di deklarasi `extern`-nya (lihat cabang
`if not arr:`), jadi mengganti `extern int p;` → `extern char *p;` TIDAK
menggeser DGROUP. Sudah diuji: `gdata.c` tidak berubah satu byte pun.

## ⭐ SLOT BINGKAI berisi KONSTANTA `long` = VARIABEL, bukan literal (probe19)

Kalau di disassembly ada slot bingkai yang diisi sebuah konstanta `long`
**sekali di awal fungsi** lalu dibaca berkali-kali, itu **variabel `long` yang
memang ditulis programmernya** — bukan literal yang "dipromosikan" kompiler.

`probe19.c` menguji tiga bentuk pembagi dengan ekspresi yang identik:

| sumber | pancaran di titik pembagian | slot bingkai |
|---|---|---|
| `... / 100` | `xor cx,cx` / `mov dx,64h` | tidak ada |
| `... / 100L` | `xor cx,cx` / `mov dx,64h` (IDENTIK) | tidak ada |
| `long hun; hun = 100; ... / hun` | `mov cx,[bp+16h]` / `mov dx,[bp+14h]` | ADA |

Dua yang pertama **tidak bisa dibedakan** — akhiran `L` tidak mengubah apa pun.
Hanya varian ketiga yang memberi slot, dan ia juga memancarkan `xor cx,cx /
mov dx,64h` **di awal fungsi** (bukan di titik pembagian), terjalin dengan
pernyataan sebelumnya. Itulah tanda pengenalnya.

Probe yang sama menjawab pertanyaan kedua: **jangan mengecor `(long)` pada
subekspresi `int`.** `(long)(tx - fx) + <long>` memperluas tanda SEGERA dan
menyimpan dua kata ke temp; `(tx - fx) + <long>` menyimpan hasil `int`-nya saja
lalu memperluas tanda di titik penjumlahan — dan yang kedua itu yang dipakai
aslinya. Cor eksplisit yang secara semantik mubazir tetap MENGUBAH kode.

Ini yang menuntaskan `f2823` (397 byte) dari 118/397 langsung ke **397/397**.

## ⭐ RUANG BINGKAI TAK TERRUJUK: ukur dari SLOT YANG TERLIHAT, bukan dari temp

Kalau sebuah fungsi memesan bingkai lebih besar daripada lokal yang benar-benar
dirujuk, **pembagian sisa ruang antara temp dan lokal-mati TIDAK bisa diketahui
dari biner** — tidak ada satu pun instruksi yang menyentuhnya.

Jadi jangan mencoba menebak jumlah temp. Pilih ukuran pengganjal supaya
**slot yang TERLIHAT jatuh di offset yang benar** dan totalnya sama dengan
`sub sp` asli. Kode yang dipancarkan jadi identik, karena hanya slot terlihat
yang muncul di instruksi.

Contoh (`f171f` @0x171f, 2026-07-31): bingkai asli 0x54, satu-satunya slot
terrujuk `[bp+0x52]`. Dengan `char pad[74]` (mengira temp 8 byte) hasilnya
0x4E dan `t` mendarat di 0x4C — 8 byte meleset. Dengan `char pad[80]`
bingkainya 0x54, `t` di 0x52, dan seluruh 114 byte **cocok persis**.

⚠ **Ruang bawah itu bisa juga MILIK TEMP** — jangan otomatis menambah
pengganjal. `f15d0` @0x15d0 punya bingkai 0x0A dengan slot terlihat di
[bp+6] dan [bp+8]; menambahkan `char pad[6]` membuat bingkainya 0x10 karena
kompiler sudah memesan 6 byte temp sendiri. Tanpa pengganjal: 80/80 **cocok**.

Jadi urutan kerjanya: **kompilasi dulu TANPA pengganjal**, lihat `sub sp` yang
keluar, baru tambahkan pengganjal kalau bingkainya masih kurang.

⚠ Bedakan dari kasus `main`: di sana membesarkan penyangga adalah KOMPENSASI
yang salah, karena penyangga itu **dirujuk** dan menggesernya memindahkan
offset yang jelas terlihat di biner. Aturan ini hanya berlaku untuk ruang yang
memang tidak pernah disentuh.

## ⚠ Menambah nama extern baru butuh TIGA langkah, bukan satu

`buildall.ps1` **tidak** menjalankan `gendata.py`, dan **tidak** ikut
mengompilasi ulang `gdata.c`. Jadi setelah menambah `extern ... /* @0xNNN */`
di sumber mana pun:

```
python src_c/build/gendata.py            # 1. regenerasi gdata.c
pwsh src_c/build/compile.ps1 -Name gdata # 2. WAJIB — buildall melewatkannya
pwsh src_c/build/buildall.ps1            # 3. sisa modul
```

Melewatkan langkah 2 memberi `Unresolved Externals` untuk nama yang jelas-jelas
sudah ada di `gdata.c` — gejala yang menyesatkan karena berkasnya benar,
hanya `.OBJ`-nya yang basi.

**Hal yang sama berlaku untuk `stubs.c`.** `buildall.ps1` hanya mengompilasi
modul yang terdaftar di `manifest.txt`; `gdata.c` dan `stubs.c` TIDAK terdaftar,
jadi keduanya harus dikompilasi manual:

```
pwsh src_c/build/compile.ps1 -Name stubs   # sesudah menambah/menghapus stub
```

## ⚠ `link.ps1` menautkan SEMUA `.OBJ` di `out/`, bukan hanya yang di manifest

Begitu sebuah `.c` baru ditaruh di `src/`, `buildall.ps1` mengompilnya dan
`link.ps1` otomatis ikut menautkannya. Kalau fungsi itu masih punya stub di
`stubs.c`, keduanya bentrok. Cabut stubnya di saat yang sama.

## ⭐ SISIR SASARAN `call` untuk menemukan fungsi yang belum tergarap

Cara termurah mencari pekerjaan berikutnya: kumpulkan semua sasaran `call`
(`e8` + rel16) di wilayah kode game, lalu buang yang sudah tercakup rentang
manifest. Sisanya adalah fungsi yang belum pernah disentuh.

Hasil 2026-07-31 (14 sasaran belum tercakup) membuka wilayah **0x2714..0x29B0
(668 byte, sedikitnya tiga fungsi)** yang sebelumnya tidak ada di peta mana
pun — termasuk 0x2823, interpolator parabola yang sudah dikenal dari jalur
port. Sisanya berada di dalam `main` (belum masuk manifest) dan `animvm`.

```python
for i in range(len(code)-2):
    if code[i] == 0xe8:
        t = (i + 3 + struct.unpack_from('<h', code, i+1)[0]) & 0xffff
```

## ⚠ 1.200 BYTE NOL di 0x5F93..0x6442 — BUKAN kode

Wilayah antara `setup` (0x5F90, tiga byte) dan rutin BIOS di 0x6443 berisi
**1.200 byte nol berturut-turut**. Itu bukan kode game dan tidak perlu
direkonstruksi. Angka target rekonstruksi mana pun yang menghitung wilayah
`<0x69d7` sebagai kode akan **terlalu besar 1.200 byte**.

Ditemukan 2026-07-31 saat menggarap `setup`, yang perkiraan ukurannya semula
"≤1.210 byte" hanya karena entri manifest berikutnya jauh. Ukuran sebenarnya
**3 byte**.

⚠ Ada juga rutin kecil di **0x6443** (7 byte: `mov al,4 / mov ah,0 / int 10h /
ret`) yang belum tercakup modul mana pun — `text.asm` baru mulai di 0x644A.

## ⚠ `setup` membuktikan lagi: tidak semua fungsi berasal dari C

`setup` aslinya `sub ax,ax / ret` — TIGA byte, tanpa prolog. MS C 1.04 selalu
memancarkan `push bp / mov bp,sp ... pop bp`, jadi `setup() { return 0; }`
memberi TUJUH byte. Ditulis sebagai `.asm` dan langsung cocok.
**Kalau sebuah fungsi tidak punya prolog `push bp`, jangan coba menulisnya
dalam C sama sekali.**

## Fungsi assembly (jangan direkonstruksi sebagai C)

Prolog MS C 1.04 selalu `push bp; sub sp,N; mov bp,sp`. Sensus 144 fungsi:

| | jumlah | byte |
|---|---|---|
| prolog C → hasil kompilasi | 93 | 26.445 |
| bukan prolog C → assembly tulisan tangan / rutin pustaka | 51 | 2.542 |

Yang assembly termasuk **semua primitif grafis**: `672f` (blit sprite), `6453` (teks),
`5cbb` (garis/span), `6524`/`657c`/`6869` (blit bermasker) — semuanya berpola
`push bp; push es; mov bp,sp`, menyimpan ES karena menulis ke memori video.
Juga `5a5b` (RNG kongruen linier) yang memakai `mul` dan mengambil word tinggi dari DX —
mustahil ditulis di C 1983 karena `unsigned long` belum ada.

## Sisa pekerjaan — ANGKA DIKOREKSI 2026-07-29

Perkiraan lama (**19.750 byte**) TERLALU KECIL. Sebabnya: ukuran di
`work/ghidra_out/functions.txt` menghitung hanya potongan pertama yang bersambung dari
sebuah fungsi. Fungsi yang badannya terpecah oleh lompatan dihitung jauh lebih kecil dari
sebenarnya. Contoh terbukti: `FUN_1000_18db` tercatat 1.229 byte, kenyataannya
**3.040 byte** (0x18db..0x24ba, epilog di 0x24b6).

Angka yang lebih jujur, dihitung dari wilayah alamat (bukan dari daftar fungsi):

| wilayah | byte | keterangan |
|---|---|---|
| Segmen kode seluruhnya | 36.976 | 0x0000..0x9070 |
| Wilayah pustaka (≥0x69d7) | 9.881 | rutin `MC.LIB` — cukup di-link |
| **Wilayah kode game (<0x69d7)** | **27.095** | yang harus ditulis ulang |
| — di antaranya assembly tulisan tangan | ±1.200 | primitif grafis (`5cbb`,`6453`,`6524`,`657c`,`672f`,`6869`,`6939`) |
| — sisanya kode C | **±26.000** | target rekonstruksi sebenarnya |

Jadi targetnya **±26.000 byte, bukan 19.750** — sekitar 32% lebih besar.
Kemajuan 787 byte = **±3,0%**, bukan 4,0%.

Batas pustaka **0x69d7 sudah TERBUKTI, bukan taksiran**: `libmatch.py`
mencocokkan 23 modul MC.LIB byte-per-byte ke 0x69d7..0x9062 (9.935 byte), dan
modul pertamanya `CXM33` mulai tepat di 0x69d7. Jalankan
`python src_c/verify/libmatch.py` untuk daftar simbol + alamatnya — itu juga
cara tercepat memastikan sebuah "stub" sebenarnya rutin pustaka.

**Aturan baru:** jangan percaya `size=` di `functions.txt`. Selalu cek di mana epilog
(`add sp,N; pop bp; ret`) yang cocok dengan `sub sp,N` di prolog.

## ⭐⭐ ORACLE BATCH: satu peluncuran DOSBox = puluhan kompilasi

`src_c/verify/sweep.py <dir> [--pola REGEX]` menyalin tiap `*.c` di `<dir>` ke
folder DOS, menyusun SATU `[autoexec]` berisi `MC1 x` + `MC2 x` untuk semuanya,
menjalankan DOSBox SEKALI, lalu membongkar tiap `.OBJ` dan melaporkan panjang
kode + baris disassembly yang cocok `--pola`.

Sebelum ini tiap varian = satu peluncuran (~8 detik + overhead), jadi probe 5
varian menghabiskan satu iterasi penuh. Sekarang 16 varian selesai dalam satu
langkah — dan itulah yang membuka `main_`, `loadcon`, dan aturan-aturan di
bawah. **Kalau sebuah situs bertahan setelah 3-4 varian, jangan menambah varian
satu per satu; tulis 12-16 sekaligus di sumbu yang BERBEDA.**

⚠ **MC1 punya batas panjang BARIS.** Badan fungsi yang ditulis satu baris
memberi `Error 4: invalid lexical token` berulang-ulang — bukan sintaks yang
salah. Tulis varian dengan baris pendek seperti sumber biasa.

## ⭐ Kompilernya DUA FASE — dan alokasi register SELURUHNYA di MC2

`MC.BAT` menjalankan `MC1 %1` lalu `MC2 %1`. MC1 memancarkan **berkas QUAD**
`<nama>.Q` (kuadrupel, representasi antara bebas-mesin); MC2 membacanya,
menghasilkan `.OBJ`, lalu **MENGHAPUS** `.Q`-nya. String di `MC2.EXE`
mengkonfirmasi: `Can't open quad file`, `Invalid intermediate file`.

Konsekuensinya penting: **register tidak ada di quad.** Pilihan BX vs SI vs DI
adalah fungsi MURNI dari urutan quad. Jadi dua bentuk sumber yang menghasilkan
quad identik TIDAK MUNGKIN memberi kode berbeda — itu penjelasan mekanis untuk
pelajaran (t) ("kalau semua varian probe sama, pertanyaannya salah tingkat").

Untuk melihat quad-nya, jalankan MC1 SENDIRIAN (tanpa MC2) — berkasnya tersisa.
MC2.EXE sendiri dikompilasi dengan Lattice C 1.02 (string di offset 0x200).

## ⭐⭐ `while (A && B && C)` vs badan + `break`: PENJADWALAN SIMPANAN

Bentuk ini yang menutup `loadcon` (687/739 → 739/739):

```c
do { pick = rnd(cnt) + first;                     /* ASLI */
} while (lastgoal == sub && cnt >= 2 && pick == lastvar);

do { pick = rnd(cnt) + first;                     /* KITA — 1 byte lebih besar */
     if (lastgoal != sub) break;
     if (cnt < 2) break;
} while (pick == lastvar);
```

Maknanya identik, tapi dengan `break` di badan kompiler **MENUNDA** simpanan
`pick` melewati pemuatan `lastgoal`. Akibatnya AX masih terpakai, globalnya
masuk **BX** (`8b 1e` = 4 byte) dan bukan **AX** (`a1` = 3 byte):

```
ASLI  mov [bp+f0],ax / mov ax,[lastgoal] / cmp ax,[sub]      11 byte
KITA  mov bx,[lastgoal] / cmp bx,[sub] / mov [bp+f0],ax      12 byte
```

Dengan badan gelung KOSONG dan semua syarat di `&&`, simpanan ter-commit lebih
dulu dan AX bebas. Ini pelengkap aturan "WAKTU SIMPANAN = TEKANAN REGISTER":
bawaannya menunda, dan **badan yang kosong itulah yang membatalkan penundaan**.

⚠ Selisihnya cuma 1 byte, tapi ia MENGGESER seluruh sisa fungsi — di `loadcon`
1 byte ini mengunci 52 byte.

## ⭐⭐ URUTAN OPERAN `+` memilih siapa yang di-CSE

Situs kedua `loadcon`, di `expect = ... + (nzany + nmech) * 2;` dengan
`nmechb = nmech;` beberapa baris di bawahnya:

```
ASLI  mov ax,[nzany] / add ax,[nmech] / shl ax,1 / add cx,ax   ... mov ax,[nmech]
KITA  mov ax,[nmech] / mov dx,[nzany] / add dx,ax / shl dx,1 / add cx,dx
```

Kompiler memuat lebih dulu operan yang **dipakai lagi nanti** (di sini `nmech`,
untuk `nmechb = nmech`), menahannya di AX, dan terpaksa memakai DX untuk yang
lain. Tulis operan yang di-CSE itu **DULUAN di sumber** (`(nmech + nzany)`) dan
kompiler malah memuat yang lain lebih dulu lalu MEMUAT ULANG yang di-CSE —
persis bentuk asli. Empat byte, dan bentuknya cocok 100%.

## ⭐⭐ `extern char *p` BUKAN kasus khusus f278e/f2714 — ia menutup `main_` juga

Aturan "`extern char *p` ≠ `extern int p` + cor `(char *)p`" sudah tercatat dari
`f2714`/`f278e`. Ternyata ia juga yang menutup situs `main_` 0x0c83 yang selama
berminggu-minggu dianggap "kelas alokator yang tak terkendali":

```c
extern int   recbase;  ... (buf[j] * 0xc + (char *)recbase)[1]   /* mov bx,[recbase] */
extern char *recbase;  ... (buf[j] * 0xc + recbase)[1]           /* mov si,[recbase] */
```

`main_` langsung 4216/4219 → **4219/4219**. Ubah juga penugasannya jadi
`recbase = (char *)recs;`. Aman untuk DGROUP: `gendata.py` memancarkan simbol
bukan-larik sebagai `int` apa pun tipe externnya.

⚠ **PELAJARAN META:** situs itu sudah divonis "alokator" berdasar probe 5 varian
yang semuanya memberi BX. Vonis itu SALAH — kelima varian mengubah BENTUK
PERNYATAAN, tak satu pun mengubah **TIPE**. Sebelum memarkir sesuatu sebagai
"tak terkendali", periksa apakah sumbu TIPE sudah benar-benar disapu.

## ⚠ DUA KESALAHAN di satu fungsi bisa SALING MENUTUP di PANJANG

`loadcon` melaporkan `geseran 0x5120:-1, 0x5298:+0`: kesalahan register (−1) dan
kesalahan CSE (+1) saling meniadakan, sehingga panjang totalnya PAS 739 dan
kedua-duanya tak terlihat dari angka panjang. Memperbaiki SATU saja membuat
GLOBAL **turun** (687 → 682) karena geseran −1 lalu merambat sampai ekor.

Jadi: **kalau `shapediff` melaporkan >1 situs, perbaiki semuanya sebelum menilai
dengan GLOBAL.** GLOBAL yang turun sesudah satu perbaikan yang bentuknya TERBUKTI
benar adalah bingkai tercemar, bukan bantahan. `shapediff` (yang menormalkan
literal) adalah wasit yang benar dalam keadaan ini, dan TERJAJAR yang naik
(701 → 724) mengkonfirmasi arah.

## ⭐ SI vs DI untuk PENUNJUK ditentukan LIVE-RANGE, bukan selera alokator

Situs `place` 0x4fd4 (`dp` masuk DI pada kita, SI pada asli) selama ini dibaca
sebagai "alokator tak terkendali". Reproduksi mini + `sweep.py` membuktikan
sebabnya mekanis: **SI dipakai ulang untuk penunjuk berikutnya kalau pemakaian
terakhir penunjuk sebelumnya ada SEBELUM titik itu.** Geser satu pemakaian ke
atas dan DI hilang sama sekali:

```c
if (sp->id == id && sp->row == row) {
    dp->spr2 = q;               /* sp masih dipakai NANTI -> dp ke DI  */
    ...  if (t2 != sp->spr) ...
}
```
```c
if (sp->id == id && sp->row == row) {
    t2 = sp->spr;               /* pemakaian terakhir sp DI SINI      */
    dp->spr2 = q;               /* -> dp ke SI                        */
}
```

Ini juga menjelaskan `main_` 0x0c83 dan `pickvar`: yang menentukan bukan bentuk
pernyataan, melainkan sampai mana nilai sebelumnya masih dibutuhkan.

⚠ Tapi di `place` ia BELUM bisa dipakai: kedua bentuk yang membebaskan SI
merusak byte lain (lihat daftar "DICOBA & GAGAL" di `place.c`). Khususnya
mengganti `if (A && B)` dengan dua `if (...) goto next` memberi SI yang benar
dan byte cabang yang identik, tapi kompiler MEMUAT ULANG penunjuknya di antara
kedua `if` (+3 byte). Jadi `&&` dan `goto` beda BUKAN di cabangnya, melainkan di
apakah penunjuk dipertahankan di register melintasi uji kedua.

## ⭐⭐ UKUR DI PREFIKS YANG MASIH SEJAJAR untuk lolos dari bingkai tercemar

Masalah berulang: satu situs yang tersisa menggeser panjang, lalu SELURUH ekor
fungsi salah sejajar dan GLOBAL menghukum perbaikan yang BENAR. Di `loadcon` ini
sempat membuat perbaikan yang benar terbaca 687 → 682.

Jalan keluarnya sederhana dan pasti: **ukur hanya sampai SEBELUM situs yang
tersisa.** Di prefiks itu kedua draf masih sejajar dari byte 0, jadi GLOBAL-nya
bersih. Perintahnya cuma memberi ukuran yang lebih kecil:

```
python src_c/verify/aligncmp.py <nama> <addr> <ukuran-prefiks>
```

Kasus nyata `pickvar` (2026-07-31): mengganti `k * 0xc` jadi `list[idx] * 0xc`
membuat GLOBAL seluruh fungsi TURUN 1.662 → 1.632, tapi di prefiks
0x42ca..0x44fd hasilnya **528 → 562 dari 563**. Perubahannya benar; angka
turunnya artefak. Tanpa pengukuran prefiks, perbaikan ini akan ditolak.

⭐ Pasangannya: `sweep.py --cmp <addr> <ukuran>` melaporkan GLOBAL tiap varian
langsung, jadi puluhan varian berkas SUNGGUHAN bisa diadu sekali jalan. Pakai
`--cmp` dengan ukuran PREFIKS untuk mengadu varian tanpa gangguan geseran.

## ⭐⭐ `k` vs `list[idx]` walau NILAINYA SAMA: yang satu di-CSE, yang lain tidak

`pickvar` menyimpan `k = list[idx]` lalu memakai `k` di ekspresi berikutnya.
Menulis ulang `list[idx]` di ekspresi itu — bukan memakai `k` — mengubah TIGA
hal sekaligus, dan ketiganya ke arah yang benar:

1. Nilai `list[idx]` tetap di **CX** (`mov ax,cx`), bukan dimuat ulang dari slot.
2. Alamat `&list[idx]` jadi **temp** yang di-spill ke `[bp+2]` — simpanan yang
   sebenarnya MATI (tak pernah dibaca), tapi ADA di biner asli.
3. Karena `[bp]` dan `[bp+2]` jadi terpakai, penomoran temp sesudahnya bergeser
   ke `[bp+4]`/`[bp+6]` — persis seperti aslinya.

Dan karena CX tidak lagi bebas, uji `idx + 1 < n` memakai **DX** sebagai scratch
(asli), bukan CX (kita). Satu perubahan sumber, empat gejala tertutup.

⚠ Balikannya juga berlaku: `k2 = list[idx]; k = list[idx];` TIDAK menghasilkan
apa-apa (kompiler meng-CSE keduanya jadi satu muatan). Yang menentukan adalah
apakah ekspresi `list[idx]` muncul lagi di ekspresi BESAR berikutnya, bukan
berapa kali ia ditulis di pernyataan penugasan.

⚠ Menulis `list[idx + 1]` sebagai `(list + idx)[1]` untuk "memaksa" CSE-nya
justru MENGHAPUS 19 byte — kompiler lalu benar-benar berbagi alamatnya. Yang
dibutuhkan biner asli adalah temp yang di-spill lalu TIDAK dipakai.
