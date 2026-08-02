"""Satu adegan utuh: layar diam + animasinya, dibangkitkan dari berkas aset.

Ini yang menggantikan `port/cc/anim/*.dat` (83 berkas rekaman frame) dan
`port/cc/draws/*.json`. Keduanya hasil MENJALANKAN game di emulator; sekarang
keduanya cuma boleh dipakai sebagai PEMBANDING.

⭐ URUTAN GAMBARNYA yang harus benar, dan ini sempat salah:

    VRAM saat MASUK drawball N  =  hasil drawball N-1  +  blit part sesudahnya

Jadi part yang di-blit SESUDAH bola akan MENUTUPI bola. Modelnya BUKAN
"latar + bola di atas". `drawball N` sendiri menghapus bola N-1 (mengembalikan
latar di kotaknya) lalu menggambar bola N.

⚠ Sempat dicatat bahwa bola tertinggal dua peristiwa dan part satu, dengan
halaman ganda sebagai sebabnya. Itu keliru: pergeseran itu hanya kebetulan
mengompensasi urutan gambar yang salah. Begitu urutannya dibetulkan, TANPA
pergeseran apa pun hasilnya naik dari 101/135 jadi 119/135 frame identik.
Angka yang membaik bukan bukti bahwa penjelasannya benar.

⭐ HASIL SEKARANG: terhadap tangkapan VRAM emulator, tujuh layar (goal 1..6 +
judul 128), animasi PENUH dari frame pertama sampai habis =
**1.210/1.210 frame byte-identik, 77.440.000/77.440.000 piksel
(100,000000%)**. Uji: `python work/test_anim_vs_gim.py`.

Catatan di bawah ditulis saat angkanya masih 381/402 lalu 396/402; sengaja
DISIMPAN karena isinya jalan buntu yang sebabnya sudah dipahami -- membacanya
lebih murah daripada mengulanginya.

── 21 frame yang BELUM cocok, dan satu hipotesis yang sudah DIUJI dan GAGAL ──

Sisa bedanya kecil dan terpusat. Contoh terjelas, goal 1 frame 121: di situ
part 5 mem-blit GRAPH 40, dan baris 32, 33, 36, 37, 38, 39 sprite itu cocok
PERSIS dengan rujukan -- hanya baris 34 dan 35 yang berbeda, dan di situ
rujukan justru punya LEBIH SEDIKIT piksel part. Bentuknya seperti lubang
berwarna latar yang ditinju ke dalam part yang baru digambar, tepat di kotak
tempat bola tadi berada.

Hipotesis yang tampak pas: `prep()` menyalin latar di bawah bola SEBELUM bola
digambar, jadi penghapusan berikutnya mengembalikan salinan yang sudah BASI
dan menimpa balik part yang di-blit sesudahnya.

Sudah dicoba. Hasilnya JAUH lebih buruk: 381/402 -> 57/402 frame identik.
Jadi di hampir semua frame gim aslinya justru memakai latar TERKINI, dan
"salinan basi" bukan aturan umum. Entah salinannya diperbarui di suatu tempat,
entah lubangnya lahir dari `blend()`/`putmsk()` yang menggabungkan mask lama
dan baru dengan cara yang belum kita turunkan.

Percobaan KEDUA, kali ini diturunkan langsung dari assembly-nya, bukan dikira:

    prep.asm    menyalin 8 baris x 3 byte dari VRAM ke penyangga halaman
                -- ia memang MENYIMPAN latar di bawah bola;
    xform()     urutannya prep(posisi BARU) -> blend -> putmsk(posisi LAMA)
                -> draw, jadi penyimpanan terjadi SEBELUM penghapusan;
    blend.c     menandai sel yang beririsan antara kotak lama dan baru
                supaya putmsk tidak memulihkannya dua kali.

Diterapkan persis dengan urutan itu: 23/402 frame identik. Lebih buruk lagi.

Jadi DUA implementasi model "salinan tersimpan", dengan urutan yang berbeda
dan salah satunya diturunkan dari assembly, sama-sama jauh di bawah model
sederhana "pulihkan dari latar terkini" (381/402). Kesimpulan yang paling
sesuai bukti: `page`/`page2` bukan salinan latar yang dikembalikan mentah --
`putmsk`/`draw` menyusun bola lewat MASK terhadap isi layar yang hidup,
sehingga efeknya setara memulihkan latar terkini. Yang belum diturunkan
adalah kedua rutin itu (`blitmsk.asm`), bukan `prep` atau `blend`.

`blitmsk.asm` akhirnya dibaca, dan semantiknya jelas:

    putmsk(dmask, page2)  di kotak LAMA: tulis byte `page2` HANYA di sel yang
                          byte mask-nya nol; lewati seluruhnya kalau
                          prevx == 0x140 ("jangan hapus").
    draw(page, sy, sx)    di kotak BARU: VRAM = (page AND mask) OR sprite.

⭐ `draw` TIDAK MEMBACA VRAM. Basisnya `page`, salinan yang baru saja diambil
`prep` -- dan `prep` mengambilnya SEBELUM bola lama dihapus. Kalau kedua kotak
beririsan, salinan itu masih memuat piksel bola lama.
Gelung pertama `blend()` hanya menol-kan kedua mask (`*p++ = *q++ = 0`), jadi
`page2` memang salinan basi, bukan disegarkan.

Model itu diterapkan PERSIS, dan hasilnya tetap 23/402 -- sama dengan
percobaan sebelumnya, jauh di bawah 381/402. Karena semantiknya kini terbaca
langsung dari assembly, yang tersisa sebagai tersangka bukan lagi rumusnya
melainkan URUTAN PANGGILANNYA: `drawball` juga dipanggil di luar VM (mis.
`setball()` untuk ikon di pita atas), dan tiap panggilan MEMUTAR page/page2.
Kalau rotasinya bergeser satu, `page2` menunjuk salinan yang salah --
sedangkan model sederhana kebal terhadap itu karena selalu memakai latar
terkini.

── Apa yang AKHIRNYA diukur, bukan lagi diterka ─────────────────────────

Keadaan bola gim direkam langsung dari DGROUP tiap panggilan `drawball`
(`CC_VSWORD` di work/emu.py), lalu diadu dengan VM ini:

    posisi bola   136/136 cocok
    bendera hapus 135/136 cocok  (satu-satunya beda di frame 1, yaitu
                  keadaan AWAL `prevx = 0x140` dari setupscr, bukan opcode)

Jadi VM-nya eksak. Sisa 21 frame sepenuhnya soal ISI yang dipulihkan saat
menghapus, bukan soal ke mana bola pergi atau kapan penghapusan dilewati.

Isi penyangga `page2` juga dibuang dari emulator (`CC_VSPTR=2e2:24`) dan
dibandingkan dengan `latar` di sini: pada frame 10 keduanya IDENTIK
(`555555` delapan baris). Jadi bedanya bukan pada isi latarnya.

── Bagaimana model ini didapat, dan apa yang tersisa ────────────────────

Sembilan percobaan gagal karena MEMBACA assembly lalu menyimpulkan. Yang
akhirnya berhasil: MEREKAM (`CC_TRACEWR`/`CC_TRACERD` di work/emu.py).

Satu panggilan `draw()`:
    65b5 baca page   -> 55 55 55 ...   LATAR, bukan snapshot berbola
    65bb baca mask   -> ff c0 3f ...   fase 3
    65c3 baca sprite -> 00 2a 80 ...   fase 3
    65c5 tulis VRAM  -> 55 6a 95 ...
dan (0x55&0xff)|0x00=0x55, (0x55&0xc0)|0x2a=0x6a, (0x55&0x3f)|0x80=0x95 --
cocok byte per byte. Rumus `draw` benar; anggapan bahwa `page` memuat bola
lama yang salah.

`blend()` ternyata MENULIS ke `page` (offset kode 5f60). Pada panggilan
tumpang-tindih PARSIAL ia menulis tepat 16 byte = 8 baris x 2 kolom yang
beririsan -- bukan 24. Jadi baris `dst = dst + 1` di blend.c bukan kode mati;
catatan itu juga ditempel di src_c/src/blend.c.

Sumber tiap bagian ditentukan dengan SAPUAN TERUKUR, bukan tafsir:

    prep   blend   putmsk   hasil
    latar  page2   page2    176/402
    latar  page2   latar    359/402
    latar  latar   page2    396/402   <- dipakai
    latar  latar   latar    381/402

⭐ `putmsk` memulihkan dari SALINAN TERTINGGAL (`page2`), bukan latar terkini.
Itulah yang meninggalkan "lubang" berwarna latar lama di dalam part yang baru
digambar -- artefak yang memang terlihat di gim asli, dan yang selama ini
tidak bisa direproduksi.

⚠ Panggilan `setball()` dari setupscr TIDAK ikut dihitung: menyertakannya
memberi 0/402, karena rujukan tidak memperlihatkan bola di pita atas saat
animasi berjalan.

── Enam frame terakhir: opcode 0x05 ternyata BUKAN no-op ────────────────

Sisa 6 frame (goal 1 f089 & f121, goal 2 f034, goal 3 f021/f023/f026)
berbentuk sama: kotak beda selebar satu bola, dan RUJUKAN SELALU LEBIH
BERSIH -- gim menghapus lebih banyak. Dugaan pertama "pemotongan di tepi
kiri" (ketiga kegagalan goal 3 ada di x = 8..15) KELIRU.

Yang benar terlihat begitu kotak bedanya diukur, bukan dilihat sepintas:
bedanya persis sebesar IRISAN kotak bola lama dan baru. Contoh goal 3 f023,
bola 89 -> 91: kotak 89..96 dan 91..98, dan barisan yang beda tepat 91..96.

Jejak instruksi (`CC_TRACEWR=26ae-6a00:21` pada goal 3) memberi sebabnya:

    prep   BACA  VRAM y 68..75      -> 5a a5 55 ...   (masih ada bola lama)
    draw   TULIS VRAM y 68..75      -> 5a a5 55 ...   (bola digambar lagi)
    putmsk TULIS VRAM y 68..75      -> 55 55 55 ...   (bola DIHAPUS lagi)

Panggilan putmsk ketiga itu terjadi SESUDAH `drawball` kembali, jadi ia
bukan bagian `xform()`. Sumbernya `animvm.c` baris 578:

    case 0x05:  putmsk(buf9c5, page2);  break;

`buf9c5` berisi nol, dan putmsk melewati sel yang mask-nya BUKAN nol --
jadi mask nol berarti SELURUH kotak dipulihkan. Pada saat itu `drawball`
sudah menukar halaman, sehingga `page2` = cuplikan `prep` frame ini, yaitu
isi layar sebelum bolanya digambar. Efek bersihnya: opcode 0x05 MENGHAPUS
bola yang baru saja digambar.

Port memperlakukan 0x05 sebagai no-op ("gambar ulang mask bola"). Begitu
diterapkan sebagai penghapusan: 396/402 -> **402/402 frame, 100,000000%
piksel**. Tujuh layar, tanpa satu pun pemetaan alamat.

⚠ Kesimpulan yang dicabut: "tepi kiri arena". Ketiga frame goal 3 memang di
x = 8..15, tapi itu kebetulan -- bola memang menyusuri tepi kiri di situ.
Sumbu yang benar adalah IRISAN kotak, bukan batas layar.

Uji regresinya sekarang permanen dan mandiri: `work/test_anim_vs_gim.py`
membuat sendiri tangkapan emulatornya kalau belum ada.

── `end` bukan akhir animasi, hanya akhir skrip SATU PART ────────────────

Animasi sempat berhenti di tengah jalan pada goal 2/3/5/6 (goal 5 cuma 22
dari 66 frame). Dugaan pertama -- "rantai diulang sekali per bola, karena
`goal` @0x718 = JUMLAH BOLA dan 66 = 3 x 22" -- SALAH: diukur, `w718` = 1
untuk goal 5, dan urutan posisi bolanya tidak berulang sama sekali.

Sebabnya struktural. Di `animvm.c` ada DUA gelung: gelung dalam menjalankan
opcode sampai `*scrptr == 0xff`, gelung LUAR berjalan atas i = 0..n1+n2-1
dan tiap putaran memasang `scrptr = parttab[...].scr` part berikutnya. Jadi
`end` cuma memindahkan kursor ke part berikutnya.

Model lama menganggap perpindahan part HANYA terjadi lewat `op03`
(lemparan). Itu kebetulan cocok di goal 1 dan 4 karena `op03` di sana
memang selalu diikuti `end`; di goal lain animasi berhenti terlalu cepat.

Sesudah `end` memajukan part: goal 1..6 = **535/535 frame identik**, dan
kini itu SELURUH panjang animasi game, bukan potongan awalnya.

── Layar judul: opcode 0x11 memantulkan bola dulu ────────────────────────

Sesudah `end` dibetulkan, layar judul cocok 53 frame lalu melenceng di
f054: port menggambar teks "CREATIVE CONTRAPTIONS" sekaligus, rujukan belum
menggambar apa pun di sana.

Penangan opcode 0x11 memanggil `bounce(buf9c5)` SEBELUM membaca satu pun
parameter teks (`animvm.c` baris 361). `bounce()` melempar bola enam kali ke
tepi layar yang berputar searah jarum jam, tiap lemparan lewat `moveball()`
-- ratusan panggilan drawball. Teks judulnya baru muncul sesudah itu.

Tujuannya diundi `rnd()`, jadi bagian ini hanya bisa cocok kalau keadaan
seed-nya sama. Ternyata sudah: seed port sesudah undian pemilihan part goal
128 = **0xa6b8**, persis nilai @0x71a yang diukur di emulator pada frame 53.
Dari situ `bounce()` memakai 32 undian `shuffle()` + 1 `rnd()` -> seed
0x3c11, dan emulator memang mencatat 0x3c11 di frame 54. Lemparan pertama
menuju X = 83 di tepi atas, dan jalur terukurnya (156, 152, 148, ...) cocok
langkah per langkah.

Karena itu `susun()` MENITIPKAN objek Rng-nya ke tiap Part; VM tidak boleh
membuat seed baru.

Hasil: layar judul 53 -> **675/675 frame**, yaitu seluruh animasinya sampai
habis, bukan potongan.

⚠ Pembagian di `moveball()` harus dipotong MENUJU NOL (gaya C), bukan ke
bawah (gaya Python). `(dx * i) / n` sering negatif; `//` menggeser jalur
bola satu piksel. Lihat `vm.cdiv()`.
"""
from . import contrap, pick, render as rend, skrip, vm, font
from .rng import Rng

