"""Bilah status, skor, timer, petunjuk, dan pesan akhir goal.

Padanan lima fungsi gim asli yang selama ini tidak ada di port:

    showsc()    @0x5D80   tampilkan skor di pita atas (+ kedip opsional)
    timedrw()   @0x59xx   bilah timer mode Mix Up
    timebar()             pendampingnya: satu tik, hapus satu piksel
    showhint()  @0x5A2x   spanduk "GAME OVER"
    prompts()   @0x5Bxx   pesan akhir goal
    pickmax()   @0x5Axx   undian nilai tertinggi untuk petunjuk Master

⭐ SKOR DISIMPAN DIBAGI SEPULUH. Format cetaknya `" %7ld0"` — sebuah `long`
rata-kanan tujuh karakter, lalu angka **nol harfiah** ditempel. Jadi `sclo`
bertambah 10000 tetapi yang terbaca pemain "100000". Menyimpan nilai tampilan
apa adanya akan membuat skor sepuluh kali lipat.

⭐ SKOR HANYA DIHITUNG DI MODE 4 (Contraption Mix Up). Di `animvm.c` case 0x10
barisnya `if (mode != 4) break;` — Fill in Mechanisms dan Fill in Zany Objects
memang latihan tanpa skor. Port lama memberi skor di semua mode.

Penomoran mode, dari `switch` hasil `mainmenu()` di `main_.c`:

    0  layar judul / attract      3  Fill in Zany Objects
    1  Review Mechanisms          4  Contraption Mix Up
    2  Fill in Mechanisms

⚠ `text()` memakai urutan (X, Y) — kebalikan `blit()` yang (Y, X). Semua
koordinat di modul ini ditulis mengikuti urutan `text()`, apa adanya seperti
di sumbernya.

Semua fungsi menggambar lewat sebuah **kanvas** (`render.KanvasFB` untuk
framebuffer indeks, `render.KanvasSurface` untuk menggambar langsung ke layar).
Aturan penempatan dan percabangannya ditulis SEKALI; yang berganti cuma
sasarannya.
"""
from . import render as rend

# --- alamat string di DGROUP, dibaca lewat dgtab -------------------------
S_GREAT = 0xA37          # "GREAT!"
S_LAGI = 0xA3E           # "Press SPACE BAR to play again."
S_COBA = 0xA5D           # "Press SPACE BAR to try again."
S_TERUS4 = 0xA7B         # "Press SPACE BAR to go on."
S_TERUS0 = 0xA95         # "Press ENTER to go on."
S_PILIH1 = 0xAAB         # "Press ENTER to select"
S_PILIH2 = 0xAC1         # "another mechanism."
S_BANGUN1 = 0xAD4        # "Press ENTER to build"
S_BANGUN2 = 0xAE9        # "another contraption."
S_ULANG = 0xAFE          # "Press SPACE BAR to see it work again."
S_HINT = 0xA26           # "GAME OVER"
# Pesan "salah taruh". Keluar lewat `printf()` di `animvm.c`, jadi ia teks DOS
# -- BUKAN digambar `text()`. Spasi depannya bagian dari string dan itulah yang
# menempatkannya: tujuh spasi untuk mekanisme, enam untuk objek zany.
S_SALAH_MEK = 0x9DD      # "       Mechanism %c does not work." + LF
S_SALAH_ZANY = 0xA01     # "      Zany object %c does not work." + LF


def pesan_salah(zany, huruf):
    """Teks gim untuk part yang salah taruh. -> string siap gambar.

    ⚠ Port dulu mengarang "Part A does not work." dan "Box A isn't right
    yet - fix it.". Yang benar ada di DGROUP, LENGKAP dgn spasi depannya --
    tujuh spasi untuk mekanisme, enam untuk objek zany. Spasi itu bukan hiasan:
    pesannya keluar lewat `printf()` (teks DOS di posisi kursor), jadi spasi
    depan itulah yang menempatkannya.
    """
    t = _str(S_SALAH_ZANY if zany else S_SALAH_MEK)
    return t.replace("%c", chr(huruf)).rstrip()

