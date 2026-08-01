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

Terukur terhadap tangkapan VRAM emulator, tujuh layar (goal 1..6 + judul 128):
381/402 frame byte-identik, 99,9988% piksel. Goal 4, 5, 6 dan layar judul
100% frame.

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

── Dua kesimpulan saya sendiri yang TERBANTAH ────────────────────────────

1. "Uji satu langkah membuktikan modelnya salah." TIDAK SAHIH. Uji itu
   mengambil frame gim sebagai masukan, menjalankan satu drawball, lalu
   mengadu dengan frame berikutnya (dibatasi ke kotak bola). Model setia
   dapat 23/118. Tapi KONTROL-nya -- model sederhana yang sudah terbukti
   381/402 -- dapat 26/118 di uji yang sama. Ujinya tidak membedakan apa
   pun, karena blit part sering jatuh DI DALAM kotak bola di antara dua
   frame. Jangan pakai lagi tanpa menyaring frame yang bersih dari blit.

2. "Bola dihapus lalu digambar ulang bergantian padahal diam." BUKAN
   misteri. Pada frame 5..9 bola memang diam di X=51, Y=24, dan memang
   hilang di f007 lalu kembali di f008 -- tetapi yang menghapusnya adalah
   BLIT PART, bukan penghapusan bola: bingkai part 0 saat itu GRAPH 3,
   lebar 52 piksel dari x=8, yaitu x 8..59, yang menutupi seluruh kotak
   bola (48..59). Model sederhana menghasilkan pola yang sama, dan memang
   ketiga frame itu cocok.

Yang tersisa benar-benar hanya dua gejala, keduanya di goal 1:
    f089        hapus-jejak separuh tinggi (26 piksel)
    f121..f136  sisa 7 piksel tetap di (139..145, 34..35)

Yang SUDAH pasti dan tidak perlu diuji ulang:
  - VM eksak: posisi bola 136/136, bendera hapus 135/136 vs gim
    (`python work/test_vm_vs_gim.py <folder CC_VRAMSEQ>`);
  - isi latar port sama dengan penyangga gim (`page2` frame 10 identik);
  - 0x26AE memang alamat MASUK drawball (offset +0), penyelarasan frame benar;
  - model "salinan tersimpan" yang diturunkan dari blitmsk.asm memberi
    23/402 -- jauh di bawah 381/402 -- dan sebabnya BELUM diketahui.

Penyaringan itu SUDAH dijalankan: dari 136 peristiwa bola, 107 tidak diikuti
blit part. Model setia hanya dapat 19/106 di antaranya -- jadi ia memang
salah, bukan korban gangguan blit.

Dan inilah pernyataan setepat yang bisa dibuat, dari f011 -> f012 (bola
(55,24) -> (57,25), kotak lama x=52.., kotak baru x=56..):

    DAERAH TUMPANG-TINDIH KELUAR BERSIH DI GIM. Baris 25 di f012 cyan pada
    x=56..58; tidak ada sisa bola lama sama sekali.

Model setia meninggalkan noda persis di situ, dan alasannya terbaca dari
assembly-nya: `blend()` menandai sel tumpang-tindih supaya `putmsk()` TIDAK
memulihkannya, lalu `draw()` menyusun bola di atas `page` -- salinan yang
`prep()` ambil SEBELUM penghapusan, jadi masih memuat bola lama. Di mana
mask bola baru mempertahankan latar, bola lama seharusnya tembus.

Gim tidak menunjukkannya. Ketiga kemungkinan sudah dipersempit dengan
membuang isi penyangga `page` tepat sesudah `prep` berjalan (hook di masuk
`blend` @0x5EA6, `CC_VSPTR=2e0:24`):

    panggilan 11, bola (57,25), page=0x0284
    snapshot: aaa555 aba955 aae955 aaa955 aaa955 aaa555 6a9555 155555

`0xaa` = empat piksel magenta -- BOLA LAMA MEMANG IKUT TERSALIN. Jadi:

  (a) GUGUR -- prep menyalin VRAM yang masih memuat bola lama;
  (b) tidak mungkin -- `putmsk` jelas melewati sel ber-mask bukan-nol, dan
      `blend` jelas menandai daerah tumpang-tindih dengan 0xff;
  (c) rumus `draw` terbaca langsung: VRAM = (page AND mask) OR sprite.

