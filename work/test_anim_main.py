"""REGRESI ANIMASI JALUR BERMAIN: larian MENANG, lewat `main.Game`.

Uji animasi yang lain (`test_anim_vs_gim.py`) menangkap `emu.py <goal> 1` --
yaitu animasi ATTRACT. Berkas ini menguji animasi yang berjalan sesudah pemain
menekan SPACE di mode 2/3/4, dan ia memang BERBEDA: panjangnya bergantung pada
apa yang ditaruh pemain.

KEDUA SISI MENJALANKAN LARIAN YANG SAMA
---------------------------------------
Emulator secara bawaan MEMAKSA cabang "jawaban cocok"
(`hook_mechmatch`/`hook_zanymatch`), jadi gim selalu menang. `CC_SALAH=1`
mematikannya, sehingga gim menuruti penempatan sungguhan -- sama seperti port.
Urutan tombolnya identik di kedua sisi, jadi penempatannya lahir dari tombol
itu sendiri, bukan dipaksakan.

TIGA HAL YANG HARUS BENAR, dan ketiganya mahal didapat
------------------------------------------------------
1. `lastgoal`/`lastvar` WAJIB diteruskan. Tanpa keduanya gelung penghindar
   varian di `loadcon()` tidak berjalan dan port menganimasikan varian yang
   SAMA SEKALI LAIN -- 18.324 piksel di bingkai pertama.
2. Penjajaran bingkai = **offset 2**. Tangkapan `f0000`/`f0001` jalur bermain
   masih layar SETENGAH GAMBAR (arena kosong); kontraption baru lengkap di
   `f0002`. Jalur attract memakai offset 1; menyamakannya keliru.
3. `clrbot()` @0x5911 MENGOSONGKAN dasar layar sebelum larian, jadi baris
   pesan cyan yang digambar `setupscr()` untuk `sub == 1` TIDAK ada saat
   animasi -- 288x8 = 2.304 piksel, persis.

YANG BELUM (jangan diklaim selesai)
-----------------------------------
Larian GAGAL belum diadu. Di gim, slot mekanisme yang salah menghentikan
animasi (`animvm.c` baris 222: `break`), dan lemparan ke part yang salah
memakai skrip KARANGAN `{00, dx, dy, FF}` (baris 433). Port memodelkan
kegagalan dgn lintasan bola pra-hitung (`_jalur()`), yaitu mekanisme yang
BERBEDA -- jadi membandingkannya sekarang hanya akan mengadu dua hal yang
memang tidak sama.
"""
import glob
import json
import os
import subprocess
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
OFFSET = 2                    # lihat catatan 2 di kepala berkas
GOAL = 1
TOMBOL = ",".join(["20"] * 6)          # SPACE: langsung jalankan
gagal = []

# nama, OBSERVE, mode gim, indeks di menu utama, lewat layar GOAL
KASUS = [
    ("Fill in Mechanisms", "fillmech", 2, 1, True),
    ("Fill in Zany",       "zany",     3, 2, True),
    ("Contraption Mix Up", "mixup",    4, 3, False),
]


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("    %-34s %6s/%-6s %s" % (nama, dapat, harap, "OK" if ok else "GAGAL"))


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def _emu(folder, nama, obs, mode, extra):
    seq = os.path.join(folder, nama)
    if os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json")):
        return seq
    print("  [emu] menangkap %s ..." % nama)
    env = dict(os.environ)
    # ⚠ CC_SALAH=1 MEMATIKAN `hook_mechmatch`/`hook_zanymatch`, yang secara
    # bawaan MEMAKSA cabang "jawaban cocok". Tanpa ini gim selalu menang
    # sementara port -- yang menuruti penempatan sungguhan -- gagal, jadi yang
    # diadu dua keadaan yang berbeda.
    env.update(CC_OUT=os.path.join(folder, "out_" + nama), OBSERVE=obs,
               CC_NOSKIP="1", CC_NOWAIT="1", CC_LEVEL="1", CC_SALAH="1",
               CC_MAXINSN="600000000", CC_OBSKEYS=TOMBOL)
    env.update(extra)
    subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                    str(GOAL), str(mode)], env=env, cwd=AKAR,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return seq


