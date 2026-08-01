"""Mesin animasi — `animvm()` @0x18db, dijalankan dari berkas aset.

Yang membuat mesin ini jauh lebih sederhana dari dugaan awal: `scrptr` @0x3ae
adalah **satu kursor global**. Skrip part TIDAK berjalan serentak. Satu part
aktif pada satu waktu; opcode 0x03/0x0c melempar bola ke part berikutnya dan
kursornya pindah ke skrip part itu.

Arti opcode, dibaca dari animvm.c yang sudah byte-exact:

    0x00  aliran titik jalur bola sampai 0xFF   (f2714 berulang)
    0x0a  satu titik, TANPA hapus jejak         (prevtop/prevx = 0x140)
    0x08  satu titik                            (f2714)
    0x01  aliran bingkai sprite sampai 0xFF     (f278e berulang)
    0x07  satu bingkai, TANPA hapus jejak
    0x09  satu bingkai                          (f278e)
    0x02  jeda n frame
    0x03  lempar bola ke part BERIKUTNYA        (parabola, interp 2823)
    0x0c  lempar bola ke koordinat RELATIF
    0x04  ganti sumber bunyi
    0x0d/0x0e/0x0f  awal gelung / tunggu tombol / akhir gelung

⚠ 0x0a JATUH TEMBUS ke 0x08, dan 0x07 ke 0x09 — di biner badan yang pertama
berakhir tepat di awal badan yang kedua tanpa lompatan. Bedanya cuma
`prevtop = prevx = 0x140`, yaitu "jangan hapus posisi sebelumnya".

Dua penggambarnya:

    f2714(dy, dx):  ballY = dy + sgn(skrip[0]);  ballX = dx + sgn(skrip[1])
                    lalu drawball()  -> SATU frame
    f278e(y, x, base, recs):  idx = base + skrip[0]
                    blit(recs[idx].spr, y + dy, x + dx, h, w)  -> TIDAK
                    memanggil drawball, jadi TIDAK menambah frame tangkapan

`base` adalah indeks record yang TERPILIH untuk part itu, DI TABEL HASIL
`loadarc()` — bukan indeks di direktori arsip penuh. Untuk goal 1 keduanya
kebetulan sama; jangan mengandalkan itu.

⚠ Ambang pemulihan tanda di sini **0xC8**, bukan 0x80. Yang 0x80 dipakai untuk
penempatan STATIS (pickvar/place). Dua ambang berbeda untuk dua keperluan
berbeda; menyamakannya akan menggeser part beberapa piksel di kasus tertentu.
"""

TANDA = 0xC8                     # ambang pemulihan tanda untuk SKRIP animasi
TAK_AKTIF = 0x140                # prevtop/prevx = 320 -> "belum ada bola"


def sgn(v):
    return v - 0x100 if v >= TANDA else v


def _u16(v):
    return bytes((v & 0xFF, (v >> 8) & 0xFF))


def cdiv(a, b):
    """Pembagian bilangan bulat gaya C: dipotong MENUJU NOL, bukan ke bawah.

    Penting di `moveball()`: `(dx * i) / n` sering negatif, dan `//` Python
    membulatkan ke bawah sehingga jalur bolanya meleset satu piksel.
    """
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


class Part:
    """Satu slot: posisi, tabel record yang dipakai, dan skripnya."""

    def __init__(self, y, x, tabel, base, simpul):
        self.y = y
        self.x = x
        self.tabel = tabel       # daftar record (hasil loadarc), diindeks `base + n`
        self.base = base         # indeks record terpilih DI TABEL itu
        self.simpul = simpul     # hasil animvm.parse(), bukan byte mentah
        self.bingkai = base      # record yang sedang tampil


