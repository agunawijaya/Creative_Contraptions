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
import struct
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
GOAL = 1                      # goal untuk uji JALUR PEMAIN (satu saja, mahal)
# ⚠ Ketiga mode dulu hanya diadu untuk goal 1. "Jalur kodenya sama untuk goal
# lain" itu ARGUMEN, bukan pengukuran -- dan di berkas ini justru sudah
# terbukti dua kali bahwa satu jalur yang sama bisa meleset di kasus lain
# (lihat catatan mode 3 vs mode 4 di kepala berkas). Sekarang keenamnya diadu.
SEMUA_GOAL = (1, 2, 3, 4, 5, 6)
# ⚠ SUMBU LEVEL. Selama ini SEMUA kasus di berkas ini berjalan di Apprentice
# (`lvl=1`), dan itu bukan sekadar beda angka batas -- `lvl` mengubah JALAN
# KODE:
#   setmark():  lim = rnd(1) + (easy == 1 ? 1 : 3)   -> Master menandai lebih
#               banyak slot, dan tiap tanda menggeser rantai undian sesudahnya
#   pickpart(): lvl2 = 2 di Master, jadi mode 2 dan 3 ikut masuk cabang
#               `lvl2 == 2 && mark[i]` -- cabang yang sebelumnya HANYA pernah
#               dieksekusi lewat Contraption Mix Up
SEMUA_LEVEL = (1, 2)                       # 1 = Apprentice, 2 = Master Builder

# nama, OBSERVE, mode gim, offset tangkap, isi_mekanisme, isi_zany, ada strip,
# goal yang diuji
#
# ⚠ Contraption Mix Up hanya goal 1, dan itu BUKAN kemalasan: mode itu memang
# tidak memakai pemilih goal sama sekali (`main_.c` case 4 memasang
# `sub = 0; goal = 6;` lalu `sub++` tiap ronde). Terukur: `sub` @0x3b2
# tercatat **1** untuk argumen goal 1, 2, 3, dan 4 -- argumen itu tidak
# berpengaruh. Menjalankannya untuk enam goal hanya akan mengulang layar yang
# SAMA enam kali dan terlihat seperti cakupan yang tidak ada.
KASUS = [
    ("Fill in Mechanisms", "fillmech", 2, "3c4e", False, True, True, SEMUA_GOAL),
    ("Fill in Zany",       "zany",     3, "42ca", True, False, False, SEMUA_GOAL),
    ("Contraption Mix Up", "mixup",    4, "3c4e", True, True, True, (1,)),
]

gagal = []


def tandai_petunjuk(k, var, r0, mode, lvl):
    """Gambar ulang SATU huruf slot dgn warna `hintmark()` @0x4CD4.

    Penanda ini hanya ada di mode 4 level Master, dan itu sebabnya ia tak
    pernah terlihat sampai sumbu level disapu: `hintmark()` dibuka
    `if (mode != 4 || lvl != 2) return;`.

        na = postab[cur2].a ; nb = postab[cur2].b
        col = 2 ; if (tx >= range) col = 0 ; if (tx == best) col = 0
        text(&buf, nb, na, 1, 1, col)   ->  X = b, Y = a

    `col` tidak dihitung ulang di sini melainkan DIBACA lewat `mflag` @0x834,
    yang di gim disetel 1 tepat ketika `col == 0`. Alasannya sama seperti
    `sub` dan `lvl`: keadaan yang bisa dibaca jangan ditebak.
    """
    if mode != 4 or lvl != 2:
        return
    pos = var.get("pos") or []
    cur2 = r0.get("w7f8", -1)
    if not (0 <= cur2 < len(pos)):
        return
    a, b = pos[cur2]
    k.teks(chr(0x41 + cur2), b, a, 0 if r0.get("w834") else 2)