HINT_REC = 19            # load(miscfh, level_, 0x13, hintspr) -> MISC record 19
TBL_NAMA = 0x922         # tabel nama goal, diindeks `sub` (1..6)
TBL_MEK = 0x8CA          # tabel nama mekanisme; indeks 0 = " " (kosong)


def _str(addr):
    from . import dgtab
    dg = dgtab.dgroup()
    akhir = dg.find(b"\0", addr)
    return dg[addr:akhir if akhir >= 0 else addr].decode("latin-1")


def nama_goal(sub):
    """Nama goal dari tabel DGROUP @0x922, diindeks `sub`.

    Bukan daftar yang ditulis tangan di port: string ini memang ada di segmen
    data gim. tab[0] adalah " " (spasi), jadi indeks 0 sengaja tidak
    menggambar apa pun.
    """
    from . import dgtab
    if not (0 <= sub < 7):
        return ""
    return _str(dgtab.word(TBL_NAMA + 2 * sub))


def judul_atau_skor(k, mode, sub, skor=0, rev=None):
    """`f171f()` — pojok kanan pita atas.

        if (mode == 4) showsc(sclo, schi, 0);
        else { t = tab[idx]; text(t, 0xc8, 0, 1, 1, 2); }

    ⭐ Satu tempat, isi berganti menurut layarnya. Yang menentukan bukan cuma
    `mode` melainkan TABEL dan INDEKS yang dioper pemanggilnya:

        layar judul   f171f(2, 0x8ca, 0, ...)        -> tab[0] = " ", kosong
        Review        f171f(mode, 0x8ca, cur+1, ...) -> nama MEKANISME
        Fill/Zany     f171f(2, 0x922, sub, ...)      -> nama GOAL
        Mix Up        mode == 4                       -> SKOR

    ⚠ Memukul rata "selain mode 4 tampilkan nama goal" langsung meleset 1.102
    piksel di layar judul: di situ indeksnya 0, yang isinya spasi.
    """
    if mode == 4:
        return showsc(k, skor, 0)
    if mode == 0:
        return False                     # tab[0] = " ": tidak menggambar apa pun
    if mode == 1:
        from . import dgtab
        if rev is None:
            return False
        nm = _str(dgtab.word(TBL_MEK + 2 * (rev + 1)))
    else:
        nm = nama_goal(sub)
    if nm.strip():
        k.teks(nm, 0xC8, 0, 2)
    return False


def skor_teks(nilai):
    """`sprintf(buf, " %7ld0", lo, hi)` -> teks skor siap gambar.

    ⭐ Skornya satu `long` 32-bit di @0x730. Rekonstruksi C memecahnya jadi dua
    `int` (`sclo` @0x730, `schi` @0x732) supaya tata letak datanya cocok, tapi
    PEMAKAIANNYA membuktikan ia satu nilai: `showsc(sclo, 2)` hanya memberi DUA
    argumen ke fungsi bertiga parameter -- karena `sclo` sebuah long yang
    memakan dua slot, dan `2` itu argumen `flash`.

    Nol harfiah di ujung format membuat skor tersimpan sepersepuluh dari yang
    dibaca pemain: `sclo += 10000` tampil sebagai "100000".
    """
    return " %7d0" % nilai


def showsc(k, nilai, flash=0):
    """Gambar skor di pita atas. -> True kalau pemanggil harus mengedipkannya.

        fillrect(0xd0, 0, 0x110, 7, 3);
        text(buf, 0xd0, 0, 1, 1, 2);

    Kedipnya (`flash >= 2`) di gim asli: XOR seluruh pita atas, bunyikan nada,
    tunggu 20 tik, XOR lagi. Karena butuh waktu, pemanggil yang menjalankannya
    lewat `kedip_pita()` -- itu sebabnya fungsi ini MENGEMBALIKAN apakah kedip
    diminta, bukan mengerjakannya sendiri.
    """
    k.fillrect(0xD0, 0, 0x110, 7, 3)
    k.teks(skor_teks(nilai), 0xD0, 0, 2)
    return flash >= 2


