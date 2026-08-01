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

Tujuh percobaan di sumbu ini. Dicatat supaya tidak diulang: jangan
memodelkan ulang penyimpanan latar; baca `blitmsk.asm` kalau mau lanjut.
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
        if e[0] != "bola":
            continue
        # 1) inilah yang terlihat saat drawball ini DIMASUKI
        keluar.append([row[:] for row in tampil])
        # 2) drawball: hapus bola sebelumnya, lalu gambar yang baru
        riwayat.append((e[1], e[2]))
        if len(riwayat) > 1:
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
        if e[0] != "bola":
            continue
        p = parts[mesin.aktif]
        jangkauan.setdefault((p.x, p.y), len(jalur))
        jalur.append((e[1], e[2]))
    return jalur, jangkauan