def hapus_penanda_lama(k, r0, prev):
    """Jejak penghapusan penanda RONDE SEBELUMNYA — artefak gim 1985.

    `hintmark()` memindahkan penanda dgn menghapus huruf LAMA lebih dulu:

        if (prev <= nmax) { buf = prev + 'A'; text(&buf, ob, oa, 1, 1, 3); }

    Dua hal membuat ini terlihat, dan keduanya baru muncul saat sumbu LEVEL
    dan RENTETAN RONDE disapu bersamaan:

    1. `postab` @0x3b6 adalah array GLOBAL yang `loadcon()` hanya timpa
       sebanyak entri kontraption yang sedang dimuat. Entri sisanya masih
       berisi koordinat RONDE SEBELUMNYA.
    2. Penjaganya `prev <= nmax`, bukan `<`. Jadi `prev == nmax` LOLOS dan
       membaca entri yang sudah di luar jangkauan.

    Terukur di ronde sub=4 Master: `prev` = 10 (cur2 ronde sebelumnya),
    `nmax` = 10, dan `postab[10]` masih berisi (142, 90) dari ronde ke-3 --
    tepat tempat huruf 'K' liar muncul di layar gim. Bukan tebakan: postab
    hidupnya dibaca dari memori gim, dan `prev` dari tangkapan ronde
    sebelumnya.
    """
    if prev is None:
        return
    if prev > r0.get("w3b4", 0):          # `prev <= nmax`, perhatikan <=
        return
    d = bytes.fromhex(r0.get("mem3") or "")
    if len(d) < (prev + 1) * 4:
        return
    a, b = struct.unpack_from("<hh", d, prev * 4)
    k.teks(chr(0x41 + prev), b, a, 3)


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def _emu(folder, nama, obs, mode, env_extra, goal=GOAL, level=1):
    seq = os.path.join(folder, nama)
    if os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json")):
        return seq
    print("  [emu] menangkap %s ..." % nama)
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out_" + nama), OBSERVE=obs,
               CC_NOSKIP="1", CC_MAXINSN="300000000", CC_OBSKEYS=TOMBOL,
               CC_LEVEL=str(level))
    env.update(env_extra)
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(goal), str(mode)], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def tangkap_layar(folder, obs, mode, off, goal, level=1):
    nm = "%s_layar_g%d_l%d" % (obs, goal, level)
    seq = _emu(folder, nm, obs, mode, {
        "CC_VRAMSEQ": "%s=%s:2" % (off, os.path.join(folder, nm)),
        # 734 = `lvl`. DIBACA, tidak dianggap sama dgn CC_LEVEL yang diminta --
        # aturan yang sama seperti `sub` @0x3b2 di Contraption Mix Up.
        # 7f8 = cur2 (slot yang ditandai hintmark), 834 = mflag (0 -> warna 2,
        # 1 -> warna 0). Keduanya hanya hidup di mode 4 level Master.
        "CC_VSWORD": "3ac,51c,738,718,7ee,3b2,734,7f8,834",
        "CC_VSMEM": "2ea:20", "CC_VSPTR": "73a:480"}, goal, level)
    return json.load(open(os.path.join(seq, "globals.json"))), seq


def tangkap_rng(folder, obs, mode, goal, level=1):
    nm = "%s_rng_g%d_l%d" % (obs, goal, level)
    seq = _emu(folder, nm, obs, mode, {
        "CC_VRAMSEQ": "5035=%s:10" % os.path.join(folder, nm),
        "CC_VSWORD": "71a,3b2,1e2e,1e30,734"}, goal, level)
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


def uji_mode(folder, nama, obs, mode, off, isi, isiz, ada_strip, arc, goal=GOAL,
             level=1):
    g, m, mi, an, cs = arc
    nama = "%s g%d %s" % (nama, goal,
                          "Apprentice" if level == 1 else "Master")
    G, seq = tangkap_layar(folder, obs, mode, off, goal, level)
    if not G:
        print("  %s: emulator tidak mencapai titik tangkap" % nama)
        gagal.append(nama)
        return
    r0 = G[0]
    ref = muat(os.path.join(seq, "f%04d.png" % r0["frame"]))
    seed, lastgoal, lastvar = tangkap_rng(folder, obs, mode, goal, level)
    # `sub` DIBACA dari gim, tidak dianggap sama dengan argumen goal -- di
    # Contraption Mix Up keduanya memang berbeda.
    sub = r0.get("w3b2", goal)
    lvl = r0.get("w734", level)            # DIBACA dari gim, bukan diasumsikan
    if lvl != level:
        gagal.append("%s: gim memakai lvl %d, diminta %d" % (nama, lvl, level))
    print("  %s  (seed=%04x sub=%d lvl=%d lastgoal=%d lastvar=%d)"
          % (nama, seed, sub, lvl, lastgoal, lastvar))

    var, _p, fb, _pil = adegan.susun_lengkap(
        sub, g, m, mi, an, cs, seed=seed, mode=mode, sub=sub,
        isi=isi, isi_zany=isiz, nbola=r0["w718"],
        lastgoal=lastgoal, lastvar=lastvar, lvl=lvl)
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
        hud.timedrw(k, r0["w7ee"], 4, r0["w718"], sub)
    tandai_petunjuk(k, var, r0, mode, lvl)

    beda = sum(1 for y in range(200) for x in range(320) if fb[y][x] != ref[y][x])
    cek("SELURUH LAYAR", 64000 - beda, 64000)


