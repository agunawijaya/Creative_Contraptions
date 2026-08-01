"""REGRESI LAYAR BERMAIN: chrome-nya diadu piksel dgn VRAM game asli.

Yang diuji di sini adalah bagian layar bermain yang selama ini KARANGAN PORT
dan tidak pernah diukur:

    pita atas      setupscr(mode=2, sub) + ikon bola + f171f()
    pita bawah     setupscr -> BIRU TUA (bukan cyan), plus strip drawpal()
    kotak slot     drawslot(): slot KOSONG = fillrect(x+1, y, x+0x1e, y+0x17, 3)
                   -- PETAK PENUH warna 3, bukan kotak bergaris berisi huruf

Arena (y 8..159) sengaja TIDAK diadu di sini: isinya bergantung pada undian
`pickpart()`, dan keadaan RNG emulator pada tangkapan ini bukan seed 0. Jalur
render arenanya sendiri sudah terbukti di tempat lain -- `work/genscreens.py
--verifikasi` (197/197 blit) dan `work/test_anim_vs_gim.py` (1.210/1.210
bingkai). Yang belum pernah diukur, dan diukur di sini, adalah chrome-nya.

Varian struktur TIDAK ditebak: ia dibaca dari tabel `base` milik gim
(`CC_VSPTR=73a:`), lalu dicocokkan ke varian CONTRAP lewat daftar jenis
mekanismenya. Memaksa `VARIANT=` lewat emulator TIDAK bisa dipakai -- hook itu
memaksa SEMUA rnd() di dalam loadcon, dan gelung
`do { pick = rnd(cnt) } while (... pick == lastvar)` jadi tak berujung.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import contrap, adegan, palet, render as rend     # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(AKAR, "_ORIGINAL_READONLY")
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
TOMBOL = ",".join(["0d"] * 12)
GOAL = 1

gagal = []


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def tangkap(folder):
    seq = os.path.join(folder, "play")
    if os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json")):
        return seq
    print("  [emu] menangkap layar bermain ...")
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out"), OBSERVE="fillmech",
               CC_NOSKIP="1", CC_MAXINSN="300000000", CC_OBSKEYS=TOMBOL,
               CC_VRAMSEQ="3c4e=%s:2" % seq, CC_VSWORD="3ac,51c,738",
               CC_VSMEM="2ea:20", CC_VSPTR="73a:480")
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(GOAL), "2"], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def base_gim(mentah, arc):
    per_off = {r["off"]: r for r in arc.recs}
    out = []
    for i in range(len(mentah) // 12):
        q = mentah[i * 12:i * 12 + 12]
        if q[0] == 0:
            break
        out.append(per_off[int.from_bytes(q[8:12], "little")])
    return out


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-34s %7s/%-7s %s" % (nama, dapat, harap, "OK" if ok else "GAGAL"))


def main(folder):
    g = Archive(D + "/GRAPH")
    m = Archive(D + "/MECHS")
    mi = Archive(D + "/MISC")
    an = Archive(D + "/ANIMATE")
    cs = contrap.parse(D + "/CONTRAP")

    seq = tangkap(folder)
    gp = os.path.join(seq, "globals.json")
    G = json.load(open(gp)) if os.path.exists(gp) else []
    if not G:
        print("  emulator tidak pernah mencapai drawpal")
        return 1
    nmech, sel = G[0]["w3ac"], G[0]["w51c"]
    idtab = bytes.fromhex(G[0]["mem2"])
    base = base_gim(bytes.fromhex(G[0]["mem"]), m)
    ref = muat(os.path.join(seq, "f%04d.png" % G[0]["frame"]))

    # varian struktur DIBACA dari `base`, bukan ditebak
    jenis_gim = sorted({r["id"] for r in base})
    vi = None
    for i, v in enumerate(cs.get(GOAL) or []):
        if sorted({t for (_y, _x, t) in v["mech"]}) == jenis_gim:
            vi = i
            break
    if vi is None:
        print("  varian gim (jenis %s) tak ditemukan di CONTRAP" % jenis_gim)
        return 1
    print("  varian gim = %d (jenis mekanisme %s)" % (vi, jenis_gim))

    var, _parts, fb = adegan.susun(GOAL, g, m, mi, an, cs, mode=2, sub=GOAL,
                                   isi=False, varian=vi, nbola=1)
    k = rend.KanvasFB(fb)
    rend.drawslot(k, [(y, x) for (y, x, _t) in var["mech"]])
    palet.drawpal(k, sel, lambda i: (m, base[idtab[i]]), nmech)

    def wilayah(y0, y1):
        n = (y1 - y0 + 1) * 320
        b = sum(1 for y in range(y0, y1 + 1) for x in range(320)
                if fb[y][x] != ref[y][x])
        return n - b, n

    a, b = wilayah(0, 7)
    cek("pita atas (setupscr + ikon bola)", a, b)
    a, b = wilayah(160, 199)
    cek("pita bawah (setupscr + strip)", a, b)

    tot = ok = 0
    for (y, x, _t) in var["mech"]:
        # `fillrect(x+1, y, x+0x1e, y+0x17, 3)` INKLUSIF di kedua ujung:
        # 24 baris x 30 kolom = 720 piksel per slot.
        n = (rend.SLOT_H + 1) * rend.SLOT_W
        d = sum(1 for yy in range(y, y + rend.SLOT_H + 1)
                for xx in range(x + 1, x + 1 + rend.SLOT_W)
                if fb[yy][xx] != ref[yy][xx])
        tot += n
        ok += n - d
    cek("kotak slot KOSONG (drawslot)", ok, tot)

    print("\n%s" % ("CHROME LAYAR BERMAIN COCOK" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "playseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
