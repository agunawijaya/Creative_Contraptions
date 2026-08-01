"""Pemilihan varian — `nvar()` @0x4147, `pickpart()` @0x4a2c, `loadcon()` @0x5035.

Kenapa modul ini ada. Sampai sekarang port memakai `pilih=0` (varian pertama)
supaya keluarannya bisa diulang. Itu membuat port TIDAK PERNAH bisa dibandingkan
piksel-per-piksel dengan game asli, karena game mengundi variannya. Modul ini
meniru undiannya persis, jadi dari seed yang sama port memilih part yang SAMA.

⭐ SATU HAL YANG MUDAH SALAH, dan sempat salah di sini berbulan-bulan:

    `nvar()` TIDAK menyaring record lanjutan. Daftar yang diundi memuat SEMUA
    record yang jenisnya cocok dan barisnya berganti -- termasuk potongan bawah
    sebuah part (row = row_atas + 100). Yang menyaring adalah `pickpart()`,
    SESUDAH undian, dengan cara MENGUNDI ULANG.

Akibatnya besar: `Archive.variants()` (yang membuang row >= 100) memberi jumlah
yang BERBEDA dari `cnt` yang dipakai `rnd(cnt)`. Memakai `len(variants())` sebagai
batas undian akan memberi urutan acak yang salah sejak undian pertama, walaupun
part yang terpilih kebetulan sering terlihat masuk akal.

Bukti bahwa penafsiran ini benar: log 18 panggilan `rnd()` dari emulator untuk
goal 1 mode 2 terulang PERSIS -- termasuk berapa kali tiap slot harus mengundi
ulang (5x, 7x, 2x). Lihat `uji_log()` di bawah.

Syarat terima di `pickpart()`:

    tolak kalau  rec.row > 100   (potongan lanjutan)
    tolak kalau  rec.id >= 0x80  (kelompok kedua)

⚠ `> 100`, bukan `>= 100`.  Ditulis apa adanya seperti di sumbernya.
"""

RECORD_MAKS = 0x78                       # nvar: while (i < 0x78 && ok)
CNT_MAKS = 0x32                          # nvar: if (cnt >= 0x32) ok = 0
BARIS_LANJUTAN = 100                     # rec.row > 100 -> potongan bawah


def tabel(arc, jenis):
    """`loadarc()` @0x5xxx: direktori arsip DISARING lalu DIPADATKAN.

    Yang disimpan hanya record yang jenisnya dipakai kontraption ini; hasilnya
    ditulis berurutan tanpa lubang, maksimum 120 record. Jadi indeks yang
    dipakai `nvar()`/`pickpart()` adalah indeks di tabel PADAT ini, bukan di
    direktori arsip asli.

    Untuk goal yang sudah diuji hasilnya kebetulan sama dengan menyaring
    langsung dari direktori penuh, tapi itu kebetulan: begitu sebuah goal
    memakai jenis yang record-nya lewat dari batas 120, keduanya berbeda.
    """
    out = []
    for r in arc.recs:
        if any(arc.cocok(r, t) for t in jenis):
            out.append(r)
            if len(out) >= RECORD_MAKS:
                break
    return out


def nvar(recs, want):
    """Daftar INDEKS RECORD yang diundi untuk jenis `want` (nvar.c).

    Berhenti lebih awal begitu ketemu record yang jenisnya melewati `want` atau
    id-nya nol -- direktori arsip terurut menaik, jadi tak ada gunanya lanjut.
    Record yang `row`-nya sama dengan record sebelumnya dilewati: itu potongan
    dari part yang sama, bukan varian baru.
    """
    out = []
    last = None
    for i, r in enumerate(recs[:RECORD_MAKS]):
        v = r["id"] & 0x7F
        if v == want:
            if r["row"] != last:
                out.append(i)
                last = r["row"]
                if len(out) >= CNT_MAKS:
                    break
        elif v > want or v == 0:
            break
    return out


def boleh(rec):
    """Syarat terima di gelung do-while `pickpart()`."""
    return not (rec["row"] > BARIS_LANJUTAN or rec["id"] >= 0x80)


