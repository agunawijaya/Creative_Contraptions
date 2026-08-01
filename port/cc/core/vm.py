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


def sgn(v):
    return v - 0x100 if v >= TANDA else v


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

    ⚠ Skripnya diambil dari `animvm.parse()`, BUKAN dipindai byte per byte di
    sini. Alasannya mahal: opcode 0x04 (bunyi) panjangnya VARIABEL -- mode 1
    membawa 6 byte, mode 2/3 mengalir sampai penanda GANDA 0xFF 0xFF. Memindai
    sendiri dengan asumsi "lewati 1 byte" membuat tiga titik pertama tetap
    cocok lalu seluruh sisanya melenceng: gejala yang tampak seperti kesalahan
    jalur bola padahal sebenarnya kursor skrip yang tergelincir.
    """

    def __init__(self, parts, aktif=0):
        self.parts = parts
        self.aktif = aktif
        self.simpul = list(parts[aktif].simpul)
        self.n = 0                       # simpul ke berapa
        self.k = 0                       # elemen ke berapa di dalam simpul
        self.bx = 0
        self.by = 0

    @property
    def part(self):
        return self.parts[self.aktif]

    def _titik(self, a, b):
        p = self.part
        self.by = p.y + sgn(a)           # ballx @0x260 = Y layar
        self.bx = p.x + sgn(b)           # bally @0x25e = X layar
        return ("bola", self.bx, self.by)

    def _bingkai(self, v):
        p = self.part
        p.bingkai = p.base + v
        return ("bingkai", self.aktif, p.bingkai)

    def langkah(self):
        """Peristiwa berikutnya, atau None kalau skripnya habis."""
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
                return ("selesai", None)
            if nama in ("op08", "op0a"):
                return self._titik(data[0], data[1])
            if nama in ("op09", "op07"):
                return self._bingkai(data[0])
            if nama == "op02":
                return ("jeda", data[0])
            if nama == "op04":
                continue                 # bunyi: tidak menggambar apa pun
            if nama in ("op03", "op0c"):
                return ("lempar", nama, data)
            return ("belum", nama, data)
        return None
