"""REGRESI LAYAR BERMAIN: seluruh layar diadu piksel dgn VRAM game asli.

Yang diuji termasuk bagian yang selama ini KARANGAN PORT dan tidak pernah
diukur:

    pita atas      setupscr(mode=2, sub) + ikon bola + f171f()
    pita bawah     setupscr -> BIRU TUA (bukan cyan), plus strip drawpal()
    kotak slot     drawslot(): slot KOSONG = fillrect(x+1, y, x+0x1e, y+0x17, 3)
                   -- PETAK PENUH warna 3, bukan kotak bergaris berisi huruf

⭐ ARENA IKUT DIADU, jadi yang diukur SELURUH 64.000 piksel layar.

Itu baru mungkin sesudah rantai RNG-nya disamakan, dan yang menghalanginya
BUKAN emulator melainkan model port: `loadcon.c` mengundi varian dengan

    do { pick = rnd(cnt) + first; }
    while (lastgoal == sub && cnt >= 2 && pick == lastvar);

Memuat goal yang SAMA dua kali berturut memaksa pengulangan, dan pengulangan
itu MEMAJUKAN seed satu undian lagi sehingga seluruh pemilihan part sesudahnya
ikut bergeser. `adegan.susun()` dulu tidak memodelkannya.

Uji ini karena itu menjalankan emulator DUA kali dengan urutan tombol yang
sama (emulatornya deterministik):

    lari A  CC_VRAMSEQ=5035  -> seed @0x71a, lastgoal @0x1e2e, lastvar @0x1e30
                               pada panggilan `loadcon` terakhir
    lari B  CC_VRAMSEQ=3c4e  -> layar bermainnya sendiri + nmech/sel/idtab/base

lalu memberi keadaan itu ke `susun()`. Memaksa `VARIANT=` lewat emulator TIDAK
bisa dipakai sebagai jalan pintas -- hook itu memaksa SEMUA rnd() di dalam
loadcon, dan gelung do/while di atas jadi tak berujung (gejalanya "0 frame").
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


def tangkap_rng(folder):
    """Lari KEDUA, urutan tombol sama: keadaan RNG tiap `loadcon`."""
    seq = os.path.join(folder, "loadcon")
    if not (os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json"))):
        print("  [emu] menangkap keadaan RNG ...")
        env = dict(os.environ)
        env.update(CC_OUT=os.path.join(folder, "out_rng"), OBSERVE="fillmech",
                   CC_NOSKIP="1", CC_MAXINSN="300000000", CC_OBSKEYS=TOMBOL,
                   CC_VRAMSEQ="5035=%s:10" % seq,
                   CC_VSWORD="71a,3b2,1e2e,1e30")
        subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                        str(GOAL), "2"], env=env, cwd=AKAR,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    G = json.load(open(os.path.join(seq, "globals.json")))
    r = G[-1]                      # loadcon TERAKHIR = yang memuat layar ini
    return r["w71a"], r["w1e2e"], r["w1e30"]


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

    # Keadaan RNG gim, dibaca dari memorinya -- BUKAN varian yang dipaksakan.
    # Dgn seed + lastgoal + lastvar yang sama, `susun()` harus mengundi varian
    # DAN part yang sama seperti gim, jadi arenanya ikut bisa diadu.
    seed, lastgoal, lastvar = tangkap_rng(folder)
    print("  keadaan RNG gim: seed=%04x lastgoal=%d lastvar=%d"
          % (seed, lastgoal, lastvar))

    var, _parts, fb = adegan.susun(GOAL, g, m, mi, an, cs, seed=seed, mode=2,
                                   sub=GOAL, isi=False, nbola=1,
                                   lastgoal=lastgoal, lastvar=lastvar)
    # silang-periksa: varian yang diundi port harus sama dgn `base` milik gim
    jenis_gim = sorted({r["id"] for r in base})
    cek("varian hasil undian port = varian gim",
        sorted({t for (_y, _x, t) in var["mech"]}), jenis_gim)
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
    a, b = wilayah(8, 159)
    cek("ARENA (kontraption + slot)", a, b)
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
    a, b = wilayah(0, 199)
    cek("SELURUH LAYAR", a, b)

    print("\n%s" % ("LAYAR BERMAIN IDENTIK DENGAN GAME ASLI" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "playseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
