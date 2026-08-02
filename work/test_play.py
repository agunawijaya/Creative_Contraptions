"""REGRESI LAYAR BERMAIN: seluruh layar diadu piksel dgn VRAM game asli.

KETIGA mode bermain diuji, dan aturannya memang berbeda di tiap mode:

    Fill in Mechanisms  slot mekanisme = PETAK ABU (fillrect warna 3),
                        objek zany utuh, ada baris pesan cyan
    Fill in Zany        mekanisme utuh, objek zany TIDAK digambar sama sekali
                        (kecuali yang TERAKHIR -- itu gambar hasil goal),
                        TIDAK ada baris pesan
    Contraption Mix Up  keduanya tetap digambar; yang "kosong" adalah slot
                        BERTANDA, dan `pickpart()` memberinya record kelompok
                        kedua (id >= 0x80) -- sprite PENGGANTI. Ada baris
                        pesan, bilah timer, dan strip 13 pilihan.

Rantai RNG-nya juga berbeda, dan itu yang paling mudah salah. Antara
`loadcon()` dan `pickpart()` ada satu panggilan lagi yang memakai RNG:

    mode 2  tidak ada
    mode 3  setzany()   -- 2 x rnd(0xf) + rnd(1) + rnd(n-3) berulang
    mode 4  setmark()   -- rnd(1) + rnd(n-3) berulang, plus pickmax() sekali
                           saat mode dimasuki

Terukur dgn menghitung panggilan di emulator (CC_VRAMSEQ pada 0x10fd, 0x1200,
0x4e01): fillmech 0/0/0, zany 0/1/0, mixup 1/0/1.

Emulator dijalankan DUA kali per mode dengan urutan tombol yang sama
(emulatornya deterministik): lari A membaca keadaan RNG di `loadcon`, lari B
menangkap layarnya. Memaksa `VARIANT=` TIDAK bisa dipakai -- hook itu memaksa
SEMUA rnd() di dalam loadcon sehingga gelung do/while pemilih varian jadi tak
berujung (gejalanya "0 frame").

⚠ Kecocokan piksel di mode 3 TIDAK membuktikan rantai RNG-nya: yang tampak di
sana cuma mekanisme (dari `fillans()`, deterministik) dan objek zany terakhir
(dipaksa `row == sub`). Yang membuktikan rantai adalah mode 4, di mana seluruh
isi arena berasal dari undian.
"""
import json
import os
import subprocess
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import contrap, adegan, palet, hud, render as rend   # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(AKAR, "_ORIGINAL_READONLY")
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
TOMBOL = ",".join(["0d"] * 12)
GOAL = 1

# nama, OBSERVE, mode gim, offset tangkap, isi_mekanisme, isi_zany, ada strip
KASUS = [
    ("Fill in Mechanisms", "fillmech", 2, "3c4e", False, True, True),
    ("Fill in Zany",       "zany",     3, "42ca", True, False, False),
    ("Contraption Mix Up", "mixup",    4, "3c4e", True, True, True),
]

gagal = []


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def _emu(folder, nama, obs, mode, env_extra):
    seq = os.path.join(folder, nama)
    if os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json")):
        return seq
    print("  [emu] menangkap %s ..." % nama)
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out_" + nama), OBSERVE=obs,
               CC_NOSKIP="1", CC_MAXINSN="300000000", CC_OBSKEYS=TOMBOL)
    env.update(env_extra)
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(GOAL), str(mode)], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def tangkap_layar(folder, obs, mode, off):
    seq = _emu(folder, obs + "_layar", obs, mode, {
        "CC_VRAMSEQ": "%s=%s:2" % (off, os.path.join(folder, obs + "_layar")),
        "CC_VSWORD": "3ac,51c,738,718,7ee",
        "CC_VSMEM": "2ea:20", "CC_VSPTR": "73a:480"})
    return json.load(open(os.path.join(seq, "globals.json"))), seq


def tangkap_rng(folder, obs, mode):
    seq = _emu(folder, obs + "_rng", obs, mode, {
        "CC_VRAMSEQ": "5035=%s:10" % os.path.join(folder, obs + "_rng"),
        "CC_VSWORD": "71a,3b2,1e2e,1e30"})
    G = json.load(open(os.path.join(seq, "globals.json")))
    r = G[-1]
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
    print("    %-30s %7s/%-7s %s" % (nama, dapat, harap, "OK" if ok else "GAGAL"))


