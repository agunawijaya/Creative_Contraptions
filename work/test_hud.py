"""Uji lima padanan fungsi gim asli: showsc, timedrw, showhint, prompts, pickmax.

Yang diperiksa bukan "tidak error" melainkan ATURANNYA: nilai skor, cabang
mana yang aktif, dan teks apa yang keluar -- semuanya dibandingkan dengan
apa yang tertulis di src_c.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port"))
from cc.core import hud, render as rend                       # noqa: E402
from cc.core.archive import Archive                           # noqa: E402
from cc.core.rng import Rng                                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gagal = []


def cek(nama, dapat, harap):
    if dapat != harap:
        gagal.append("%s: dapat %r, harap %r" % (nama, dapat, harap))
    print("  %-46s %s" % (nama, "OK" if dapat == harap else "GAGAL"))


print("skor: nol harfiah di ujung format -> tampil x10")
cek("skor_teks(0)", hud.skor_teks(0).strip(), "00")
cek("skor_teks(10000) = satu kontraption sempurna", hud.skor_teks(10000).strip(), "100000")
cek("skor_teks(2500) = tiga kesalahan atau lebih", hud.skor_teks(2500).strip(), "25000")

print("\nskor_akhir: SATU penilaian per kontraption, dan HANYA mode 4")
for mode in (0, 1, 2, 3):
    cek("mode %d tidak berskor" % mode, hud.skor_akhir(0, 0, mode, 1, 1, 0, 0, 1)[2], False)
cek("mode 4 berskor", hud.skor_akhir(0, 0, 4, 1, 1, 0, 0, 1)[2], True)
cek("zcnt=0 -> +10000", hud.skor_akhir(0, 0, 4, 1, 1, 0, 0, 1)[0], 10000)
cek("zcnt=1 -> +5000", hud.skor_akhir(0, 1, 4, 1, 1, 0, 0, 1)[0], 5000)
cek("zcnt=2 -> +2500", hud.skor_akhir(0, 2, 4, 1, 1, 0, 0, 1)[0], 2500)
cek("zcnt=9 -> +2500 (default)", hud.skor_akhir(0, 9, 4, 1, 1, 0, 0, 1)[0], 2500)
cek("Master: + cur2*1000", hud.skor_akhir(0, 0, 4, 2, 1, 3, 0, 1)[0], 10000 + 3000)
cek("goal 6: + (bola-1)*2500", hud.skor_akhir(0, 0, 4, 1, 6, 0, 0, 4)[0], 10000 + 3 * 2500)
cek("goal 6 Master: + sisa_waktu*100", hud.skor_akhir(0, 0, 4, 2, 6, 0, 0x140, 1)[0],
    10000 + 0 + 0x140 * 100)
cek("goal 6 menyetel bola kembali 1", hud.skor_akhir(0, 0, 4, 1, 6, 0, 0, 4)[1], 1)

print("\ntimedrw: tx = waktu TERSISA; cabang kedua = pengisian AWAL")
fb = rend.new_fb()
k = rend.KanvasFB(fb)
cek("mode 2 tidak menggambar", hud.timedrw(k, 200, 2), False)
cek("tx=0x140 (awal) -> pengisian", hud.timedrw(k, 0x140, 4), True)
cek("tx=200 -> gambar biasa", hud.timedrw(k, 200, 4), False)
cek("timebar mengurangi tx", hud.timebar(k, 200, 4), 199)
cek("timebar diam di mode lain", hud.timebar(k, 200, 2), 200)

print("\nprompts: cabang & teks dari DGROUP")
def teks_terpakai(mode, sub, gagal_, lvl, nbola):
    fb2 = rend.new_fb()
    k2 = rend.KanvasFB(fb2)
    hud.prompts(k2, mode, sub, gagal_, lvl, nbola)
    return sum(1 for baris in fb2 for c in baris if c != rend.BG)

cek("mode 0 tanpa GREAT!", teks_terpakai(0, 1, 0, 1, 1) > 0, True)
cek("gagal -> ada teks", teks_terpakai(2, 1, 1, 1, 1) > 0, True)
cek("mode 4 tuntas -> bola disetel 0",
    hud.prompts(rend.KanvasFB(rend.new_fb()), 4, 6, 0, 1, 1), 0)
cek("mode 2 biasa -> bola tak berubah",
    hud.prompts(rend.KanvasFB(rend.new_fb()), 2, 1, 0, 1, 1), 1)

print("\nshowhint: hanya mode 4, spanduk MISC record 19")
misc = Archive(os.path.join(ROOT, "_ORIGINAL_READONLY", "MISC"))
cek("mode 2 tidak menggambar", hud.showhint(rend.KanvasFB(rend.new_fb()), misc, 2), False)
cek("mode 4 menggambar", hud.showhint(rend.KanvasFB(rend.new_fb()), misc, 4), True)
cek("record 19 berukuran 104x7", (misc.recs[hud.HINT_REC]["w"], misc.recs[hud.HINT_REC]["h"]),
    (104, 7))

print("\npickmax: count dikurangi SEBELUM gelung")
r = Rng(0)
best, cnt = hud.pickmax(r, 4, 0x12C)
cek("count 4 -> 3", cnt, 3)
cek("best dalam jangkauan", 0 <= best < 0x12C, True)
cek("count 1 -> 0, tanpa undian", hud.pickmax(Rng(0), 1, 10), (-1000, 0))

print("\nkedip_pita: XOR dua kali kembali seperti semula")
fb3 = rend.new_fb()
rend.fillrect(fb3, 0, 0, 319, 7, 3)
asli = [b[:] for b in fb3]
k3 = rend.KanvasFB(fb3)
hud.kedip_pita(k3)
berubah = fb3 != asli
hud.kedip_pita(k3)
cek("sekali XOR mengubah", berubah, True)
cek("dua kali XOR memulihkan", fb3 == asli, True)

print()
if gagal:
    print("GAGAL %d:" % len(gagal))
    for g in gagal:
        print("  ", g)
    sys.exit(1)
print("SEMUA UJI HUD LULUS")