BG_ = rend.BG
_FASE = [None]


def _fase():
    """Sprite dan mask bola, empat fase pra-geser. Di-cache."""
    if _FASE[0] is None:
        from . import dgtab
        _FASE[0] = dgtab.fase_bola()
    return _FASE[0]


def susun(*a, **k):
    """-> (var, parts, latar). Pembungkus `susun_lengkap()` untuk pemanggil
    lama yang tidak butuh rincian undiannya."""
    var, parts, latar, _pilihan = susun_lengkap(*a, **k)
    return var, parts, latar


def susun_lengkap(goal, graph, mechs, misc, animate, kontrap, seed=0, mode=0,
                  varian=None, sub=None, isi=True, nbola=0, lastgoal=None,
                  lastvar=None, isi_zany=True, lvl=1):
    """-> (var, parts, latar, pilihan) untuk satu goal.

    `parts` sudah URUT RANTAI sesuai `state` di CONTRAP; `latar` adalah layar
    TANPA bola -- ikon bola di pita atas ITU bolanya, dan ia dihapus begitu
    animasi mulai.

    `lastgoal`/`lastvar` = keadaan @0x1e2e/@0x1e30 dari pemanggilan `loadcon()`
    SEBELUMNYA. `loadcon.c` mengundi varian dengan gelung

        do { pick = rnd(cnt) + first; }
        while (lastgoal == sub && cnt >= 2 && pick == lastvar);

    jadi memuat goal yang SAMA dua kali berturut TIDAK PERNAH memberi varian
    yang sama -- dan pengulangan itu MEMAJUKAN seed satu undian lagi, sehingga
    seluruh pemilihan part sesudahnya ikut bergeser. Mengabaikannya membuat
    rantai RNG port melenceng dari gim persis di kasus itu.

    Terukur: pada tangkapan `OBSERVE=fillmech`, `loadcon` kedua punya
    seed 0xc002 dgn lastgoal=1, lastvar=0. Tanpa aturan ulang port memilih
    varian 0; dengan aturan ulang ia memilih varian 1 -- dan varian 1 itulah
    yang terbaca di tabel `base` milik gim.
    """
    vs = kontrap.get(goal)
    if not vs:
        return None, None, None, None
    r = Rng(seed)
    vi = pick.loadcon_pick(r, len(vs), lastgoal=lastgoal,
                           sub=sub if sub is not None else goal,
                           lastvar=lastvar, first=vs[0].get("idx", 0))
    # `varian` memaksa varian struktur tertentu (mode Review memilih demo
    # mekanisme ke-n). Undiannya TETAP dijalankan lebih dulu supaya seed maju
    # sama seperti di game -- pilihan part sesudahnya bergantung pada itu.
    var = vs[min(varian, len(vs) - 1)] if varian is not None else vs[vi]

    # ⭐ Antara `loadcon()` dan `pickpart()` ada SATU panggilan lagi yang
    # memakai RNG, dan mana yang dipanggil tergantung mode (`main_.c`):
    #
    #     mode 3 Fill Zany  -> setzany(nzany + nmechc, state, lvl2, ...)
    #     mode 4 Mix Up     -> setmark(nzany + nmechc, state, lvl, ...)
    #     mode 2 Fill Mech  -> tidak ada
    #
    # Terukur dgn menghitung panggilan di emulator (CC_VRAMSEQ pada 0x10fd,
    # 0x1200, 0x4e01): fillmech 0/0/0, zany 0/1/0, mixup 1/0/1.
    #
    # Undian keduanya HARUS ikut dihitung walaupun hasilnya tidak selalu
    # terlihat: ia memajukan seed, jadi seluruh `pickpart()` sesudahnya
    # bergeser kalau dilewatkan.
    #
    # ⚠ Di mode 3 arena kebetulan TIDAK bergantung undian -- yang tampak cuma
    # mekanisme (dari `fillans()`, deterministik) dan objek zany TERAKHIR (yang
    # dipaksa `row == sub`). Jadi kecocokan piksel di mode 3 TIDAK membuktikan
    # rantai RNG-nya; yang membuktikannya mode 4, di mana semuanya tampak.
    n_slot = len(var["zany"]) + len(var["mech"])
    mark_zany = None
    mark_mech = None
    if mode == 3:
        _mk, mark_zany, _c, _z = pick.setzany(r, n_slot, var["state"])
    elif mode == 4:
        mark_mech, mark_zany, _c = pick.setmark(r, n_slot, var["state"], lvl)
    # `lvl2`: 2 di Mix Up, dan di mode isian 1 (Apprentice) / 2 (Master).
    lvl2 = 2 if mode == 4 else (1 if lvl == 1 else 2)

    jz = [t for (y, x, t) in var["zany"]]
    tz = pick.tabel(graph, jz)
    selz = pick.pickpart(r, tz, jz, sub=goal, mark=mark_zany, lvl2=lvl2)
    jm = [t for (y, x, t) in var["mech"]]
    # ⚠ `loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`: di mode isian `base`
    # adalah direktori yang DISARING + DIPADATKAN, di Contraption Mix Up
    # direktori PENUH. Bedanya baru terasa sesudah slot mekanisme BERTANDA
    # dimodelkan: id acaknya diambil dari `base`, dan kalau `base` tersaring
    # id itu sering tidak ada di sana sama sekali.
    tm = mechs.recs if mode == 4 else pick.tabel(mechs, jm)
    # ⭐ Di Mix Up slot mekanisme BERTANDA mendapat id ACAK (fillans.c baris
    # 46). Daftar tanda mekanisme dulu dibuang di sini -- lihat pick.fillans().
    selm = (pick.fillans(tm, jm, rng=r, mark=mark_mech, lvl3=3, base=tm)
            if mode == 4 else pick.fillans(tm, jm))

    # `sub` = nomor goal. Ia menentukan strip cyan di dasar layar:
    #     if (sub == 1 && mode != 0 && mode != 1)
    #         fillrect(0x10, 0xc0, 0x12f, 199, 1);
    latar = rend.setupscr(rend.new_fb(), mode, nbola=nbola, misc=misc,
                          sub=goal if sub is None else sub)
    rend.apply(latar, contrap.draw_list(
        var, graph, mechs, None, isi_mekanisme=isi, isi_zany=isi_zany,
        corong=False,
        pilihan={"zany": [tz[i]["idx"] for i in selz],
                 "mech": [None if i is None else tm[i]["idx"] for i in selm]}))
    rend.labels(latar, var["pos"])
    # f171f(): pojok kanan pita atas -- nama goal (atau skor di mode 4).
    from . import hud
    hud.judul_atau_skor(rend.KanvasFB(latar), mode, goal if sub is None else sub)

    parts = []
    c_m = c_z = 0
    for s in var["state"]:
        if s == -1:
            (y, x, _t) = var["mech"][c_m]
            tab, base, arc = tm, selm[c_m], mechs
            c_m += 1
        else:
            (y, x, _t) = var["zany"][c_z]
            tab, base, arc = tz, selz[c_z], graph
            c_z += 1
        if base is None:
            continue
        simpul, _ = skrip.muat(tab[base], animate)
        p = vm.Part(y, x, tab, base, simpul)
        p.arc = arc
        # ⭐ RNG-nya DITITIPKAN, bukan dibuat ulang di VM. `bounce()` (opcode
        # 0x11, layar judul) mengundi tepi tujuan dengan `rnd()` yang SAMA;
        # kalau VM memulai seed baru, keenam lemparannya salah arah.
        # Terukur: sesudah undian pemilihan part goal 128 selesai, seed port
        # = 0xa6b8 -- persis nilai @0x71a di emulator pada frame 53, tepat
        # sebelum bounce mulai.
        p.rng = r
        parts.append(p)
    # `pilihan` ikut dikembalikan supaya pemanggil (mis. layar bermain) tidak
    # perlu MENYALIN ulang seluruh rantai undian. Menyalinnya adalah cara
    # paling mudah membuat "layar design != layar run": dua salinan yang
    # lambat laun berbeda. Satu implementasi, satu hasil.
    pilihan = dict(vi=vi, selz=selz, selm=selm, tz=tz, tm=tm, jz=jz, jm=jm,
                   rng=r, mark_zany=mark_zany, lvl2=lvl2)
    return var, parts, latar, pilihan