def kedip_pita(k, warna=1):
    """`line(0, 0, 0x13f, 7, 1)` — XOR sepanjang pita atas.

    `line()` di assembly meng-XOR byte VRAM dengan pola warnanya, jadi per
    piksel efeknya `nilai ^= warna`. Dipanggil DUA kali dengan argumen sama:
    sekali menyalakan kedip, sekali mengembalikannya.
    """
    k.xor(0, 0, 0x13F, 7, warna)


def timedrw(k, tx, mode, nbola=1, sub=1):
    """Bilah timer mode Mix Up. -> True kalau ini pengisian AWAL (bilah penuh).

        if (mode != 4) return;
        if (tx < 0x140 && (goal != 6 || sub != 1)) {
            if (tx >= 0) {
                fillrect(0, 0xa2, tx, 0xa5, 2);
                fillrect(tx, 0xa2, 0x13f, 0xa5, 0);
            }
        } else { ...bunyi + isi bilah sepotong demi sepotong... }

    ⭐ `tx` adalah waktu TERSISA dalam piksel, bukan waktu terpakai. `main_.c`
    menyetelnya `tx = 0x140` saat Mix Up dimulai (bilah PENUH) dan `timebar()`
    menguranginya satu tiap tik sambil menghapus dari `tx` ke kanan -- bilahnya
    menyusut. Karena itu bonus Master `sclo += tx * 100` memang menghargai sisa
    waktu, bukan waktu yang habis terpakai.

    ⚠ Cabang kedua BUKAN "waktu habis". Ia dimasuki saat `tx == 0x140`, yaitu
    di AWAL: bilahnya diisi delapan piksel sekali sambil membunyikan nada --
    animasi pembuka, bukan penutup.
    """
    if mode != 4:
        return False
    if tx < 0x140 and (nbola != 6 or sub != 1):
        if tx >= 0:
            k.fillrect(0, 0xA2, tx, 0xA5, 2)
            k.fillrect(tx, 0xA2, 0x13F, 0xA5, 0)
        return False
    # Pengisian awal: gim asli mengisi bilah 8 piksel sekali sambil membunyikan
    # nada. Di sini langsung penuh; bunyinya belum ada di port.
    k.fillrect(0, 0xA2, 0x13F, 0xA5, 2)
    return True


def timebar(k, tx, mode):
    """`timebar()` — satu tik timer. -> `tx` baru.

        if (mode != 4) return;
        tx = tx - 1;
        if (tx < 0x140 && tx >= 0) { fillrect(tx, 0xa2, 0x13f, 0xa5, 0); }

    Pendamping `timedrw()`: yang satu menggambar seluruh bilah, yang ini hanya
    menghapus satu piksel di ujung kanan tiap tik -- jauh lebih murah.
    """
    if mode != 4:
        return tx
    tx -= 1
    if 0 <= tx < 0x140:
        k.fillrect(tx, 0xA2, 0x13F, 0xA5, 0)
    return tx


def showhint(k, misc, mode=4):
    """Spanduk "GAME OVER".

        if (mode == 4) {
            hintshown = 1;
            blit(hintspr, 0, 0x6c, 8, 0x68);
            text(hintstr, 0x7c, 0, 1, 1, 3);
        }

    `hintspr` @0x646 adalah BUFFER kosong di DGROUP, diisi saat program mulai
    oleh `load(miscfh, level_, 0x13, 0x646)` -- yaitu MISC record 19 (104x7).
    Sama polanya dengan `hdrspr` yang diisi MISC record 2.
    """
    if mode != 4:
        return False
    k.blit(misc, misc.recs[HINT_REC], 0x6C, 0)
    k.teks(_str(S_HINT), 0x7C, 0, 3)
    return True