def pickpart(rng, recs, jenis, sub=None):
    """Undi satu varian per slot. -> daftar indeks record, sepanjang `jenis`.

    `jenis` = urutan jenis part per slot, seperti di CONTRAP.
    `sub`   = nomor goal. Diperlukan karena SLOT TERAKHIR tidak diundi:

        if (sub >= 1 && sub <= 6 && i == n - 1) {
            j = 0;
            while (j < cnt && (b + tr[j] * 0xc)[1] != sub) j = j + 1;
        }

    ⭐ Undiannya TETAP dijalankan lebih dulu, lalu hasilnya DIBUANG. Itu penting
    untuk kesetiaan: undian yang dibuang tetap memajukan seed, jadi menghapusnya
    ("optimasi" yang kelihatan aman) akan merusak SELURUH pilihan sesudahnya.

    Isinya masuk akal: objek zany terakhir adalah HASIL kontraptionnya, jadi ia
    harus sesuai goal yang diminta -- varian dipilih lewat `row == nomor goal`,
    bukan diacak. Goal 1 ("bangunkan orang tidur") selalu mendapat varian row 1.

    Cabang `lvl2 == 2 && mark[i]` (batas 150 undian lalu jatuh ke cabang umum)
    belum diperlukan: mode yang sudah diuji tidak pernah memasukinya.
    """
    hasil = []
    n = len(jenis)
    for i, t in enumerate(jenis):
        tr = nvar(recs, t)
        if not tr:
            hasil.append(None)
            continue
        if not any(boleh(recs[ix]) for ix in tr):
            # Tak ada yang bisa diterima -> gelungnya takkan berhenti di game
            # asli. Belum pernah terjadi pada data nyata; jangan diam-diam
            # dibulatkan ke varian pertama.
            raise ValueError("jenis %d: tidak ada varian yang memenuhi" % t)
        while True:
            j = rng.rnd(len(tr))
            if boleh(recs[tr[j]]):
                break
        if sub is not None and 1 <= sub <= 6 and i == n - 1:
            j = 0
            while j < len(tr) and recs[tr[j]]["row"] != sub:
                j += 1
            if j >= len(tr):            # sumbernya membiarkan j == cnt di sini
                j = len(tr) - 1         # -> baca lewat ujung; jangan ditiru
        hasil.append(tr[j])
    return hasil


def mkpal(recs):
    """`mkpal()` @0x3909: daftar "palet" mekanisme = record yang MENGAWALI
    kelompok baru, yaitu saat (id, row) berbeda dari record sebelumnya.

        c1 = (base[i].id  != base[i-1].id);
        c2 = (base[i].row != base[i-1].row);
        ok = (i == 0 || c1 || c2);

    Dibatasi 35 record (0x23) seperti sumbernya.
    """
    out = []
    for i, r in enumerate(recs[:0x23]):
        if i == 0 or r["id"] != recs[i - 1]["id"] or r["row"] != recs[i - 1]["row"]:
            out.append(i)
    return out


def fillans(recs, jenis):
    """`fillans()` @0x4b??: mekanisme TIDAK diundi. -> indeks record per slot.

        for (j = 0; j < nmech; j++)
            if (b[tr[j] * 0xc] == tt[i]) { ans[i] = tr[j]; break; }

    Yang dibandingkan adalah BYTE ID record, sama persis dengan jenis slot.
    Sengaja BUKAN `nvar()`: nvar memakai `id & 0x7f`, dan untuk mekanisme
    ber-id >= 128 masker itu merusak nilainya (150 & 0x7f = 22), sehingga
    jenis 150 tidak akan pernah ketemu. Salah satu tempat di mana memakai
    ulang "fungsi yang mirip" akan diam-diam meleset.
    """
    tr = mkpal(recs)
    hasil = []
    for t in jenis:
        ketemu = None
        for j in tr:
            if recs[j]["id"] == t:
                ketemu = j
                break
        hasil.append(ketemu)
    return hasil


ZANY_AMBANG = 0x8C               # id >= 140 dianggap SEKELOMPOK saat dedup


