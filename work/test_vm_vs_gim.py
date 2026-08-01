"""VM animasi diadu langsung dengan keadaan bola gim asli.

Yang dibandingkan BUKAN piksel melainkan keputusan mesinnya: ke mana bola
pergi, dan kapan penghapusan dilewati. Keduanya dibaca dari DGROUP saat gim
berjalan di emulator (`CC_VSWORD=25e,260,266` pada hook 0x26ae).

Rujukan dibuat dengan:
  CC_VSWORD=260,25e,264,266 CC_VRAMSEQ=26ae=<folder> python work/emu.py 1 2
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "port"))
from cc.core.archive import Archive                                  # noqa: E402
from cc.core import contrap, pick, skrip, vm                         # noqa: E402
from cc.core.rng import Rng                                          # noqa: E402

D = os.path.join(ROOT, "_ORIGINAL_READONLY")
JANGAN_HAPUS = 0x140            # prevx == 0x140 -> putmsk dilewati


def rantai(goal):
    g = Archive(os.path.join(D, "GRAPH"))
    m = Archive(os.path.join(D, "MECHS"))
    an = Archive(os.path.join(D, "ANIMATE"))
    cs = contrap.parse(os.path.join(D, "CONTRAP"))
    r = Rng(0)
    vi = pick.loadcon_pick(r, len(cs[goal]))
    var = cs[goal][vi]
    jz = [t for (y, x, t) in var["zany"]]
    tz = pick.tabel(g, jz)
    selz = pick.pickpart(r, tz, jz, sub=goal)
    jm = [t for (y, x, t) in var["mech"]]
    tm = pick.tabel(m, jm)
    selm = pick.fillans(tm, jm)
    parts = []
    cm = cz = 0
    for s in var["state"]:
        if s == -1:
            (y, x, _t) = var["mech"][cm]; tab, base, arc = tm, selm[cm], m; cm += 1
        else:
            (y, x, _t) = var["zany"][cz]; tab, base, arc = tz, selz[cz], g; cz += 1
        if base is None:
            continue
        p = vm.Part(y, x, tab, base, skrip.muat(tab[base], an)[0])
        p.arc = arc
        parts.append(p)
    return parts


def main(folder):
    G = json.load(open(os.path.join(folder, "globals.json")))
    V = vm.VM(rantai(1))
    pos = flag = tot = 0
    beda = []
    k = 1
    while k < len(G):
        e = V.langkah()
        if e is None or e[0] in ("selesai", "belum"):
            break
        if e[0] != "bola":
            continue
        tot += 1
        pos += (e[1], e[2]) == (G[k]["w25e"], G[k]["w260"])
        gf = G[k]["w266"] == JANGAN_HAPUS
        pf = e[3] if len(e) > 3 else False
        flag += pf == gf
        if pf != gf and len(beda) < 5:
            beda.append((k, pf, gf))
        k += 1
    print("  posisi bola   : %d/%d" % (pos, tot))
    print("  bendera hapus : %d/%d" % (flag, tot))
    for b in beda:
        print("    frame %d: port=%s gim=%s" % b)
    # frame 1 sah berbeda: itu keadaan AWAL prevx=0x140 dari setupscr
    ok = pos == tot and flag >= tot - 1
    print("\n%s" % ("VM COCOK DENGAN GIM" if ok else "VM TIDAK COCOK"))
    return 0 if ok else 1


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else None
    if not f or not os.path.isdir(f):
        print("pakai: python work/test_vm_vs_gim.py <folder CC_VRAMSEQ>")
        sys.exit(0)
    sys.exit(main(f))