def uji_mode(folder, nama, obs, mode, off, isi, isiz, ada_strip, arc):
    g, m, mi, an, cs = arc
    G, seq = tangkap_layar(folder, obs, mode, off)
    if not G:
        print("  %s: emulator tidak mencapai titik tangkap" % nama)
        gagal.append(nama)
        return
    r0 = G[0]
    ref = muat(os.path.join(seq, "f%04d.png" % r0["frame"]))
    seed, lastgoal, lastvar = tangkap_rng(folder, obs, mode)
    print("  %s  (seed=%04x lastgoal=%d lastvar=%d)" % (nama, seed, lastgoal, lastvar))

    var, _p, fb, _pil = adegan.susun_lengkap(
        GOAL, g, m, mi, an, cs, seed=seed, mode=mode, sub=GOAL,
        isi=isi, isi_zany=isiz, nbola=r0["w718"],
        lastgoal=lastgoal, lastvar=lastvar, lvl=1)
    k = rend.KanvasFB(fb)
    if not isi:
        rend.drawslot(k, [(y, x) for (y, x, _t) in var["mech"]])
    if ada_strip:
        idtab = bytes.fromhex(r0["mem2"])
        base = (base_gim(bytes.fromhex(r0["mem"]), m)
                if r0["w738"] == 1 else m.recs)
        palet.drawpal(k, r0["w51c"],
                      lambda i: (m, base[idtab[i]]), r0["w3ac"])
    if mode == 4:
        hud.timedrw(k, r0["w7ee"], 4, r0["w718"], GOAL)

    beda = sum(1 for y in range(200) for x in range(320) if fb[y][x] != ref[y][x])
    cek("SELURUH LAYAR", 64000 - beda, 64000)


def uji_interaktif(folder, arc):
    """Jalur PEMAIN SUNGGUHAN: main.Game + key(), bukan hanya modul inti.

    Aturan kerja proyek ini menuntut uji lewat jalur user. Ini yang dulu
    menangkap bug palet dikocok DUA KALI -- jalur modul inti tidak lewat
    main.py sama sekali dan memberi 64.000/64.000 sementara jalur pemain
    meleset 738 piksel.
    """
    import pygame
    from cc import assets, cga
    from cc.core import palet as _pal
    import main as portmain

    G, seq = tangkap_layar(folder, "fillmech", 2, "3c4e")
    ref = muat(os.path.join(seq, "f%04d.png" % G[0]["frame"]))
    seed, lastgoal, lastvar = tangkap_rng(folder, "fillmech", 2)

    pygame.init()
    asli = _pal.penunjuk
    _pal.penunjuk = lambda *a, **k: None       # penunjuk sedang di fase padam
    try:
        g = portmain.Game(assets.find_data_dir())
        g.rng_seed, g.lastgoal, g.lastvar = seed, lastgoal, lastvar
        g.key(pygame.K_RETURN)                 # TITLE -> MENU
        g.key(pygame.K_DOWN)                   # sel 1 = Fill in Mechanisms
        g.key(pygame.K_RETURN)                 # -> LEVEL
        g.key(pygame.K_RETURN)                 # Apprentice -> INSTRUKSI (menu9)
        g.key(pygame.K_RETURN)                 # ENTER -> GOAL
        g.sel = g.goal_ids.index(GOAL)
        g.key(pygame.K_RETURN)                 # -> PLAY
        # keadaan yang berubah menurut waktu/interaksi, bukan aturan gambar
        g.cur_slot, g.message, g.cur_part = -1, "", G[0]["w51c"]
        fb = cga.make_framebuffer()
        g.draw(fb)
        beda = sum(1 for y in range(200) for x in range(320)
                   if PALET[fb.get_at((x, y))[:3]] != ref[y][x])
        pygame.image.save(fb, os.path.join(AKAR, "work", "play_port.png"))
    finally:
        _pal.penunjuk = asli
        pygame.quit()
    cek("SELURUH LAYAR", 64000 - beda, 64000)


def main(folder):
    arc = (Archive(D + "/GRAPH"), Archive(D + "/MECHS"), Archive(D + "/MISC"),
           Archive(D + "/ANIMATE"), contrap.parse(D + "/CONTRAP"))
    for nama, obs, mode, off, isi, isiz, strip in KASUS:
        uji_mode(folder, nama, obs, mode, off, isi, isiz, strip, arc)
    print("  Fill in Mechanisms lewat JALUR PEMAIN")
    uji_interaktif(folder, arc)
    print("\n%s" % ("LAYAR BERMAIN IDENTIK DENGAN GAME ASLI (3 mode)"
                    if not gagal else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "playseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
