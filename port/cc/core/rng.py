"""Generator acak game — SALINAN PERSIS dari `rnd()` @0x5A5B.

Sumbernya `src_c/asm/snd1.asm`, yang sudah cocok byte-per-byte dengan biner
asli, jadi ini bukan tafsir:

    rnd:    MOV BX, SP
            MOV AX, 3E85H
            MUL WORD PTR DS:[71AH]        ; seed * 0x3E85
            ADD AX, 3619H                 ; + 0x3619   (16 bit, buang carry)
            MOV WORD PTR DS:[71AH], AX    ; simpan seed baru
            MOV AX, WORD PTR [BX+2]       ; argumen n
            MUL WORD PTR DS:[71AH]        ; n * seed  -> DX:AX
            MOV AX, DX                    ; ambil KATA TINGGI
            RET

Jadi: LCG 16-bit, lalu hasilnya diskalakan ke [0, n) dengan mengambil kata
tinggi dari perkalian 16x16. Itu cara klasik menghindari operasi modulo yang
mahal di 8086 -- dan ia TIDAK sama dengan `seed % n`, jadi menirunya dengan
modulo akan memberi urutan yang berbeda.

KENAPA INI PENTING UNTUK PORT. Selama urutan acaknya tidak sama, "tampilannya
sama persis" tidak bisa DIUKUR -- varian kontraption, palet part, dan slot yang
dikosongkan semuanya diundi. Menyamakan RNG lebih dulu adalah syarat untuk
membandingkan piksel sama sekali.

⚠ `seed` ada di DGROUP 0x71A dan nilai AWALNYA di berkas .EXE adalah 0. Game
mengisinya saat mulai (lihat `sndini` yang membaca jam BIOS lewat INT 1Ah).
Untuk perbandingan yang bisa diulang, setel seed secara eksplisit.
"""

MUL = 0x3E85
ADD = 0x3619
MASK = 0xFFFF


class Rng:
    """Keadaan RNG game. Satu instance = satu `seed` @0x71A."""

    def __init__(self, seed=0):
        self.seed = seed & MASK

    def next_seed(self):
        self.seed = (self.seed * MUL + ADD) & MASK
        return self.seed

    def rnd(self, n):
        """Setara `rnd(n)`: majukan seed, lalu kembalikan kata TINGGI dari n*seed.

        Hasilnya di [0, n) untuk n > 0. Untuk n == 0 hasilnya 0, sama seperti
        biner (perkalian dengan nol).
        """
        s = self.next_seed()
        return ((n & MASK) * s) >> 16

    # ---- alat bantu untuk pengujian --------------------------------------
    def state(self):
        return self.seed

    def set_state(self, s):
        self.seed = s & MASK


_default = Rng()


def rnd(n):
    """Bentuk fungsi global, memakai satu keadaan bersama."""
    return _default.rnd(n)


def seed(s):
    _default.set_state(s)


def get_seed():
    return _default.state()