Dengan mask fase 1 baris 0 = `fc 03 ff` dan sprite = `02 a8 00`, byte
pertamanya menghasilkan (0xaa & 0xfc) | 0x02 = 0xaa -- empat piksel magenta.
Gim menuliskan cyan di situ.

Jadi salah satu dari ketiga bacaan itu keliru pada tingkat yang tidak
terlihat dari teks assembly-nya. Langkah berikutnya BUKAN model baru
melainkan penelusuran tingkat-instruksi di dalam `draw` (@0x657C): rekam
SI, DI, DL, dan byte yang benar-benar ditulis ke ES:[SI] untuk satu
panggilan. Semua bahan sudah ada; yang kurang cuma jejak itu.
"""
from . import contrap, pick, render as rend, skrip, vm, font
from .rng import Rng


def susun(goal, graph, mechs, misc, animate, kontrap, seed=0, mode=0, varian=None,
          sub=None, isi=True, nbola=0):
    """-> (var, parts, latar) untuk satu goal.

    `parts` sudah URUT RANTAI sesuai `state` di CONTRAP; `latar` adalah layar
    TANPA bola -- ikon bola di pita atas ITU bolanya, dan ia dihapus begitu
    animasi mulai.
    """
    vs = kontrap.get(goal)
    if not vs:
        return None, None, None
    r = Rng(seed)
    vi = pick.loadcon_pick(r, len(vs))
    # `varian` memaksa varian struktur tertentu (mode Review memilih demo
    # mekanisme ke-n). Undiannya TETAP dijalankan lebih dulu supaya seed maju
    # sama seperti di game -- pilihan part sesudahnya bergantung pada itu.
    var = vs[min(varian, len(vs) - 1)] if varian is not None else vs[vi]

    jz = [t for (y, x, t) in var["zany"]]
    tz = pick.tabel(graph, jz)
    selz = pick.pickpart(r, tz, jz, sub=goal)
    jm = [t for (y, x, t) in var["mech"]]
    tm = pick.tabel(mechs, jm)
    selm = pick.fillans(tm, jm)

    # `sub` = nomor goal. Ia menentukan strip cyan di dasar layar:
    #     if (sub == 1 && mode != 0 && mode != 1)
    #         fillrect(0x10, 0xc0, 0x12f, 199, 1);
    latar = rend.setupscr(rend.new_fb(), mode, nbola=nbola, misc=misc,
                          sub=goal if sub is None else sub)
    rend.apply(latar, contrap.draw_list(
        var, graph, mechs, None, isi_mekanisme=isi, corong=False,
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
        parts.append(p)
    return var, parts, latar


def frames(goal, graph, mechs, misc, animate, kontrap, seed=0, mode=0,
           maks=400, varian=None, sub=None):
    """-> daftar framebuffer indeks-warna, satu per panggilan drawball."""
    var, parts, latar = susun(goal, graph, mechs, misc, animate, kontrap,
                              seed, mode, varian, sub)
    if not parts:
        return []
    tampil = [row[:] for row in latar]
    mesin = vm.VM(parts)
    keluar = []
    riwayat = []
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
        if e[0] != "bola":
            continue
        # 1) inilah yang terlihat saat drawball ini DIMASUKI
        keluar.append([row[:] for row in tampil])
        # 2) drawball: hapus bola sebelumnya, lalu gambar yang baru.
        #
        # `e[3]` = bendera "jangan hapus" (prevx = 0x140) yang dipasang
        # op06/op07/op0a. `putmsk()` melewati penghapusan seluruhnya kalau
        # benderanya menyala, sehingga bola sebelumnya TETAP di layar.
        jangan_hapus = e[3] if len(e) > 3 else False
        riwayat.append((e[1], e[2]))
        if len(riwayat) > 1 and not jangan_hapus:
            px, py = riwayat[-2]
            x0 = (px >> 2) * 4                 # bola menempati 3 byte = 12 piksel
            for yy in range(py, min(py + 8, rend.H)):
                baris_l, baris_t = latar[yy], tampil[yy]
                for xx in range(x0, min(x0 + 12, rend.W)):
                    baris_t[xx] = baris_l[xx]
        rend.bola(tampil, e[1], e[2])
    return keluar


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
