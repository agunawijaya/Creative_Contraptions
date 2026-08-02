"""Contraption Mix Up: RENTETAN kontraption, bukan satu.

Menguji struktur yang dibaca dari `main_.c` case 4:

    sub = 0; goal = 6; pickmax();
    while (goal > 0) { ...; sub++; loadcon(-1); ...; if (lvl == 1) goal++; goal--; }

Jadi:
  * Mix Up TIDAK lewat `goalmenu()` -- kontraption 1..6 dimainkan BERURUTAN;
  * Master Builder (lvl 2) = enam ronde lalu keluar ke menu;
  * Apprentice (lvl 1) = tak berujung (goal++ dan goal-- saling meniadakan);
  * skornya TERKUMPUL lintas ronde, bukan direset tiap kontraption.

⚠ Versi lama uji ini menavigasi lewat layar GOAL dan tetap "lulus" sesudah
layar itu dihapus untuk Mix Up -- tombol berlebihnya cuma terserap gelung
PLAY. Alat ukur yang tidak ikut diperbarui akan menyembunyikan perubahan
perilaku, bukan melaporkannya.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")

import pygame                                                  # noqa: E402

from cc import assets                                          # noqa: E402
import main                                                    # noqa: E402

gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-50s %s%s" % (nama, "OK" if ok else "GAGAL",
                            "" if ok else "  (%s != %s)" % (dapat, harap)))


def mulai(g, level):
    """TITLE -> MENU -> Mix Up -> LEVEL. TIDAK ada layar GOAL."""
    g.key(pygame.K_RETURN)
    for _ in range(3):
        g.key(pygame.K_DOWN)             # sel = 3 = Contraption Mix Up
    g.key(pygame.K_RETURN)               # -> LEVEL
    for _ in range(level):
        g.key(pygame.K_DOWN)
    g.key(pygame.K_RETURN)               # pilih level -> INSTRUKSI (menu12)
    g.key(pygame.K_RETURN)               # ENTER -> LANGSUNG main


def isi_benar(g):
    def pal_of(idm):
        for i, p in enumerate(g.palette):
            if idm in p[1]:
                return i
        return None
    for i, s in enumerate(g.slots):
        c = pal_of(s["correct"])
        if c is not None:
            g.cur_slot = i
            g.cur_part = c
            g.key(pygame.K_RETURN)
    return all(s["filled"] == s["correct"] for s in g.slots)


def main_uji():
    pygame.init()
    d = assets.find_data_dir()

    print("Master Builder: enam ronde lalu kembali ke menu")
    g = main.Game(d)
    mulai(g, 1)
    cek("langsung PLAY tanpa layar GOAL", g.state, main.PLAY)
    cek("layar INSTRUKSI muncul sekali", 3 in g.instruksi_tampil, True)
    cek("kontraption pertama = sub 1", g.chosen_goal, 1)
    cek("sisa ronde = 6", g.mix_sisa, 6)
    cek("penanda petunjuk Master dibuat", g.petunjuk is not None, True)

    urut = []
    skor = []
    for ronde in range(6):
        urut.append(g.chosen_goal)
        if not isi_benar(g):
            gagal.append("ronde %d tidak bisa diisi benar" % (ronde + 1))
            break
        g.key(pygame.K_SPACE)            # menang -> animasi
        skor.append(g.score)
        g.key(pygame.K_SPACE)            # SPACE = kontraption berikutnya
    cek("urutan kontraption 1..6", urut, [1, 2, 3, 4, 5, 6])
    cek("sesudah ronde ke-6 kembali ke MENU", g.state, main.MENU)
    cek("skor tidak pernah turun antar ronde",
        all(b >= a for a, b in zip(skor, skor[1:])), True)
    cek("skor akhir > skor ronde pertama", skor[-1] > skor[0], True)

    print("\nApprentice: tak berujung, berputar 6 -> 1")
    g = main.Game(d)
    mulai(g, 0)
    cek("sisa ronde tak dibatasi", g.mix_sisa, None)
    urut = []
    for _ in range(8):
        urut.append(g.chosen_goal)
        if not isi_benar(g):
            break
        g.key(pygame.K_SPACE)
        g.key(pygame.K_SPACE)
    cek("berputar sesudah kontraption ke-6", urut, [1, 2, 3, 4, 5, 6, 1, 2])
    cek("masih bermain, tidak keluar ke menu",
        g.state in (main.PLAY, main.PLAYANIM), True)

    print("\nFill in Mechanisms TETAP lewat layar GOAL")
    g = main.Game(d)
    g.key(pygame.K_RETURN)
    g.key(pygame.K_DOWN)                 # sel = 1 = Fill in Mechanisms
    g.key(pygame.K_RETURN)
    g.key(pygame.K_RETURN)               # Apprentice -> INSTRUKSI
    g.key(pygame.K_RETURN)               # ENTER -> GOAL
    cek("mode 2 berhenti di layar GOAL", g.state, main.GOAL)

    print("\nTimer Mix Up tetap berjalan mundur")
    g = main.Game(d)
    mulai(g, 1)
    g.timer = 3.0
    g.state = main.PLAY
    g.running = False
    for _ in range(120):
        g.tick()
    cek("waktu habis -> timer 0", round(g.timer, 1), 0)

    pygame.quit()
    print("\n%s" % ("SEMUA UJI MIX UP LULUS" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


sys.exit(main_uji())