def frames(goal, graph, mechs, misc, animate, kontrap, seed=0, mode=0,
           maks=400, varian=None, sub=None, seed_setball=True, pembuka=False,
           nbola=1):
    """-> daftar framebuffer indeks-warna, satu per panggilan drawball.

    `pembuka=True` menyisipkan bingkai pembuka `animvm()` (jam pasir + bilah
    bola) DI DEPAN. Bawaannya False supaya perbandingan animasi tetap sejajar
    dengan tangkapan emulator, yang diambil di `drawball` @0x26ae -- yakni
    SESUDAH pembuka. Pembukanya sendiri diadu terpisah oleh
    `work/test_intro.py` (tangkapan di `keyhit` @0x1791): 59/59 bingkai,
    151.040/151.040 piksel.
    """
    var, parts, latar = susun(goal, graph, mechs, misc, animate, kontrap,
                              seed, mode, varian, sub)
    if not parts:
        return []
    awal = []
    if pembuka:
        buka = [row[:] for row in latar]
        kb = rend.KanvasFB(buka)
        for _ in intro(kb, misc, nbola):
            awal.append([row[:] for row in buka])
        latar = buka
    tampil = [row[:] for row in latar]
    # Panggilan `setball(0, i*10)` dari setupscr adalah drawball PERTAMA, dan
    # ia sudah memutar page/page2 sebelum VM mulai. Tanpa menghitungnya,
    # seluruh rantai penyangga bergeser satu.
    if False:   # panggilan setball awal TIDAK ikut dihitung: rujukan tidak
                # memperlihatkan bola di pita atas saat animasi berjalan
                # (diukur: menyertakannya memberi 0/402).
        _x0 = 0
        page2 = (_x0, 0, [[latar[yy][xx] for xx in range(_x0, _x0 + 12)]
                          for yy in range(0, 8)])
        _s, _m = _fase()
        for _r in range(8):
            for _cb in range(3):
                _sb, _mb = _s[0][_r * 3 + _cb], _m[0][_r * 3 + _cb]
                for _p in range(4):
                    _xx = _x0 + _cb * 4 + _p
                    _g = 6 - 2 * _p
                    tampil[_r][_xx] = (page2[2][_r][_cb * 4 + _p] &
                                       ((_mb >> _g) & 3)) | ((_sb >> _g) & 3)
    mesin = vm.VM(parts)
    keluar = []
    page2 = None
    while len(keluar) < maks:
        e = mesin.langkah()
        if e is None or e[0] in ("selesai", "belum"):
            break
        if e[0] == "bingkai":
            p = parts[e[1]]
            rec = p.tabel[e[2]] if e[2] < len(p.tabel) else None
            if rec:
                for buf in (latar, tampil):
                    rend.blit(buf, p.arc, rec, p.x + rec["dx"], p.y + rec["dy"])
            continue
        if e[0] == "teks":
            for buf in (latar, tampil):
                font.gambar(buf, e[1]["teks"], e[1]["x"], e[1]["y"],
                            e[1]["warna"], rend.W, rend.H, e[1]["w"], e[1]["h"])
            continue
        if e[0] == "bunyi":
            continue                       # tak ada efek visual
        if e[0] == "hapus":
            # opcode 0x05 = putmsk(buf9c5, page2) dengan mask NOL: pulihkan
            # SELURUH kotak bola dari cuplikan pra-gambar. Ini BUKAN panggilan
            # drawball, jadi ia TIDAK menghasilkan frame baru.
            if page2 is not None and not e[1]:
                px0, py0, tambalan = page2
                for r, yy in enumerate(range(py0, py0 + 8)):
                    if not (0 <= yy < rend.H):
                        continue
                    for c, xx in enumerate(range(px0, px0 + 12)):
                        if 0 <= xx < rend.W:
                            tampil[yy][xx] = tambalan[r][c]
            continue
        if e[0] != "bola":
            continue
        # 1) inilah yang terlihat saat drawball ini DIMASUKI
        keluar.append([row[:] for row in tampil])
        # 2) drawball, PERSIS seperti `xform()`:
        #
        #    prep()    salin latar di kotak BARU dari layar     -> page
        #    blend()   di daerah tumpang-tindih dgn kotak lama:
        #                salin page2 -> page, DAN tandai supaya putmsk
        #                melewatinya
        #    putmsk()  pulihkan kotak LAMA dari page2, kecuali yang ditandai
        #    draw()    di kotak BARU: layar = (page AND mask) OR sprite
        #
        # ⭐ `blend()` MENULIS ke `dst`. Di rekonstruksi C, baris `dst = dst + 1`
        # tampak seperti aritmetika penunjuk yang mati -- tidak. Jejak instruksi
        # membuktikannya: `prep` menulis 5a a5 55 ke penyangga, lalu `draw`
        # MEMBACA 55 55 55 dari penyangga yang SAMA. Satu-satunya yang berjalan
        # di antaranya adalah `blend`.
        #
        # Itulah sebabnya bola lama tidak pernah tembus di daerah
        # tumpang-tindih: salinan latar yang lebih LAMA (page2, diambil sebelum
        # bola lama digambar) menimpanya lebih dulu.
        #
        # `e[3]` = bendera "jangan hapus" (prevx = 0x140) dari op06/op07/op0a.
        jangan_hapus = e[3] if len(e) > 3 else False
        bx, by = e[1], e[2]
        x0 = (bx >> 2) * 4                     # bola = 3 byte = 12 piksel
        # prep() + blend(): basis `draw` adalah LATAR TERKINI di kotak baru.
        # (Sapuan kombinasi: blend dari latar 396/402, dari page2 hanya 176.)
        page = [[latar[yy][xx] if 0 <= yy < rend.H and 0 <= xx < rend.W else BG_
                 for xx in range(x0, x0 + 12)]
                for yy in range(by, by + 8)]
        if page2 is not None:
            px0, py0, tambalan = page2
            for r, yy in enumerate(range(py0, py0 + 8)):
                for c, xx in enumerate(range(px0, px0 + 12)):
                    tumpang = (x0 <= xx < x0 + 12 and by <= yy < by + 8)
                    if tumpang:
                        continue                                  # blend()
                    if not jangan_hapus and 0 <= yy < rend.H and 0 <= xx < rend.W:
                        # putmsk(): dipulihkan dari SALINAN TERTINGGAL, bukan
                        # latar terkini. Itulah yang meninggalkan "lubang"
                        # berwarna latar lama di dalam part yang baru digambar
                        # -- artefak yang memang terlihat di gim asli.
                        tampil[yy][xx] = tambalan[r][c]           # putmsk()
        spr, msk = _fase()
        fase = bx & 3
        sb, mb = spr[fase], msk[fase]
        for r in range(8):
            yy = by + r
            if not (0 <= yy < rend.H):
                continue
            baris = tampil[yy]
            for cb in range(3):
                s_by, m_by = sb[r * 3 + cb], mb[r * 3 + cb]
                for pxl in range(4):
                    xx = x0 + cb * 4 + pxl
                    if not (0 <= xx < rend.W):
                        continue
                    g = 6 - 2 * pxl
                    baris[xx] = (page[r][cb * 4 + pxl] & ((m_by >> g) & 3)) |                                 ((s_by >> g) & 3)
        page2 = (x0, by, page)
    return awal + keluar