def palet_mekanisme(recs, jenis, lvl3, rng=None, shufflg=1):
    """`mkpal()` @0x3909 seutuhnya. -> daftar INDEKS record yang ditawarkan.

    ⭐ Inilah yang menentukan BERAPA BANYAK pilihan yang muncul di strip, dan
    jawabannya tergantung MODE:

        if (lvl3 != 1 || base[i*0xc] == tab[j*3+2]) { ...masuk palet }

    `lvl3 == 1` di mode 1/2/3 -> hanya part yang memang DIBUTUHKAN kontraption
    ini yang ditawarkan; soalnya jadi "taruh di kotak yang benar".
    `lvl3 == 3` di mode 4 -> syaratnya gugur, SELURUH daftar ditawarkan.

    Lalu, kalau `shufflg == 1`, daftarnya dikocok dan di-DEDUP: dua entri
    dianggap sama kalau id-nya sama, ATAU kalau KEDUANYA >= 0x8c. Entri yang
    dibuang ditimpa entri terakhir dan cacahnya menyusut. `want` -- id >= 0x8c
    yang memang diminta kontraption ini -- dilindungi: kalau ia yang hendak
    dibuang, ia dipindahkan dulu ke posisi yang dipertahankan.

    TERUKUR vs `nmech` @0x3ac di emulator:
        Fill in Mechanisms  goal 1 -> 3, goal 2 -> 4, goal 4 -> 3
        Contraption Mix Up  goal 1 -> 13
    dan 13 itu memang jumlah id record berbeda di MECHS (15) sesudah tiga id
    >= 0x8c (140, 141, 150) diciutkan jadi satu.

    ⚠ `recs` HARUS tabel `base` milik mode itu, bukan selalu direktori arsip.
    `main_.c` memanggil `loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`:

        lvl3 == 1 -> base = tabel DISARING + DIPADATKAN, yaitu `tabel()`
        lvl3 != 1 -> base = direktori PENUH

    Terukur dgn `CC_VSPTR=73a:...`: goal 1 mode isian `base` berisi 6 record,
    mode Mix Up 30 record. Memberi direktori penuh untuk mode isian tetap
    memberi CACAH yang benar tapi RECORD yang salah -- indeks `idtab[]` gim
    menunjuk ke `base`, jadi thumbnail-nya meleset.

    `rng` boleh None: tanpa kocokan urutannya tetap urutan arsip. Kocokannya
    memakai RNG gim, jadi berikan objek Rng yang sama dengan pemilihan part.
    """
    want = 0
    for t in jenis:
        if t >= ZANY_AMBANG:
            want = t
            break
    grup = []
    for i, r in enumerate(recs[:0x23]):
        if i == 0 or r["id"] != recs[i - 1]["id"] or r["row"] != recs[i - 1]["row"]:
            if lvl3 != 1 or any(r["id"] == t for t in jenis):
                grup.append(i)
        if i + 1 >= len(recs) or recs[i + 1]["id"] == 0:
            break
    if not (shufflg == 1 and rng is not None):
        return grup
    for i in range(len(grup)):
        r = rng.rnd(len(grup))
        grup[r], grup[i] = grup[i], grup[r]
    i = 0
    while i < len(grup):
        id1 = recs[grup[i]]["id"]
        j2 = i + 1
        while j2 < len(grup):
            id2 = recs[grup[j2]]["id"]
            if id1 == id2 or (id1 >= ZANY_AMBANG and id2 >= ZANY_AMBANG):
                if want != 0 and id2 == want:
                    grup[i] = grup[j2]
                grup[j2] = grup[-1]
                grup.pop()
                continue                 # `j2--` lalu `j2++` = periksa ulang slot ini
            j2 += 1
        i += 1
    return grup


def loadcon_pick(rng, jumlah_varian, lastgoal=None, sub=None, lastvar=None):
    """loadcon(): undi varian STRUKTUR, hindari mengulang varian sebelumnya.

        do { pick = rnd(cnt) } while (lastgoal == sub && cnt >= 2 && pick == lastvar)

    `pick` di sumber aslinya indeks ABSOLUT di direktori (`+ first`); di sini
    dikembalikan relatif terhadap goal-nya, karena `parse()` sudah mengelompokkan.
    """
    while True:
        pick = rng.rnd(jumlah_varian)
        if not (lastgoal == sub and sub is not None
                and jumlah_varian >= 2 and pick == lastvar):
            return pick


# --------------------------------------------------------------------------
def uji_log(path_log, recs, jenis, jumlah_varian, sub=None):
    """Cocokkan simulasi dengan log rnd() emulator. -> (cocok, total, catatan).

    Log satu baris per panggilan: `<seed sebelum hex> <n> <hasil>`.
    Yang dibandingkan BUKAN cuma part yang terpilih, tapi SETIAP undian --
    termasuk yang ditolak. Kalau jumlah undiannya sama, penolakannya juga sama.
    """
    from .rng import Rng
    baris = [l.split() for l in open(path_log).read().split("\n") if l.strip()]
    diharap = [(int(a, 16), int(b), int(c)) for a, b, c in baris]
    rng = Rng(0)
    urut = []

    def rnd(n):
        s = rng.seed
        v = rng.rnd(n)
        urut.append((s, n, v))
        return v

    tiruan = type("T", (), {"rnd": staticmethod(rnd), "seed": 0})()
    loadcon_pick(tiruan, jumlah_varian)
    hasil = pickpart(tiruan, recs, jenis, sub)
    cocok = sum(1 for a, b in zip(urut, diharap) if a == b)
    return cocok, max(len(urut), len(diharap)), hasil