def prompts(k, mode, sub, gagal, lvl, nbola):
    """Pesan akhir goal. -> nbola yang mungkin sudah diubah (lihat `goal = 0`).

    Ditulis mengikuti cabang aslinya persis, termasuk urutan `else if`.
    """
    if mode not in (0, 1):
        baris = 0x15 if mode == 4 else 0x14
        if gagal == 0:
            k.teks(_str(S_GREAT), 0x80, baris * 8 + 2, 3)

    tuntas = (sub == 6 and gagal == 0)
    if mode == 4 and (tuntas or (lvl == 2 and nbola <= 1)):
        nbola = 0
        k.teks(_str(S_LAGI), 0x20, 0xC0, 2)
    elif gagal != 0:
        k.teks(_str(S_COBA), 0x28, 0xC0, 2)
    else:
        if mode == 4:
            k.teks(_str(S_TERUS4), 0x38, 0xC0, 2)
        elif mode == 0:
            k.teks(_str(S_TERUS0), 0x48, 0xC0, 2)
        else:
            if mode == 1:
                k.teks(_str(S_PILIH1), 0x40, 0xAC, 2)
                k.teks(_str(S_PILIH2), 0x40, 0xB6, 2)
            else:
                k.teks(_str(S_BANGUN1), 0x40, 0xAC, 2)
                k.teks(_str(S_BANGUN2), 0x40, 0xB6, 2)
            k.teks(_str(S_ULANG), 0x10, 0xC0, 2)
    return nbola


def pickmax(rng, count, jangkauan):
    """Undian nilai tertinggi untuk petunjuk Master. -> (best, count baru).

        best = -1000;
        count = count - 1;
        for (i = 0; i < count; i++) { r = rnd(range); if (r > best) best = r; }

    Perhatikan `count` dikurangi SEBELUM gelung, jadi undian berkurang satu
    tiap kali dipanggil -- petunjuknya makin sempit seiring permainan.
    """
    best = -1000
    count = count - 1
    for _ in range(max(0, count)):
        r = rng.rnd(jangkauan)
        if r > best:
            best = r
    return best, count