def jalur_bola(goal, graph, mechs, misc, animate, kontrap, seed=0, mode=0,
               maks=400, varian=None):
    """-> (jalur, jangkauan)

    `jalur`      daftar (x, y) bola, satu per panggilan drawball.
    `jangkauan`  {(x_part, y_part): indeks langkah bola saat part itu AKTIF}

    Menggantikan berkas rekaman `ball*.json` dan `reach*.json`. Dipakai mode
    Fill in Mechanisms untuk memutuskan di kotak salah yang MANA bola berhenti:
    kotak yang lebih dulu dicapai rantai, bukan kotak salah pertama menurut
    urutan slot di CONTRAP -- keduanya bisa berbeda.
    """
    var, parts, _latar = susun(goal, graph, mechs, misc, animate, kontrap,
                               seed, mode, varian)
    if not parts:
        return [], {}
    mesin = vm.VM(parts)
    jalur = []
    jangkauan = {}
    while len(jalur) < maks:
        e = mesin.langkah()
        if e is None or e[0] in ("selesai", "belum"):
            break
        if e[0] == "bunyi":
            continue                       # tak ada efek visual
        if e[0] != "bola":
            continue
        p = parts[mesin.aktif]
        jangkauan.setdefault((p.x, p.y), len(jalur))
        jalur.append((e[1], e[2]))
    return jalur, jangkauan


