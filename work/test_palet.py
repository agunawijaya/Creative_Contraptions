"""REGRESI STRIP PALET: petak pemilih part diadu piksel dgn VRAM game asli.

Menguji `port/cc/core/palet.py` (`drawpal()` @0x3B83) dan
`port/cc/core/pick.py` (`palet_mekanisme()` = `mkpal()` @0x3909) di DUA mode,
karena aturannya memang berbeda per mode:

    Fill in Mechanisms (lvl3 == 1)  hanya part yang DIBUTUHKAN kontraption
    Contraption Mix Up (lvl3 == 3)  SELURUH daftar, dikocok lalu dedup

Tangkapan dibuat sendiri lewat emulator. Dua saklar yang WAJIB, dan keduanya
pernah membuat pengukuran ini dikira mustahil:

  * `CC_NOSKIP=1` -- bawaan `work/emu.py` mem-bypass gelung penempatan part
    (`hook_2e90`), dan `drawpal()` hidup DI DALAM gelung itu;
  * urutan tombol TANPA ESC -- urutan bawaan mode mixup diakhiri 0x1B, yang
    membuat `runplay()` mengembalikan -1 sebelum strip sempat digambar.

Titik tangkapnya alamat RET `drawpal` (0x3C4E), BUKAN alamat masuknya: di
alamat masuk yang terlihat selalu keadaan SEBELUM ia menggambar.

⭐ `idtab[]` @0x2ea MENGINDEKS `base`, bukan direktori arsip. Dan `base` itu
sendiri berbeda menurut mode -- `main_.c` memanggil
`loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`:

    lvl3 == 1  -> tabel DISARING + DIPADATKAN (hanya jenis yang dipakai)
    lvl3 != 1  -> direktori PENUH

Karena itu uji ini MEMBACA `base` milik gim (`CC_VSPTR=73a:...`) dan
memetakannya balik ke record arsip lewat offset datanya, alih-alih menebak
varian mana yang kebetulan diundi emulator.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import palet, pick, render as rend                # noqa: E402
from cc.core.archive import Archive                            # noqa: E402
from cc.core.rng import Rng                                    # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(AKAR, "_ORIGINAL_READONLY")
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
TOMBOL = ",".join(["0d"] * 12)          # TANPA ESC -- lihat catatan modul
N_BASE = 40                             # record `base` yang dibuang (12 byte each)

# (nama, OBSERVE, goal, mode emu, lvl3 yang diharapkan)
KASUS = [("Fill in Mechanisms", "fillmech", 1, 2, 1),
         ("Contraption Mix Up", "mixup", 1, 4, 3)]


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def tangkap(folder, obs, goal, mode):
    seq = os.path.join(folder, obs)
    if os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json")):
        return seq
    print("  [emu] menangkap %s ..." % obs)
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out_" + obs), OBSERVE=obs,
               CC_NOSKIP="1", CC_MAXINSN="300000000", CC_OBSKEYS=TOMBOL,
               CC_VRAMSEQ="3c4e=%s:4" % seq,
               CC_VSWORD="3ac,51c,738", CC_VSMEM="2ea:20",
               CC_VSPTR="73a:%d" % (N_BASE * 12))
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(goal), str(mode)], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def base_gim(mentah, arc):
    """Byte `base` -> daftar record ARSIP, dipetakan lewat offset datanya."""
    per_off = {r["off"]: r for r in arc.recs}
    out = []
    for i in range(len(mentah) // 12):
        q = mentah[i * 12:i * 12 + 12]
        if q[0] == 0:                               # id 0 = akhir tabel
            break
        off = int.from_bytes(q[8:12], "little")
        r = per_off.get(off)
        if r is None:
            return None
        out.append(r)
    return out


def uji(folder, nama, obs, goal, mode, lvl3_harap, mechs):
    seq = tangkap(folder, obs, goal, mode)
    gpath = os.path.join(seq, "globals.json")
    G = json.load(open(gpath)) if os.path.exists(gpath) else []
    if not G:
        print("  %-20s : emulator tidak pernah mencapai drawpal" % nama)
        return False, 0, 0

    nmech, lvl3 = G[0]["w3ac"], G[0]["w738"]
    idtab = bytes.fromhex(G[0]["mem2"])
    base = base_gim(bytes.fromhex(G[0]["mem"]), mechs)
    if base is None:
        print("  %-20s : `base` gim tak bisa dipetakan ke record arsip" % nama)
        return False, 0, 0

    # 1. tiruan mkpal() atas `base` yang SAMA harus memberi cacah yang sama
    jenis = sorted({r["id"] for r in base}) if lvl3 == 1 else []
    n_port = len(pick.palet_mekanisme(base, jenis, lvl3, Rng(0)))
    ok = (lvl3 == lvl3_harap) and (n_port == nmech)
    print("  %-20s : lvl3=%d(harap %d)  base=%2d rec  nmech gim=%2d port=%2d  %s"
          % (nama, lvl3, lvl3_harap, len(base), nmech, n_port,
             "OK" if ok else "BEDA"))

    # 2. piksel: gambar ulang petaknya lalu adu dgn tangkapan
    tot = beda = 0
    for r in G:
        sel = r["w51c"]
        ref = muat(os.path.join(seq, "f%04d.png" % r["frame"]))
        fb = rend.new_fb()
        for y in range(rend.H):
            fb[y] = ref[y][:]                       # latar dari rujukan...
        for i in range(palet.N_SEL):                # ...petaknya dikosongkan
            x = palet.SEL_X0 - i * palet.SEL_W
            for yy in range(palet.SEL_Y, palet.SEL_Y + palet.SEL_H):
                for xx in range(x, x + palet.SEL_W):
                    fb[yy][xx] = 1
        palet.drawpal(rend.KanvasFB(fb), sel,
                      lambda i: (mechs, base[idtab[i]]), nmech)
        for i in range(palet.N_SEL):
            x = palet.SEL_X0 - i * palet.SEL_W
            for yy in range(palet.SEL_Y, palet.SEL_Y + palet.SEL_H):
                for xx in range(x, x + palet.SEL_W):
                    tot += 1
                    beda += fb[yy][xx] != ref[yy][xx]
    print("  %-20s   %d frame, %d/%d piksel %s"
          % ("", len(G), tot - beda, tot, "COCOK" if not beda else "BEDA"))
    return ok and not beda, tot - beda, tot


def main(folder):
    mechs = Archive(D + "/MECHS")
    semua = True
    OK = TOT = 0
    for nama, obs, goal, mode, lvl3 in KASUS:
        ok, a, b = uji(folder, nama, obs, goal, mode, lvl3, mechs)
        semua = semua and ok
        OK += a
        TOT += b
    print("\n  TOTAL %d/%d piksel strip" % (OK, TOT))
    print("\n%s" % ("STRIP PALET COCOK DI KEDUA MODE" if semua
                    else "ADA YANG BELUM COCOK"))
    return 0 if semua else 1


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "palseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