class Petunjuk:
    """Keadaan penanda petunjuk Master — `hintmark()` @0x4CD4.

    Hanya hidup di mode 4 (Contraption Mix Up) level 2 (Master Builder). Tiap
    kali pewaktu habis, penanda huruf pindah ke slot acak baru: huruf LAMA
    dihapus dengan menggambarnya ulang berwarna 3 (warna latar pita), huruf
    BARU digambar berwarna 2 atau 0.

    Warna 0 berarti "ini benar-benar petunjuk" dan menyalakan `mflag`, yang
    dipakai `animvm.c` case 0x10 sebagai syarat bonus bola. Warna 2 hanya
    penanda biasa.

    Nilainya dikumpulkan di satu objek karena di gim aslinya ini SEMUA global
    yang saling terkait (`best`/`count`/`range` juga dipakai `pickmax()`);
    memisahkannya jadi argumen lepas membuat urutan pemanggilannya mudah
    salah.

        best  @0x82e   count @0x82c   range @0x830   mflag @0x834
        cur2  @0x7f8   lvl6  @0x7f6   timer @0x7f2   tx    @0x7ee
    """

    def __init__(self, rng, nmax, count=4):
        self.rng = rng
        self.nmax = nmax
        self.range_ = 0x140
        self.count = count
        self.best = -1000
        self.cur2 = 0
        self.lvl6 = 0
        self.timer = 0
        self.mflag = 0
        self.warna = 2
        self.pickmax()               # dipanggil sekali saat mode 4 dimasuki

    def mulai_ronde(self, nmax, tx=0x140, tinit=True):
        """Pembuka `runplay()` @0x5505 -- keadaan penanda tiap kontraption:

            timer = -1;
            lvl6  = nmax;
            if (tinit == 1) { range = tx - (rnd(200) * 0x17 / 199 + 2); tinit = 0; }
            else              range = 0x140;
            if (best > range) best = tx - range;

        ⚠ DUA nilai awal ini dulu SALAH di port: `lvl6` dimulai 0 (seharusnya
        `nmax`) dan `range` dipatok `0x140 - 0x14`. Terukur dari DGROUP pada
        panggilan `hintmark()` pertama: lvl6 = 10 = nmax, dan range = 314 --
        bukan 300. `range` memang DIACAK tiap kontraption pertama.

        `lvl6` penting karena `cur2 = lvl6 + rnd(3) + rnd(3) - 2`: ia PUSAT
        sebaran penanda. Dimulai dari 0, penandanya akan selalu terdorong ke
        slot pertama alih-alih ke slot terakhir.
        """
        self.nmax = nmax
        self.timer = -1
        self.lvl6 = nmax
        if tinit:
            self.range_ = tx - (self.rng.rnd(200) * 0x17 // 199 + 2)
        else:
            self.range_ = 0x140
        if self.best > self.range_:
            self.best = tx - self.range_
        return self.range_

    def pickmax(self):
        self.best, self.count = pickmax(self.rng, self.count, self.range_)
        return self.best

    def tik(self, mode, lvl, tx, postab, k=None):
        """Satu panggilan `hintmark()`. -> True kalau penandanya dipindah.

        `postab` = daftar (a, b) posisi label huruf, satu per slot. Di gim itu
        `postab[]` @0x3b6 dgn stride 4 byte, diisi `loadcon()`; di port ia
        `countA` hasil `contrap.parse()`.

        `k` boleh None. Gim aslinya menggambar penanda SEKALI saat ia pindah
        (dan menghapus yang lama dengan menimpanya warna 3); penggambar port
        menyusun ulang seluruh layar tiap frame, jadi di sana penandanya
        digambar dari `cur2`/`warna` dan pemanggil cukup memakai nilai itu.
        Perhitungan undiannya tetap SAMA -- itu yang menentukan slot mana yang
        ditunjuk dan kapan `mflag` menyala.
        """
        if mode != 4 or lvl != 2:
            return False
        if not (self.timer <= 0 or tx == self.best):
            self.timer -= 1
            return False
        prev = self.cur2
        self.timer = 0x3C
        if self.lvl6 > 0:
            self.lvl6 -= 1
        # DUA undian rnd(3) dijumlahkan lalu dikurangi 2: sebarannya segitiga,
        # jadi penandanya cenderung dekat `lvl6` -- bukan seragam.
        self.cur2 = self.lvl6 + self.rng.rnd(3) + self.rng.rnd(3) - 2
        if self.cur2 < 0 or self.cur2 >= self.nmax:
            self.cur2 = self.lvl6
        if k is not None and prev <= self.nmax and prev < len(postab):
            oa, ob = postab[prev]
            k.teks(chr(prev + 0x41), ob, oa, 3)     # hapus: gambar ulang warna 3
        col = 2
        if tx >= self.range_:
            col = 0
        if tx == self.best:
            col = 0
            self.pickmax()
        if k is not None and self.cur2 < len(postab):
            na, nb = postab[self.cur2]
            k.teks(chr(self.cur2 + 0x41), nb, na, col)
        self.warna = col
        self.mflag = 1 if col == 0 else 0
        return True


def skor_akhir(sclo, zcnt, mode, lvl, sub, cur2, tx, nbola):
    """Penilaian akhir goal, `animvm.c` case 0x10. -> (sclo, nbola, tampilkan)

        if (mode != 4) break;                    <- HANYA Mix Up yang berskor
        switch (zcnt) { 0: +10000; 1: +5000; default: +2500; }
        if (lvl == 2) sclo += cur2 * 1000;
        if (sub == 6) {
            sclo += (goal - 1) * 2500;  goal = 1;
            if (lvl == 2) { sclo += tx * 100; tx = 0; }
        }

    ⚠ SATU penilaian per kontraption, dari `zcnt` (penghitung kesalahan untuk
    kontraption itu) -- BUKAN satu penilaian per kotak. Port lama memberi
    10000/5000/2500 ke TIAP kotak menurut percobaan kotak itu sendiri, yang
    membuat skornya bisa berlipat-lipat dari yang mungkin di gim asli.
    """
    if mode != 4:
        return sclo, nbola, False
    sclo += 10000 if zcnt == 0 else (5000 if zcnt == 1 else 2500)
    if lvl == 2:
        sclo += cur2 * 1000
    if sub == 6:
        sclo += (nbola - 1) * 2500
        nbola = 1
        if lvl == 2:
            sclo += tx * 100
    return sclo, nbola, True