def tangkap(folder, obs, mode):
    seq = _emu(folder, "%s_anim" % obs, obs, mode, {
        "CC_VRAMSEQ": "26ae=%s:400" % os.path.join(folder, "%s_anim" % obs),
        "CC_VSWORD": "3ac,51c,738,718,3b2,7e6"})
    rng = _emu(folder, "%s_rng" % obs, obs, mode, {
        "CC_VRAMSEQ": "5035=%s:6" % os.path.join(folder, "%s_rng" % obs),
        "CC_VSWORD": "71a,3b2,1e2e,1e30"})
    return seq, json.load(open(os.path.join(rng, "globals.json")))[-1]


def bingkai_port(obs, mode, sel_menu, punya_goal, lc):
    """Animasi MENANG lewat jalur pemain sungguhan: main.Game + key()."""
    import pygame
    from cc import assets
    from cc.core import palet as _pal
    import main as portmain

    asli = _pal.penunjuk
    _pal.penunjuk = lambda *a, **k: None
    pygame.init()
    try:
        g = portmain.Game(assets.find_data_dir())
        for k in (pygame.K_RETURN, pygame.K_RETURN, pygame.K_y, pygame.K_y):
            g.key(k)
        g.rng_seed, g.lastgoal, g.lastvar = lc["w71a"], lc["w1e2e"], lc["w1e30"]
        for _ in range(sel_menu):
            g.key(pygame.K_DOWN)
        g.key(pygame.K_RETURN)                 # -> LEVEL (Apprentice)
        g.key(pygame.K_RETURN)                 # -> INSTRUKSI
        g.key(pygame.K_RETURN)                 # -> GOAL / PLAY
        if punya_goal:
            g.sel = g.goal_ids.index(GOAL)
            g.key(pygame.K_RETURN)
        # Urutan tombol yang SAMA dgn yang diumpankan emulator. Penempatannya
        # lahir dari tombol itu sendiri, bukan dipaksakan: SPACE pertama
        # menaruh part yang disorot lalu mengakhiri pemilihan, SPACE kedua
        # menjalankan.
        g.key(pygame.K_SPACE)
        g.key(pygame.K_SPACE)
        # `anim_frames` adalah daftar pygame.Surface; disalin apa adanya
        # karena `pygame.quit()` di bawah tidak membatalkan permukaannya.
        return list(getattr(g, "anim_frames", [])), g
    finally:
        _pal.penunjuk = asli
        pygame.quit()


def uji(folder, nama, obs, mode, sel_menu, punya_goal):
    seq, lc = tangkap(folder, obs, mode)
    ref = sorted(glob.glob(os.path.join(seq, "*.png")))
    if len(ref) <= OFFSET:
        gagal.append("%s: emulator tidak menghasilkan animasi" % nama)
        print("  %s: tidak ada tangkapan" % nama)
        return
    surf, g = bingkai_port(obs, mode, sel_menu, punya_goal, lc)
    print("  %s: gim %d bingkai, port %d" % (nama, len(ref) - OFFSET, len(surf)))
    if not surf:
        gagal.append("%s: port tidak menghasilkan animasi" % nama)
        return
    import pygame
    n = min(len(ref) - OFFSET, len(surf))
    sama = 0
    for k in range(n):
        r = muat(ref[k + OFFSET])
        s = surf[k]
        beda = sum(1 for y in range(200) for x in range(320)
                   if PALET[s.get_at((x, y))[:3]] != r[y][x])
        if beda == 0:
            sama += 1
        elif sama == k:
            print("      beda pertama di bingkai %d: %d piksel" % (k, beda))
    cek("%s bingkai identik" % nama, sama, n)


def main(folder):
    for nama, obs, mode, selm, pg in KASUS:
        uji(folder, nama, obs, mode, selm, pg)
    print("\n%s" % ("ANIMASI JALUR BERMAIN IDENTIK DENGAN GAME ASLI"
                    if not gagal else "BELUM COCOK: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "animmainseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
