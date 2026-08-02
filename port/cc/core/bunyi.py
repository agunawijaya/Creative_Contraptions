"""Suara PC-speaker — opcode `0x04` dan penangan interupsi timer.

Nada digerakkan penangan INT 1Ch yang dipasang `sndsave` (vektor @0x70), bukan
oleh gelung utama. Yang menentukan bentuk datanya ada di `snd2.asm`:

    MOV DX, 12H ; MOV AX, 34DEH ; DIV CX      -> 0x1234DE / CX = 1.193.182 / CX

Itu pembagi PIT. Artinya **angka di skrip adalah FREKUENSI dalam Hz**, bukan
pembagi dan bukan nomor not. `CX == 0` berarti diam.

Format alirannya, dari `ADD [1EF6H], 3` dan pembacaannya:

    tiap not = u16 frekuensi + u8 durasi (dalam tik timer)
    frekuensi == 0xFFFF  -> akhir aliran
                            mode 3: putar ulang dari awal
                            mode 2: berhenti

Mode dari opcode `0x04`:

    1   tiga word tetap -- sapuan nada (dipakai `timedrw()` saat bilah
        timer terisi di awal)
    2   aliran not, sekali jalan
    3   aliran not, BERULANG
    lain (mis. 0) tanpa payload -> matikan bunyi

⚠ Durasi dihitung dalam tik INT 1Ch, yaitu ~18,2 per detik pada PC/XT. Nilai
itu dipakai apa adanya di sini; kalau kelak terbukti gim memprogram ulang PIT,
angka ini yang perlu diperbaiki -- bukan format notnya.
"""
import math
import struct

PIT = 1193182                    # 0x1234DE
TIK = 18.2065                    # INT 1Ch per detik (PC/XT)
AKHIR = 0xFFFF


# Dua deskriptor nada pendek di DGROUP, keduanya arpeggio naik tiga not
# (1048, 1176, 1320 Hz, satu tik masing-masing):
#
#   tune1 @0x1DD0  dipakai `tone()`  -- kedipan skor (`showsc` flash >= 2)
#   tune2 @0x1DDB  dipakai `tone2()` -- BUNYI PILIH MENU (`runmenu`), dan juga
#                  `askopts()` serta `revdet()`
#
# `tone2()` menyimpan lalu memulihkan konteks suara (`sndsave`/`sndrest`)
# supaya nada latar yang sedang berjalan tidak rusak.
NADA_TONE = 0x1DD0
NADA_TONE2 = 0x1DDB


def nada_dgroup(addr):
    """-> daftar (frekuensi, tik) dari deskriptor nada di DGROUP."""
    from . import dgtab
    return not_dari(2, bytes(dgtab.dgroup()[addr:addr + 24]))[0]


def not_dari(mode, payload):
    """-> (daftar (frekuensi_hz, tik), berulang).

    `payload` = byte mentah sesudah byte mode, seperti diberikan
    `animvm.parse()` pada simpul `op04`.
    """
    if mode in (2, 3):
        out = []
        i = 0
        b = bytes(payload)
        while i + 2 < len(b):
            f = struct.unpack_from("<H", b, i)[0]
            if f == AKHIR:
                break
            out.append((f, b[i + 2]))
            i += 3
        return out, mode == 3
    if mode == 1 and len(payload) >= 6:
        # Tiga word tetap. `timedrw()` mengisinya {500, 0x474, 0x10} tepat
        # sebelum bilah timer diisi sepotong demi sepotong, jadi ini sapuan
        # dan bukan not tunggal. Ditafsirkan (awal, akhir, langkah).
        a, z, s = struct.unpack_from("<HHH", bytes(payload), 0)
        if s == 0:
            return [(a, 1)], False
        arah = 1 if z >= a else -1
        return [(f, 1) for f in range(a, z + arah, arah * max(1, s))], False
    return [], False


def gelombang(notes, rate=22050, volume=0.25):
    """Not -> sampel gelombang KOTAK 8-bit bertanda, seperti bunyi PC-speaker.

    Speaker PC hanya bisa menyala atau mati, jadi kotak adalah bentuk yang
    benar -- bukan sinus.
    """
    keluar = []
    for freq, tik in notes:
        n = max(1, int(rate * max(1, tik) / TIK))
        if freq <= 0:
            keluar.extend([0] * n)
            continue
        periode = max(2, int(rate / max(1, freq)))
        tinggi = int(127 * volume)
        for i in range(n):
            keluar.append(tinggi if (i % periode) * 2 < periode else -tinggi)
    return keluar


def durasi(notes):
    """Panjang total dalam detik."""
    return sum(max(1, t) for _f, t in notes) / TIK


class Pemutar:
    """Pemutar sederhana di atas pygame.mixer. Diam kalau mixer tak tersedia."""

    def __init__(self, pygame=None, rate=22050):
        self.rate = rate
        self.pygame = pygame
        self.aktif = False
        self._cache = {}
        if pygame is None:
            return
        try:
            pygame.mixer.init(frequency=rate, size=8, channels=1, buffer=512)
            self.aktif = True
        except Exception:
            self.aktif = False

    def mainkan(self, mode, payload):
        if not self.aktif:
            return False
        kunci = (mode, bytes(payload))
        if kunci not in self._cache:
            notes, ulang = not_dari(mode, payload)
            if not notes:
                self._cache[kunci] = None
            else:
                import array
                buf = array.array("b", gelombang(notes, self.rate))
                self._cache[kunci] = (self.pygame.mixer.Sound(buffer=buf), ulang)
        item = self._cache[kunci]
        if item is None:
            return False
        suara, ulang = item
        suara.play(loops=-1 if ulang else 0)
        return True

    def klik(self, addr=NADA_TONE2):
        """`tone2()` -- bunyi pendek saat memilih di menu.

        Port lama diam sama sekali di menu; gim membunyikan arpeggio tiga not
        tiap kali pemain menekan ENTER (`runmenu()` memanggil `tone2()`).
        """
        if not self.aktif:
            return False
        from . import dgtab
        return self.mainkan(2, bytes(dgtab.dgroup()[addr:addr + 24]))

    def diam(self):
        if self.aktif:
            self.pygame.mixer.stop()
