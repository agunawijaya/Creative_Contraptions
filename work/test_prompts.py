"""REGRESI `prompts()` dan `hintmark()` — dua fungsi yang lama tak terukur.

`prompts()` @0x2B77 menulis pesan akhir goal. Ia diukur dgn cara yang paling
langsung: tangkap VRAM di alamat MASUK-nya dan di alamat RET-nya, lalu jalankan
`hud.prompts()` di atas tangkapan MASUK dan bandingkan dgn tangkapan RET.
Yang diadu murni EFEK fungsi itu, tanpa perlu menyusun ulang layarnya.

`hintmark()` @0x4CD4 hanya berbuat sesuatu di mode 4 level Master Builder
(`if (mode != 4 || lvl != 2) return;`). Stub menu emulator selalu memilih
level 1, jadi selama ini fungsi itu TIDAK BISA dijangkau sama sekali; saklar
`CC_LEVEL=2` di work/emu.py yang membukanya.

Karena penandanya digambar `text()` -- yang tidak dirender emulator -- yang
diadu adalah KEADAAN yang dihitungnya (cur2, lvl6, timer, mflag), dibaca
langsung dari DGROUP. Itu justru bagian yang menentukan permainan: slot mana
yang ditunjuk dan kapan `mflag` menyala (syarat bonus bola).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "port"))

from PIL import Image                                          # noqa: E402

from cc.core import hud, render as rend                        # noqa: E402
from cc.core.rng import Rng                                    # noqa: E402

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALET = {(0, 0, 170): 0, (0, 170, 170): 1, (170, 0, 170): 2, (170, 170, 170): 3}
PROMPTS_MASUK, PROMPTS_RET = "2b77", "2d10"
HINTMARK = "4cd4"

gagal = []


def muat(p):
    im = Image.open(p).convert("RGB").load()
    return [[PALET[im[x, y]] for x in range(320)] for y in range(200)]


def emu(folder, nama, goal, mode, env_extra):
    seq = os.path.join(folder, nama)
    if not (os.path.isdir(seq) and os.path.exists(os.path.join(seq, "globals.json"))):
        print("  [emu] menangkap %s ..." % nama)
        env = dict(os.environ)
        env.update(CC_OUT=os.path.join(folder, "out_" + nama),
                   CC_MAXINSN="300000000")
        env.update(env_extra)
        subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                        str(goal), str(mode)], env=env, cwd=AKAR,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.load(open(os.path.join(seq, "globals.json"))), seq


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("    %-40s %-9s %s" % (nama, dapat if ok else "%s != %s" % (dapat, harap),
                                 "OK" if ok else "GAGAL"))


def uji_prompts(folder):
    print("  prompts() -- efeknya diadu langsung (MASUK vs RET)")
    for goal in (1, 6):
        Ga, sa = emu(folder, "prompts_masuk_%d" % goal, goal, 1, {
            "CC_VRAMSEQ": "%s=%s:2" % (PROMPTS_MASUK,
                                       os.path.join(folder, "prompts_masuk_%d" % goal)),
            "CC_VSWORD": "792,734,718,3b2"})
        Gb, sb = emu(folder, "prompts_ret_%d" % goal, goal, 1, {
            "CC_VRAMSEQ": "%s=%s:2" % (PROMPTS_RET,
                                       os.path.join(folder, "prompts_ret_%d" % goal)),
            "CC_VSWORD": "792,734,718,3b2"})
        if not Ga or not Gb:
            gagal.append("prompts goal %d tak terjangkau" % goal)
            continue
        masuk = muat(os.path.join(sa, "f%04d.png" % Ga[0]["frame"]))
        keluar = muat(os.path.join(sb, "f%04d.png" % Gb[0]["frame"]))
        fb = [r[:] for r in masuk]
        hud.prompts(rend.KanvasFB(fb), Ga[0]["w792"], Ga[0]["w3b2"], 0,
                    Ga[0]["w734"], Ga[0]["w718"])
        beda = sum(1 for y in range(200) for x in range(320)
                   if fb[y][x] != keluar[y][x])
        diubah = sum(1 for y in range(200) for x in range(320)
                     if masuk[y][x] != keluar[y][x])
        cek("goal %d (gim mengubah %d piksel)" % (goal, diubah), 64000 - beda, 64000)


def uji_hintmark(folder):
    print("  hintmark() -- keadaan penanda, dibaca dari DGROUP")
    G, _ = emu(folder, "hintmark", 1, 4, {
        "OBSERVE": "mixup", "CC_NOSKIP": "1", "CC_LEVEL": "2",
        "CC_OBSKEYS": ",".join(["0d"] * 16),
        "CC_VRAMSEQ": "%s=%s:6" % (HINTMARK, os.path.join(folder, "hintmark")),
        "CC_VSWORD": "792,734,7f2,7ee,82e,7f8,7f6,3b4,830,834"})
    if len(G) < 2:
        gagal.append("hintmark tak terjangkau")
        print("    tidak terjangkau (butuh CC_LEVEL=2)")
        return
    a, b = G[0], G[1]                      # sebelum dan sesudah penanda pindah
    cek("gim: mode 4, level Master", (a["w792"], a["w734"]), (4, 2))
    cek("gim: lvl6 awal == nmax", a["w7f6"], a["w3b4"])

    # Jalankan Petunjuk port dgn keadaan gim, lalu adu hasilnya.
    p = hud.Petunjuk(Rng(0), a["w3b4"])
    p.timer, p.lvl6, p.cur2 = -1 if a["w7f2"] == 0xFFFF else a["w7f2"], a["w7f6"], a["w7f8"]
    p.range_, p.best, p.nmax = a["w830"], a["w82e"], a["w3b4"]
    # cari seed yang memberi undian yang SAMA dgn gim (cur2 gim sudah diketahui)
    sasaran = b["w7f8"] - (a["w7f6"] - 1) + 2      # rnd(3) + rnd(3) di gim
    ketemu = None
    for seed in range(0x4000):
        r = Rng(seed)
        if r.rnd(3) + r.rnd(3) == sasaran:
            ketemu = seed
            break
    if ketemu is None:
        gagal.append("tak ada seed yang mereproduksi undian gim")
        return
    p.rng = Rng(ketemu)
    p.tik(a["w792"], a["w734"], a["w7ee"], [(0, 0)] * a["w3b4"])
    cek("cur2 sesudah pindah", p.cur2, b["w7f8"])
    cek("lvl6 menyusut satu", p.lvl6, b["w7f6"])
    cek("timer di-set ulang 0x3c", p.timer, b["w7f2"])
    cek("mflag (syarat bonus bola)", p.mflag, b["w834"])


def uji_baris_pesan(folder):
    """Di baris mana keluaran `printf()` gim mendarat -- DIUKUR.

    Dua hal harus dibuka dulu, dan keduanya sempat dikira "tak bisa":

    1. `animvm()` dibuka gelung "jam pasir" `for(;;) { waitn(0x10); ... }`
       yang berhenti pada `ticks <= 0`. `ticks` dihitung mundur ISR timer, dan
       ISR itu tidak berjalan di emulator -- jadi eksekusi berhenti JAUH
       sebelum sampai ke `printf`. Saklar `CC_NOWAIT=1` menol-kan `ticks` di
       stub `waitn()`. (Sekadar mengembalikan `waitn` seketika TIDAK cukup:
       gelungnya cuma berputar lebih cepat.)
    2. keluaran teks DOS/BIOS dibuang diam-diam oleh emulator. `CC_TRACEDOS=1`
       merekamnya, TERMASUK INT 10h AH=02h (set posisi kursor).

    Hasilnya: 11 kali set kursor ke (baris 22, kolom 0), dan `f66fd` @0x66fd
    -- yang dipanggil `animvm.c:219` sebagai `f66fd(0x16, 0)` di puncak gelung
    per-slot -- juga terpanggil tepat 11 kali. 0x16 = 22, dan 11 = jumlah slot
    kontraption. Jadi baris pesannya y = 22*8 = 176, x = 0.
    """
    import re
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(folder, "out_kursor"), OBSERVE="fillmech",
               CC_NOWAIT="1", CC_TRACEDOS="1", CC_MAXINSN="300000000")
    r = subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                        "1", "2"], env=env, cwd=AKAR,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    keluar = r.stdout.decode("latin-1", "replace")
    kursor = re.findall(r"kursor\s+\((\d+), (\d+)\)", keluar)
    print("  baris pesan printf -- diukur lewat INT 10h AH=02h")
    cek("jumlah set kursor", len(kursor), 11)
    cek("posisi kursor (baris, kolom)",
        sorted(set(kursor)), [("22", "0")])
    cek("hud.PESAN_Y == baris * 8", hud.PESAN_Y, 22 * 8)
    cek("hud.PESAN_X == kolom * 8", hud.PESAN_X, 0)


def main(folder):
    uji_prompts(folder)
    uji_hintmark(folder)
    uji_baris_pesan(folder)
    print("\n%s" % ("prompts() DAN hintmark() COCOK DENGAN GIM" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AKAR, "work", "prseq")
    if not os.path.isdir(f):
        os.makedirs(f)
    sys.exit(main(f))