# ── Pembuka `animvm()`: jam pasir lalu bilah bola ───────────────────────────
#
# Sebelum bola pertama digambar, `animvm()` @0x18db menjalankan dua gelung di
# PITA ATAS layar. Keduanya terukur dari VRAM emulator (tangkapan pada
# `keyhit()` @0x1791, yang dipanggil di UJUNG kedua gelung -- jadi tiap
# tangkapan memperlihatkan keadaan SESUDAH gambarnya, bukan sebelum):
#
#   f00, f01   jam pasir: dua sprite 48x8 bergantian di x=0x88
#   f02..f57   bilah 16x8 meluncur dari x=0x78 ke kiri, 2 piksel per bingkai
#   sesudahnya `shftr()` dua kali + satu `fillrect`
#
# ⚠ Mengukurnya perlu memperbaiki harness sendiri LEBIH DULU: tanpa ISR timer
# `ticks` tidak pernah berkurang, jadi gelung jam pasir tak berujung dan
# `CC_NOWAIT` selama ini MELEWATINYA sama sekali. `CC_SNDISR=1` memasang ISR
# sungguhan -- dan saklar itu sendiri masih cacat (pelepas penjaganya
# terdaftar di alamat yang sama dgn pemicunya, jadi `IRET` memicunya lagi).
# Sesudah keduanya beres, intronya langsung terlihat.
#
# BERAPA KALI jam pasir berkedip ditentukan `ticks` (0x27, dihitung mundur ISR
# 18,2 Hz) berbanding `waitn(0x10)` yang menunggu 16 BINGKAI. Jadi jumlahnya
# bergantung kecepatan bingkai, bukan konstanta -- dan itu tidak mengubah satu
# piksel pun, sebab tiap putaran BERAKHIR dengan sprite yang sama (hdrspr[0]).
JAM_X = 0x88                     # blit(hdrspr, 0, 0x88, 8, 0x30)
BILAH_AWAL = 0x78                # for (i = 0x78; i >= goal * 10; i -= 2)
JAM_REC = (3, 2)                 # hdrspr[96] = MISC rec 3 ; hdrspr[0] = rec 2
BILAH_REC = 4                    # hdrspr[192] = MISC rec 4 (16x8)


