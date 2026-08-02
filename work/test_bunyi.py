"""Uji dekode suara: format not, frekuensi, dan sapuan mode 1."""
import os, sys, struct
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port"))
from cc.core import bunyi, skrip, contrap, pick                     # noqa: E402
from cc.core.archive import Archive                                 # noqa: E402
from cc.core.rng import Rng                                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "_ORIGINAL_READONLY")
gagal = []


def cek(nama, dapat, harap):
    if dapat != harap:
        gagal.append("%s: %r != %r" % (nama, dapat, harap))
    print("  %-52s %s" % (nama, "OK" if dapat == harap else "GAGAL"))


print("format not: u16 frekuensi + u8 durasi, diakhiri FFFF")
p = struct.pack("<HB", 440, 3) + struct.pack("<HB", 880, 5) + b"\xff\xff\x00"
cek("mode 2 -> dua not", bunyi.not_dari(2, p)[0], [(440, 3), (880, 5)])
cek("mode 2 tidak berulang", bunyi.not_dari(2, p)[1], False)
cek("mode 3 BERULANG", bunyi.not_dari(3, p)[1], True)
cek("FFFF mengakhiri aliran", len(bunyi.not_dari(2, p + struct.pack("<HB", 100, 1))[0]), 2)
cek("mode 0 tanpa not", bunyi.not_dari(0, b"")[0], [])

print("\nmode 1 = sapuan (timedrw menyetel 500, 1140, 16)")
sw = bunyi.not_dari(1, struct.pack("<HHH", 500, 0x474, 0x10))[0]
cek("mulai 500 Hz", sw[0][0], 500)
# ⚠ BERAKHIR DI 1124, BUKAN 1140. Nilai yang SAMA DENGAN `akhir` tidak pernah
# dibunyikan: `tone3` @0x5B73 (snd2.asm, L5C50) menguji `CMP AX,CX / JE stop`
# SEBELUM menulis nada, jadi deretnya putus satu langkah lebih awal. Harapan
# 1140 di sini peninggalan tafsiran lama yang belum pernah diukur.
cek("berakhir satu langkah SEBELUM nilai akhir", sw[-1][0], 1140 - 16)
cek("langkah 16 Hz", sw[1][0] - sw[0][0], 16)

print("\nPIT: 1.193.182 / frekuensi = pembagi")
cek("440 Hz -> pembagi 2711", bunyi.PIT // 440, 2711)
cek("PIT = 0x1234DE", bunyi.PIT, 0x1234DE)

print("\ngelombang: KOTAK, bukan sinus (speaker cuma nyala/mati)")
w = bunyi.gelombang([(1000, 1)], rate=22050)
cek("hanya dua nilai berbeda", len(set(w)), 2)
cek("panjang ~ 1 tik", abs(len(w) - int(22050 / bunyi.TIK)) <= 1, True)
cek("frekuensi 0 = diam", set(bunyi.gelombang([(0, 1)])), {0})

print("\nskrip nyata: goal 1")
g = Archive(os.path.join(D, "GRAPH")); an = Archive(os.path.join(D, "ANIMATE"))
cs = contrap.parse(os.path.join(D, "CONTRAP"))
r = Rng(0); pick.loadcon_pick(r, len(cs[1])); var = cs[1][0]
jz = [t for (y, x, t) in var["zany"]]; tz = pick.tabel(g, jz)
n_not = 0
for i in pick.pickpart(r, tz, jz, sub=1):
    nodes, _ = skrip.muat(tz[i], an)
    for t in nodes:
        if t[0] == "op04":
            n_not += len(bunyi.not_dari(t[1], t[2])[0])
cek("ada not terdekode", n_not > 0, True)
print("     (%d not dari skrip goal 1)" % n_not)

print()
if gagal:
    for x in gagal:
        print("  GAGAL:", x)
    sys.exit(1)
print("SEMUA UJI BUNYI LULUS")
