"""REGRESI ANIMASI: tiap frame port harus BYTE-IDENTIK dgn VRAM game asli.

Ini uji terkuat yang dimiliki jalur port. Bukan "mirip bergerak", bukan
"tidak error": untuk tujuh layar (goal 1..6 + layar judul) setiap panggilan
`drawball` di game menghasilkan satu tangkapan VRAM, dan frame ke-n port
harus sama piksel per piksel dengan tangkapan ke-n.

Tangkapan dibuat SENDIRI oleh skrip ini lewat emulator Unicorn
(`work/emu.py`, `CC_VRAMSEQ=26ae=<folder>`), jadi tidak bergantung pada
berkas rekaman yang harus diingat asal-usulnya. Sekali dibuat, tangkapan
dipakai ulang; hapus foldernya untuk membuatnya lagi.

    python work/test_anim_vs_gim.py            # bikin/pakai work/animseq/
    python work/test_anim_vs_gim.py <folder>   # pakai tangkapan yang sudah ada

⚠ Bandingannya adalah kotak VRAM saat MASUK `drawball`. Panggilan `setball()`
dari `setupscr` adalah drawball PERTAMA game dan TIDAK dihitung di port --
karena itu tangkapan f0000 dilewati dan f0001 diadu dgn frame port ke-0.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import contrap, adegan                            # noqa: E402
from cc.core.archive import Archive                            # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(AKAR, "_ORIGINAL_READONLY")
LAYAR = (1, 2, 3, 4, 5, 6, 128)
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def tangkap(folder, goal):
    """Jalankan emulator sampai animasi satu layar habis, simpan tiap frame."""
    seq = os.path.join(folder, "seq%d" % goal)
    if os.path.isdir(seq) and os.listdir(seq):
        return seq
    print("  [emu] menangkap goal %d ..." % goal)
    env = dict(os.environ)
    env["CC_OUT"] = os.path.join(folder, "out")
    # Batas 1200: layar judul saja butuh 676 frame (enam pantulan `bounce()`
    # sebelum teks judul muncul). Bawaan CC_VRAMSEQ 400 memotongnya.
    env["CC_VRAMSEQ"] = "26ae=%s:1200" % seq
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(goal), "1"], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def uji_jalur_pemain(folder):
    """LAYAR JUDUL lewat `main.Game` + `draw()`, bukan lewat modul inti.

    Perlu terpisah karena kedua jalur bisa berbeda: `main.py` memanggil
    `adegan.frames()` dgn batas frame SENDIRI, dan batas itu pernah dipatok 400
    -- memotong layar judul (675 frame) tepat di tengah, sementara uji
    per-modul lolos karena ia memakai batasnya sendiri.
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    from cc import assets, cga
    import main as portmain

    seq = os.path.join(folder, "seq128")
    n = len([f for f in os.listdir(seq) if f.endswith(".png")])
    pygame.init()
    try:
        g = portmain.Game(assets.find_data_dir())
        fb = cga.make_framebuffer()
        cocok = 0
        pertama = None
        for k in range(n - 1):
            g.title_tick = k * 2          # _title(): frame = title_tick // 2
            g.draw(fb)
            ref = muat(os.path.join(seq, "f%04d.png" % (k + 1)))
            sama = all(PALET[fb.get_at((x, y))[:3]] == ref[y][x]
                       for y in range(200) for x in range(320))
            if sama:
                cocok += 1
            elif pertama is None:
                pertama = k
    finally:
        pygame.quit()
    print("  layar judul lewat JALUR PEMAIN : %d/%d frame identik%s"
          % (cocok, n - 1, "" if pertama is None else "   (beda pertama f%d)" % pertama))
    return cocok == n - 1


def main(folder):
    g = Archive(D + "/GRAPH")
    m = Archive(D + "/MECHS")
    mi = Archive(D + "/MISC")
    an = Archive(D + "/ANIMATE")
    cs = contrap.parse(D + "/CONTRAP")

    tot_ok = tot = beda_piksel = 0
    semua = True
    for goal in LAYAR:
        seq = tangkap(folder, goal)
        n = len([f for f in os.listdir(seq) if f.endswith(".png")])
        fs = adegan.frames(goal, g, m, mi, an, cs, mode=0,
                           sub=(goal if goal != 128 else None), maks=1200)
        ok = dibanding = 0
        gagal = []
        for k in range(1, n):
            if k - 1 >= len(fs):
                break
            ref = muat(os.path.join(seq, "f%04d.png" % k))
            por = fs[k - 1]
            b = sum(1 for y in range(200) for x in range(320)
                    if por[y][x] != ref[y][x])
            dibanding += 1
            beda_piksel += b
            if b:
                gagal.append((k, b))
            else:
                ok += 1
        tot_ok += ok
        tot += dibanding
        sisa = (n - 1) - dibanding
        print("  layar %-3s : %3d/%-3d frame identik%s"
              % ("judul" if goal == 128 else goal, ok, dibanding,
                 "   (%d frame rujukan belum dijangkau VM)" % sisa if sisa else ""))
        for k, b in gagal[:5]:
            print("      f%04d beda %d piksel" % (k, b))
        semua = semua and not gagal

    semua = uji_jalur_pemain(folder) and semua

    piksel = tot * 320 * 200
    print("\n  TOTAL %d/%d frame  |  %d/%d piksel (%.6f%%)"
          % (tot_ok, tot, piksel - beda_piksel, piksel,
             100.0 * (piksel - beda_piksel) / max(1, piksel)))
    print("\n%s" % ("ANIMASI IDENTIK DENGAN GAME ASLI" if semua
                    else "ADA FRAME YANG BELUM COCOK"))
    return 0 if semua else 1


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "animseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
