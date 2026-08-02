"""REGRESI `autofill()` dan bunyi klik menu -- dua perilaku yang lama tak ada.

`autofill()` @0x5954: untuk tiap slot yang pencacah gagalnya `fail[i] >= 2`,
gim MENGISIKAN jawaban benarnya. `main_.c` memanggilnya HANYA di level
Apprentice (`if (lvl == 1)`), sesudah animasi. Jadi pemain pemula tidak bisa
tersangkut selamanya di satu kotak -- dan port lama tidak punya ini sama
sekali.

`tone2()` @0x3734: `runmenu()` memanggilnya tiap kali sebuah pilihan diterima.
Deskriptor nadanya @0x1DDB -- arpeggio naik tiga not. Port lama diam total di
menu.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "port"))

import pygame                                                  # noqa: E402

from cc import assets, cga                                     # noqa: E402
from cc.core import bunyi                                      # noqa: E402
import main as portmain                                        # noqa: E402

gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-42s %-6s %s" % (nama, dapat, "OK" if ok else "GAGAL (harap %s)" % (harap,)))


def buka(g, level):
    R, D = pygame.K_RETURN, pygame.K_DOWN
    g.key(R); g.key(R); g.key(pygame.K_y); g.key(pygame.K_y)   # judul->credits->setup->menu
    g.key(D); g.key(R)                                          # Fill in Mechanisms -> LEVEL
    for _ in range(level):
        g.key(D)
    g.key(R); g.key(R)                                          # level -> INSTRUKSI -> GOAL
    g.sel = 0
    g.key(R)                                                    # -> PLAY


def dua_kali_salah(g):
    benar = g.slots[0]["correct"]
    salah = [i for i, p in enumerate(g.palette) if benar not in p[1]][0]
    for _ in range(2):
        for s in g.slots:
            s["filled"] = None
        g.cur_slot, g.cur_part = 0, salah
        g.key(pygame.K_RETURN)
        for i, s in enumerate(g.slots[1:], 1):
            c = [k for k, p in enumerate(g.palette) if s["correct"] in p[1]]
            if c:
                g.cur_slot, g.cur_part = i, c[0]
                g.key(pygame.K_RETURN)
        # ⚠ SPACE punya DUA tahap di gim: yang pertama MENARUH part yang
        # sedang disorot lalu mengakhiri pemilihan, yang kedua menjalankan.
        # Uji ini sengaja menyisakan slot yang salah/kosong, jadi tahap
        # "menaruh" akan merusak skenarionya. Yang dinyatakan di sini:
        # pemilihan sudah selesai, tinggal dijalankan.
        g.pilih_selesai = True
        g.key(pygame.K_SPACE)
        for _ in range(400):
            g.tick()
            if not g.running and g.ball_i < 0:
                break


def main():
    pygame.init()
    d = assets.find_data_dir()
    print("  nada klik menu (tone2 @0x1DDB)")
    n = bunyi.nada_dgroup(bunyi.NADA_TONE2)
    cek("tiga not naik", [f for f, _t in n], [1048, 1176, 1320])
    cek("tone() dan tone2() nadanya sama",
        bunyi.nada_dgroup(bunyi.NADA_TONE) == n, True)

    print("  autofill() -- bantuan sesudah dua kali gagal")
    for level, nama, harap in ((0, "Apprentice", True), (1, "Master", False)):
        g = portmain.Game(d)
        buka(g, level)
        dua_kali_salah(g)
        cek("%s: slot gagal 2x -> diisikan gim" % nama,
            bool(g.slots[0].get("auto")), harap)
        cek("%s: pencacah gagal >= 2" % nama, g.slots[0]["tries"] >= 2, True)
    pygame.quit()
    hasil = "BANTUAN DAN BUNYI KLIK COCOK" if not gagal else (
        "GAGAL: " + ", ".join(gagal))
    print("")
    print(hasil)
    return 1 if gagal else 0


sys.exit(main())
