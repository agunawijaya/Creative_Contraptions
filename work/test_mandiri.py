"""REGRESI KEMANDIRIAN: port tidak boleh MEMBACA satu pun berkas rekaman.

`port/cc/anim/` (frame animasi ter-pack, jalur bola, tata letak Review, ikon)
dan `port/cc/draws/` (daftar blit per goal) semuanya hasil MENJALANKAN gim di
emulator. Selama port membacanya, "cocok dengan gim" hanya berarti "berhasil
memutar rekaman" -- bukan bahwa aturannya dipahami.

Uji ini tidak memindahkan berkas apa pun. Ia membungkus `builtins.open` dan
`pygame.image.load` supaya SETIAP pembacaan di bawah kedua folder itu
melempar, lalu menjalankan port lewat jalur pemain: menu utama, keempat mode,
layar Review, dan animasi kemenangan. Kalau ada satu saja yang masih dibaca,
uji ini gagal dengan menyebut berkasnya.

⚠ Jangan menggantinya dengan "cari string di kode": rujukan bisa disusun dari
potongan path saat runtime, dan komentar/docstring akan memberi positif palsu.
Yang diuji harus PEMBACAAN yang benar-benar terjadi.
"""
import builtins
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "port"))

TERLARANG = (os.path.join("cc", "anim"), os.path.join("cc", "draws"),
             "cc/anim", "cc/draws")
dibaca = []


def _terlarang(path):
    try:
        p = os.path.abspath(str(path))
    except Exception:
        return False
    return any(t.replace("/", os.sep) in p for t in TERLARANG)


_open_asli = builtins.open


def _open_jaga(file, *a, **k):
    if _terlarang(file):
        dibaca.append(str(file))
        raise AssertionError("port MEMBACA berkas rekaman: %s" % file)
    return _open_asli(file, *a, **k)


def main():
    builtins.open = _open_jaga
    try:
        import pygame
        from cc import assets, cga
        import main as portmain

        _load_asli = pygame.image.load

        def _load_jaga(f, *a, **k):
            if _terlarang(f):
                dibaca.append(str(f))
                raise AssertionError("port MEMBACA gambar rekaman: %s" % f)
            return _load_asli(f, *a, **k)
        pygame.image.load = _load_jaga

        pygame.init()
        fb = cga.make_framebuffer()
        langkah = []

        def jalan(nama, tombol):
            g = portmain.Game(assets.find_data_dir())
            for t in tombol:
                g.key(t)
            g.draw(fb)
            for _ in range(30):
                g.tick()
            g.draw(fb)
            langkah.append((nama, g.state))

        R, D_, S = pygame.K_RETURN, pygame.K_DOWN, pygame.K_SPACE
        jalan("layar judul", [])
        jalan("menu utama", [R])
        jalan("Review Mechanisms", [R, R])
        jalan("Review detail + demo", [R, R, R, S])
        jalan("Fill in Mechanisms", [R, D_, R, R, R])
        jalan("Fill in Zany", [R, D_, D_, R, R, R])
        jalan("Contraption Mix Up", [R, D_, D_, D_, R, R])

        # animasi kemenangan (jalur yang dulu memutar cc/anim/*.dat)
        g = portmain.Game(assets.find_data_dir())
        for t in (R, D_, R, R, R):
            g.key(t)

        def pal_of(idm):
            for i, p in enumerate(g.palette):
                if idm in p[1]:
                    return i
            return None
        for i, s in enumerate(g.slots):
            c = pal_of(s["correct"])
            if c is not None:
                g.cur_slot, g.cur_part = i, c
                g.key(R)
        g.key(S)
        for _ in range(200):
            g.tick()
        g.draw(fb)
        langkah.append(("animasi kemenangan", g.state))

        pygame.quit()
    finally:
        builtins.open = _open_asli

    for nama, st in langkah:
        print("  %-24s OK (state=%d)" % (nama, st))
    print("\n%s" % ("PORT MANDIRI: tidak satu pun berkas rekaman dibaca"
                    if not dibaca else "GAGAL, dibaca: %s" % dibaca))
    return 1 if dibaca else 0


sys.exit(main())