class VM:
    """Penjalan skrip. `langkah()` memberi satu peristiwa per panggilan.

    Peristiwa yang dikeluarkan:
        ("bola", x, y)                   bola pindah -> satu frame tangkapan
        ("bingkai", part, idx_record)    part berganti bingkai
        ("jeda", n)                      jeda n frame
        ("lempar", op, data)             opcode 0x03/0x0c
        ("selesai", None)

    Sengaja berbentuk generator peristiwa dan bukan penggambar: yang diuji
    lebih dulu adalah URUTAN peristiwanya terhadap rujukan VRAM. Kalau
    urutannya salah, langsung menggambar hanya menyembunyikan letak salahnya.

    ⭐ URUTAN GAMBAR, kalau dipakai untuk menggambar. Yang ditiru:

        VRAM saat MASUK drawball N = hasil drawball N-1 + blit part sesudahnya

    Jadi part yang di-blit SESUDAH bola akan MENUTUPI bola. Modelnya bukan
    "latar + bola di atas": sembilan frame gagal dgn kotak beda persis sebesar
    bola sampai ini dibetulkan. drawball N sendiri menghapus bola N-1
    (mengembalikan latar di kotaknya) lalu menggambar bola N.

    ⚠ CATATAN KOREKSI. Sempat dicatat di sini bahwa bola tertinggal DUA
    peristiwa dan part satu ("penyelarasan (2,1)"), dengan halaman ganda
    sebagai sebabnya. Itu KELIRU. Pergeseran itu cuma kebetulan mengompensasi
    urutan gambar yang salah: begitu urutannya dibetulkan, TANPA pergeseran
    sama sekali hasilnya naik dari 101/135 jadi 119/135 frame identik
    (99,9920% -> 99,9984% piksel). Angka yang membaik bukan bukti bahwa
    penjelasannya benar.

    ⚠ Skripnya diambil dari `animvm.parse()`, BUKAN dipindai byte per byte di
    sini. Alasannya mahal: opcode 0x04 (bunyi) panjangnya VARIABEL -- mode 1
    membawa 6 byte, mode 2/3 mengalir sampai penanda GANDA 0xFF 0xFF. Memindai
    sendiri dengan asumsi "lewati 1 byte" membuat tiga titik pertama tetap
    cocok lalu seluruh sisanya melenceng: gejala yang tampak seperti kesalahan
    jalur bola padahal sebenarnya kursor skrip yang tergelincir.
    """

    def __init__(self, parts, aktif=0, rng=None):
        self.parts = parts               # URUT RANTAI (lihat contrap `state`)
        self.aktif = aktif
        # RNG game. `bounce()` (dipanggil opcode 0x11) mengundi tepi layar
        # tujuan, jadi mesin ini butuh keadaan seed yang SAMA dengan yang
        # dipakai `adegan.susun()` untuk memilih part -- bukan seed baru.
        # `susun()` menitipkannya di tiap Part; lihat catatan di sana.
        from .rng import Rng
        self.rng = rng or getattr(parts[0], "rng", None) or Rng(0)
        self.antre = []                  # peristiwa yang sudah dibangkitkan
        self.simpul = list(parts[aktif].simpul)
        self.n = 0                       # simpul ke berapa
        self.k = 0                       # elemen ke berapa di dalam simpul
        self.bx = 0
        self.by = 0
        self.terbang = []                # sisa titik lemparan yang belum keluar
        # `prevtop = prevx = 0x140` yang dipasang op06/op07/op0a. Dibaca
        # `putmsk()`: kalau prevx == 0x140 penghapusan DILEWATI seluruhnya,
        # jadi bola sebelumnya TETAP di layar. Berlaku untuk drawball
        # BERIKUTNYA, lalu direset oleh drawball itu sendiri.
        self.jangan_hapus = False
        self.gelung = 0                  # simpul awal badan gelung (op0d)
        self.sisa = -1                   # pencacah gelung (u5a)
        self.tunggu = False              # mode tunggu tombol (op0e)

    def _pindah(self, ke):
        """Kursor skrip pindah ke part lain. Satu kursor, bukan banyak."""
        self.aktif = ke
        self.simpul = list(self.parts[ke].simpul)
        self.n = 0
        self.k = 0
        self.gelung = 0
        self.sisa = -1

    def _tujuan(self, ke):
        """Titik mendarat di part berikutnya.

        `op03` membaca opcode PERTAMA skrip part tujuan; kalau ia titik jalur
        (0x00/0x08/0x0a/0x0b), titik pertamanya dipakai sebagai tempat mendarat.
        Jadi lemparan diarahkan ke tempat part itu memang menunggu bola --
        bukan ke titik tengah part atau sudutnya.
        """
        p = self.parts[ke]
        for nama, data in ((s[0], s[1] if len(s) > 1 else None) for s in p.simpul):
            if nama == "waypoints" and data:
                a, b = data[0]
            elif nama in ("op08", "op0a", "op0b") and data:
                a, b = data[0], data[1]
            else:
                continue
            return p.y + sgn(a), p.x + sgn(b)
        return p.y, p.x

    def _lempar(self, nama, data):
        """op03 / op0c -> deretan titik parabola (f2823).

        f2823(A, fx, fy, tx, ty, N, 1) dgn fx = ballx = Y LAYAR. Jadi lendutan
        parabolanya jatuh di sumbu TEGAK -- yang memang seharusnya, karena itu
        gravitasi. Interpolatornya dipakai ULANG dari cc/animvm.py yang sudah
        eksak 42/42; jangan tulis ulang di sini.

        ⚠ op03 MENYIMPAN BALIK nilai A yang sudah dipulihkan tandanya, op0c
        MEMBUANGNYA -- di biner, AX yang memuat nilai terpulihkan langsung
        ditimpa `mov ax,si` tanpa pernah disimpan balik, jadi f2823 menerima
        byte MENTAH. Itu tampak seperti bug di gim aslinya; kita meniru apa
        adanya, karena yang dikejar adalah tampilan yang SAMA, bukan yang benar.
        Menyeragamkan kedua case juga sudah diuji di src_c dan menurunkan
        penjajaran biner.
        """
        from ..animvm import interp_2823
        N = data[1]
        if nama == "op03":
            A = sgn(data[0])
            ke = self.aktif + 1
            if ke >= len(self.parts):
                return None
            ty, tx = self._tujuan(ke)
        else:
            # op0c: sasarannya dibaca dari operan opcode BERIKUTNYA di skrip
            # yang SAMA, relatif ke posisi PART -- bukan ke posisi bola:
            #     u54 = scrptr; u54++;            <- lewati byte opcode
            #     u4c = sgn(*u54++) + u22;        <- + Y part
            #     u50 = sgn(*u54++) + u24;        <- + X part
            # `scrptr` sendiri TIDAK dimajukan, jadi opcode itu tetap dijalankan
            # sesudahnya. Kelihatan mubazir, dan memang begitu adanya.
            A = data[0]                  # ⚠ MENTAH, lihat catatan di bawah
            p = self.part
            lanjut = self.simpul[self.n] if self.n < len(self.simpul) else None
            if lanjut is None or len(lanjut) < 2 or not lanjut[1]:
                return None
            d = lanjut[1]
            a, b = (d[0] if not isinstance(d[0], tuple) else d[0][0],
                    d[1] if not isinstance(d[0], tuple) else d[0][1])
            ty, tx = p.y + sgn(a), p.x + sgn(b)
            ke = self.aktif
        if N <= 0:
            return None
        titik = interp_2823(self.by, self.bx, ty, tx, N, A)
        self.terbang = list(titik)
        self.lempar_ke = ke
        return True

    # ── bounce(): layar judul ─────────────────────────────────────────────
    #
    # Opcode 0x11 memanggil `bounce(buf9c5)` SEBELUM menulis teksnya. Itulah
    # sebabnya layar judul punya ratusan frame lebih banyak daripada dugaan
    # semula: teks "CREATIVE CONTRAPTIONS" baru muncul sesudah bolanya selesai
    # memantul enam kali.
    #
    # Sumber: src_c/src/bounce.c (398 byte, byte-identik dgn biner).

    def _shuffle(self):
        """`shuffle()` @0x2b34 — 32 kali `rnd(2)`.

        Yang digambarnya (kocok palet) tidak mengubah arena, tapi PEMAKAIAN
        RNG-nya harus ditiru: tanpa 32 undian ini, tepi tujuan keenam
        lemparan berikutnya akan salah semua.
        """
        for _ in range(0x20):
            self.rng.rnd(2)

    def _moveball(self, x1, y1, x2, y2, n):
        """`moveball()` @0x29b0 — gerak LURUS n langkah, tiap langkah drawball.

        Nama argumennya mengikuti biner: `x1` = ballx = **Y layar**,
        `y1` = bally = **X layar**. Lihat setball(): `balltop = 199 - x`.
        """
        ev = []
        dx = x2 - x1
        dy = y2 - y1
        for i in range(1, n):
            self.by = x1 + cdiv(dx * i, n)
            self.bx = y1 + cdiv(dy * i, n)
            ev.append(("bola", self.bx, self.by, False))
        self.by, self.bx = x2, y2        # langkah terakhir DIPAKSA tepat
        ev.append(("bola", self.bx, self.by, False))
        return ev

    def _bounce(self):
        """-> daftar peristiwa untuk enam pantulan bola di layar judul.

        Tepi tujuan berputar searah jarum jam. Dengan sumbu yang SUDAH
        dibetulkan (0x260 = Y, 0x25e = X) urutannya: atas, kanan, bawah, kiri
        -- bukan "kiri, bawah, kanan, atas" seperti tertulis di bounce.c,
        yang ditulis saat nama ballx/bally masih dikira harfiah.

        Jumlah langkah dari hampiran jarak OKTAGONAL (maks + separuh min),
        lalu dibagi 4 lewat DUA kali /2 seperti di biner.
        """
        ev = []
        self._shuffle()
        if self.jangan_hapus:            # prevtop/prevx masih 0x140
            self._shuffle()
            return ev
        ph = 0
        for _ in range(6):               # keyhit() selalu 0 di sini
            if ph == 0:                  # tepi ATAS
                tx = 8
                ty = self.rng.rnd(0x10E) + 0x14
            elif ph == 1:                # tepi KANAN
                ty = 0x137
                tx = self.rng.rnd(0x6F) + 0x1C
            elif ph == 2:                # tepi BAWAH
                tx = 0x97
                ty = self.rng.rnd(0x10E) + 0x14
            else:                        # tepi KIRI
                tx = self.rng.rnd(0x6F) + 0x1C
                ty = 0
            ph = 0 if ph + 1 > 3 else ph + 1
            bxc, byc = self.by, self.bx  # ballx = Y, bally = X
            a = abs(byc - ty)
            b = abs(bxc - tx)
            a = (max(a, b)) + (min(a, b)) // 2
            a = a // 2
            d = a // 2
            if d > 0xB4:
                d = 0x96
            ev.append(("bunyi", 1, _u16(500) + _u16((d * 8 + 500) & 0xFFFF)
                       + _u16(8)))
            ev.extend(self._moveball(bxc, byc, tx, ty, d))
        # putmsk(spr, page2) dgn mask NOL -> hapus bolanya, sama seperti op05.
        ev.append(("hapus", False))
        return ev

    @property
    def part(self):
        return self.parts[self.aktif]

    def _titik(self, a, b, jangan=False):
        p = self.part
        self.by = p.y + sgn(a)           # ballx @0x260 = Y layar
        self.bx = p.x + sgn(b)           # bally @0x25e = X layar
        jh = self.jangan_hapus or jangan
        self.jangan_hapus = False
        return ("bola", self.bx, self.by, jh)

    def _bingkai(self, v):
        p = self.part
        p.bingkai = p.base + v
        return ("bingkai", self.aktif, p.bingkai)

    def langkah(self):
        """Peristiwa berikutnya, atau None kalau skripnya habis."""
        if self.antre:                   # sisa peristiwa bounce()
            return self.antre.pop(0)
        if self.terbang:                 # bola sedang melayang
            y, x = self.terbang.pop(0)
            self.by, self.bx = y, x
            jh = self.jangan_hapus
            self.jangan_hapus = False
            if not self.terbang and self.lempar_ke != self.aktif:
                self._pindah(self.lempar_ke)
            return ("bola", self.bx, self.by, jh)
        while self.n < len(self.simpul):
            nama = self.simpul[self.n][0]
            data = self.simpul[self.n][1] if len(self.simpul[self.n]) > 1 else None
            if nama == "waypoints":
                if self.k < len(data):
                    a, b = data[self.k]
                    self.k += 1
                    return self._titik(a, b)
                self.n += 1; self.k = 0; continue
            if nama == "frames":
                if self.k < len(data):
                    v = data[self.k]
                    self.k += 1
                    return self._bingkai(v)
                self.n += 1; self.k = 0; continue
            self.n += 1; self.k = 0
            if nama == "end":
                # ⭐ `end` (0xFF) BUKAN akhir animasi -- ia akhir SKRIP SATU
                # PART. Di `animvm.c` gelung dalam berhenti pada `*scrptr ==
                # 0xff`, lalu gelung LUAR (atas i = 0 .. n1+n2-1) memasang
                # `scrptr = parttab[...].scr` part berikutnya dan jalan lagi.
                # Yang mengakhiri animasi adalah opcode 0x10, atau habisnya
                # part.
                #
                # Model lama berhenti di sini. Itu tidak terlihat pada goal 1
                # dan 4 karena di sana part terakhir yang dijangkau memang
                # part terakhir; pada goal 2/3/5/6 animasi berhenti di
                # tengah jalan (goal 5: 22 dari 66 frame).
                if self.aktif + 1 >= len(self.parts):
                    return ("selesai", None)
                self._pindah(self.aktif + 1)
                continue
            if nama in ("op08", "op0a"):
                # 0x0a JATUH TEMBUS ke 0x08 sesudah memasang "jangan hapus",
                # jadi benderanya berlaku untuk titik ini juga.
                return self._titik(data[0], data[1], nama == "op0a")
            if nama in ("op09", "op07"):
                if nama == "op07":
                    self.jangan_hapus = True
                return self._bingkai(data[0])
            if nama == "op02":
                return ("jeda", data[0])
            if nama == "op04":
                # Bunyi. Tidak menggambar apa pun, tapi TETAP dipancarkan
                # supaya pemutar bisa mengikutinya; penggambar frame
                # mengabaikannya. Simpulnya ("op04", mode, payload).
                simpul = self.simpul[self.n - 1]
                return ("bunyi", simpul[1], simpul[2] if len(simpul) > 2 else b"")
            if nama == "op05":
                # ⭐ HAPUS BOLA. Bukan no-op, dan bukan "gambar ulang mask"
                # seperti dikira sebelumnya: `animvm.c` baris 578 memanggil
                # `putmsk(buf9c5, page2)` -- yaitu putmsk dengan mask NOL,
                # sehingga SELURUH kotak dipulihkan dari `page2`.
                #
                # Pada saat opcode ini jalan, `drawball` sudah menukar halaman,
                # jadi `page2` adalah cuplikan `prep` FRAME INI: isi layar di
                # kotak bola SEBELUM bolanya digambar. Efeknya: bola yang baru
                # saja digambar dihapus lagi.
                #
                # Diukur dari jejak instruksi (CC_TRACEWR pada panggilan
                # drawball ke-21 goal 3): sesudah `draw` menulis bola di
                # y 68..75, putmsk menulis balik 55 55 55 di baris yang sama.
                #
                # `prevx == 0x140` tetap melewatkan penghapusan, dan benderanya
                # TIDAK dikonsumsi di sini -- putmsk tidak menyentuh prevx.
                return ("hapus", self.jangan_hapus)
            if nama == "op06":
                self.jangan_hapus = True
                continue
            if nama == "op0d":           # awal badan gelung
                self.gelung = self.n
                self.sisa = -1
                continue
            if nama == "op0e":           # aktifkan mode tunggu tombol
                self.tunggu = True
                continue
            if nama == "op0f":           # akhir gelung
                # u5a == -1  -> ambil pencacah, balik ke awal badan
                # u5a  > 0   -> kurangi, balik ke awal badan
                # u5a == 0   -> keluar dari gelung
                if self.sisa == -1:
                    self.sisa = data[0] if data else 0
                elif self.sisa > 0:
                    self.sisa -= 1
                else:
                    continue
                self.n = self.gelung
                continue
            if nama == "op10":           # akhir goal
                return ("selesai", None)
            if nama == "op11":           # tulis teks berparameter dari skrip
                # Di sinilah judul "CREATIVE CONTRAPTIONS" digambar -- bukan
                # oleh layar statis. Dan `bounce(buf9c5)` dipanggil LEBIH DULU,
                # sebelum satu pun parameter teks dibaca: bola memantul enam
                # kali dulu, teksnya baru muncul sesudahnya.
                self.antre = self._bounce() + [("teks", data)]
                return self.antre.pop(0)
            if nama in ("op03", "op0c"):
                if self._lempar(nama, data) is None:
                    return ("selesai", None)
                return self.langkah()
            return ("belum", nama, data)
        return None
