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

13. **SWITCH JARANG: tabel nilai/label disusun KEBALIKAN urutan sumber.**
    Pemindainya mulai dari entri TERAKHIR dan menghitung mundur
    (`mov si,18h` / `cmp ax,cs:[si+tab]` / `sub si,4` / `jns`).
    Jadi **urutan `case` di sumber = urutan ALAMAT badan case-nya**, sedangkan
    tabelnya dibaca mundur. Tanpa aturan ini urutan case pasti tertukar.

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

## ⚠ `gendata.py` membuang alamat DGROUP 0..3

Penyaringnya `START <= a` dengan `START = 4`, padahal `a` itu alamat **DGROUP**
sedangkan `START` offset **DATA**. Simbol di DGROUP:0000..0003 karena itu tidak
pernah terbit dan LINK melaporkan unresolved. Ini memblokir satu instruksi di
`main` (0x00B9 `mov bx,[0]`, biaya 7 byte). **Belum diperbaiki** — menyentuh
penataan DGROUP yang sekarang 100% cocok (9.556/9.556), jadi butuh keputusan.

## ⚠ `link.ps1` menautkan SEMUA `.OBJ` di `out/`, bukan hanya yang di manifest

Begitu sebuah `.c` baru ditaruh di `src/`, `buildall.ps1` mengompilnya dan
`link.ps1` otomatis ikut menautkannya. Kalau fungsi itu masih punya stub di
`stubs.c`, keduanya bentrok. Cabut stubnya di saat yang sama.

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