# Urutan tombol yang benar-benar MENYELESAIKAN satu ronde Mix Up.
# `pickloop()` @0x2E90: ENTER memajukan slot tanpa mengubah pilihan, SPACE di
# dalam `review()` mengembalikan `cur | 0x8000` -- nilai NEGATIF, jadi ia yang
# keluar dari gelung -- lalu SPACE kedua dibaca `clrbot()` (case 0x20 -> jalan).
# ⚠ ESC (0x1b) MEMBATALKAN ronde; urutan OBSERVE bawaan diakhiri ESC, dan
# itulah sebabnya `sub` @0x3b2 dulu tak pernah lewat dari 1: tiap ronde
# dibatalkan, mode 4 dimasuki lagi, `sub = 0` lalu `sub++`.
# ⚠ Panah TIDAK dipakai: mengubah pilihan berarti part benar-benar DITARUH,
# dan layar awal ronde berikutnya jadi tidak lagi keadaan awal.
TOMBOL_RONDE = ",".join((["0d"] * 3 + ["20", "20"]) * 10)


def uji_mixup_rentetan(folder, arc, level=1):
    """KEENAM ronde Contraption Mix Up, bukan hanya yang pertama.

    Mode 4 adalah RENTETAN: `main_.c` case 4 memasang `sub = 0; goal = 6;`
    lalu `sub++` tiap putaran. Lima kontraption sesudah yang pertama dulu tak
    pernah bisa diadu -- `hook_58c9` menghentikan emulasi tepat sesudah
    animasi ronde pertama. `CC_NOSTOP=1` kini membiarkannya jalan terus.

    Dua lari (emulatornya deterministik): satu membaca keadaan RNG di tiap
    `loadcon()`, satu menangkap layarnya. Dipasangkan lewat `sub` yang
    dicatat KEDUANYA -- bukan lewat urutan, karena `drawpal()` bisa terpanggil
    lebih dari sekali per ronde.
    """
    g, m, mi, an, cs = arc
    tag = "Apprentice" if level == 1 else "Master"
    env = dict(CC_NOSTOP="1", CC_NOWAIT="1", CC_OBSKEYS=TOMBOL_RONDE)
    nmS = "mixup_rentetan_l%d" % level
    nmL = "mixup_ronde_rng_l%d" % level
    seqS = _emu(folder, nmS, "mixup", 4, dict(
        env, CC_VRAMSEQ="3c4e=%s:8" % os.path.join(folder, nmS),
        CC_VSWORD="3ac,51c,738,718,7ee,3b2,730,732,734,7f8,834,3b4",
        # 3b6 = postab HIDUP milik gim, 12 entri -- termasuk entri di LUAR
        # jangkauan kontraption ini. Lihat `hapus_penanda_lama()`.
        CC_VSMEM="2ea:20,3b6:48", CC_VSPTR="73a:480"), GOAL, level)
    seqL = _emu(folder, nmL, "mixup", 4, dict(
        env, CC_VRAMSEQ="5035=%s:12" % os.path.join(folder, nmL),
        CC_VSWORD="71a,3b2,1e2e,1e30,718,734"), GOAL, level)
    S = json.load(open(os.path.join(seqS, "globals.json")))
    L = json.load(open(os.path.join(seqL, "globals.json")))
    uniq = []
    for r in S:                       # drawpal bisa >1x per ronde: ambil yang pertama
        if not uniq or uniq[-1]["w3b2"] != r["w3b2"]:
            uniq.append(r)
    per_off = {r["off"]: r for r in m.recs}
    for i, r0 in enumerate(uniq[:6]):
        lc = L[i + 1]
        sub = r0["w3b2"]
        if lc["w3b2"] != sub:         # penjajaran DIPERIKSA, bukan diasumsikan
            gagal.append("ronde %d: sub loadcon %d != layar %d"
                         % (i, lc["w3b2"], sub))
            continue
        skor = r0["w730"] | (r0["w732"] << 16)
        ref = muat(os.path.join(seqS, "f%04d.png" % r0["frame"]))
        var, _p, fb, _pil = adegan.susun_lengkap(
            sub, g, m, mi, an, cs, seed=lc["w71a"], mode=4, sub=sub,
            isi=True, isi_zany=True, nbola=r0["w718"],
            lastgoal=lc["w1e2e"], lastvar=lc["w1e30"],
            lvl=r0.get("w734", level))
        k = rend.KanvasFB(fb)
        idtab = bytes.fromhex(r0["mem2"])
        base = (base_gim(bytes.fromhex(r0["mem"]), m)
                if r0["w738"] == 1 else m.recs)
        palet.drawpal(k, r0["w51c"], lambda j: (m, base[idtab[j]]), r0["w3ac"])
        hud.timedrw(k, r0["w7ee"], 4, r0["w718"], sub)
        hud.judul_atau_skor(k, 4, sub, skor)
        hapus_penanda_lama(k, r0, uniq[i - 1].get("w7f8") if i else None)
        tandai_petunjuk(k, var, r0, 4, r0.get("w734", level))
        beda = sum(1 for y in range(200) for x in range(320)
                   if fb[y][x] != ref[y][x])
        cek("Mix Up %s ronde sub=%d (skor %d)" % (tag, sub, skor),
            64000 - beda, 64000)


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

    G, seq = tangkap_layar(folder, "fillmech", 2, "3c4e", GOAL)
    ref = muat(os.path.join(seq, "f%04d.png" % G[0]["frame"]))
    seed, lastgoal, lastvar = tangkap_rng(folder, "fillmech", 2, GOAL)

    pygame.init()
    asli = _pal.penunjuk
    _pal.penunjuk = lambda *a, **k: None       # penunjuk sedang di fase padam
    try:
        g = portmain.Game(assets.find_data_dir())
        # Alur pembuka gim: TITLE -> CREDITS -> SET UP (dua Y/N) -> MENU.
        g.key(pygame.K_RETURN)                 # TITLE -> CREDITS
        g.key(pygame.K_RETURN)                 # CREDITS -> SET UP
        g.key(pygame.K_y)                      # monitor berwarna? Y
        g.key(pygame.K_y)                      # suara? Y  -> MENU
        # ⚠ Seed dipasang SESUDAH pembuka: `askopts()` diikuti 20 undian
        # pemanasan (`for (i=0;i<0x14;i++) rnd(1);`), jadi menyetelnya lebih
        # dulu akan tergeser. Nilai yang ditangkap emulator adalah keadaan di
        # `loadcon`, yaitu SESUDAH pemanasan itu.
        g.rng_seed, g.lastgoal, g.lastvar = seed, lastgoal, lastvar
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
    for nama, obs, mode, off, isi, isiz, strip, goals in KASUS:
        for level in SEMUA_LEVEL:
            for goal in goals:
                uji_mode(folder, nama, obs, mode, off, isi, isiz, strip, arc,
                         goal, level)
    for level in SEMUA_LEVEL:
        print("  Contraption Mix Up: RENTETAN enam ronde (%s)"
              % ("Apprentice" if level == 1 else "Master Builder"))
        uji_mixup_rentetan(folder, arc, level)
    print("  Fill in Mechanisms lewat JALUR PEMAIN")
    uji_interaktif(folder, arc)
    print("")
    print("%s" % ("LAYAR BERMAIN IDENTIK DENGAN GAME ASLI"
                  " (6 goal x 2 mode x 2 level + 6 ronde Mix Up x 2 level)"
                  if not gagal else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "playseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