def panjang_pembuka(nbola, kedip=2):
    """Berapa bingkai yang disisipkan `intro()` -- supaya pemanggil tidak
    perlu memakai angka tetap. Terukur di gim: nbola=1 -> 59."""
    return kedip + len(range(BILAH_AWAL, nbola * 10 - 1, -2)) + 1


def intro(k, misc, nbola, kedip=2):
    """Jalankan pembuka `animvm()` di kanvas `k`, satu `yield` per bingkai.

    `nbola` = `goal` @0x718, yang MENGHITUNG BOLA (bukan nomor goal) -- lihat
    CODE_MAP.md §8b. Posisi akhir bilah = `nbola * 10`.
    """
    for _ in range(kedip):
        k.blit(misc, misc.recs[JAM_REC[0]], JAM_X, 0)
        k.blit(misc, misc.recs[JAM_REC[1]], JAM_X, 0)
        yield

    u56 = nbola * 10
    for i in range(BILAH_AWAL, u56 - 1, -2):
        if i != BILAH_AWAL:
            # jejak 2 piksel di belakang sprite, disapu warna 3
            k.fillrect(i + 0x10, 0, i + 0x11, 7, 3)
        k.blit(misc, misc.recs[BILAH_REC], i, 0)
        yield

    for _ in range(2):
        rend.shftr(k, 0, 4, 8, 0x64, -1)
    k.fillrect(u56 - 8, 0, u56 + 0x10, 7, 3)
    yield
