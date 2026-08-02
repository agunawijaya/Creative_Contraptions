"""Creative Contraptions port — skeleton dengan alur menu.

Alur (mengikuti game asli): TITLE -> MENU(4 mode) -> LEVEL -> GOAL -> CONTRAPTION.
String & alur dari hasil reverse-engineering (lihat GAME_GUIDE.md / CODE_MAP.md).

Jalankan:  python port/main.py
           python port/main.py --shots     (render tiap layar ke PNG, headless)
"""
import os
import sys
import json
import struct
import zlib
import random

sys.path.insert(0, os.path.dirname(__file__))
import pygame
from cc import cga, assets, text, anim
from cc.core import archive as _arc, contrap as _con, render as _rend
from cc.core import pick as _pick, rng as _rng, adegan as _adg
from cc.core import resensi as _res, hud as _hud, palet as _pal
from cc.core import menu as _menu, bunyi as _bunyi


GOAL_NAMES = {1: "Up and At 'Em", 2: "Hair Care", 3: "Easy Eating",
              4: "Dog Days", 5: "Cool It", 6: "Lights Out!"}
MENU_OPTIONS = ["Review Mechanisms", "Fill in Mechanisms",
                "Fill in Zany Objects", 'Play "Contraption Mix Up"']
LEVELS = ["Apprentice", "Master Builder"]

# 9 KATEGORI mekanisme (spt game asli: "tepat 9 ikon"). Tiap kategori = beberapa
# id_major MECHS (varian). Pencocokan by-kategori: jawaban slot cocok bila id_major
# jawaban ada di set kategori yang dipilih. Grup dari GAME_GUIDE §7 (133 = Pulley).
MECH_CATEGORIES = [
    ("Inclined Plane", (100, 101)),
    ("Pulley", (110, 111, 112, 133)),
    ("Wheel & Axle", (115,)),
    ("Wedge", (120,)),
    ("Pendulum", (130, 131)),
    ("Magnet", (132,)),
    ("Screw", (135,)),
    ("Lever", (140, 141)),
    ("Spring", (150,)),
]

TITLE, MENU, LEVEL, GOAL, CONTRAPTION, PLAY, PLAYANIM, REVIEW, REVIEW_DETAIL = range(9)

# urutan mekanisme di Review = urutan MECH_CATEGORIES (Inclined Plane, Pulley, ...)

# Ensiklopedia "Review Mechanisms" — teks EKSAK diekstrak dari biner (offset 0x9F36+).
# (nama, id_major utama, [baris deskripsi]). Urutan = urutan mekanisme di game.
REVIEW_DATA = [
    ("Inclined Plane", 100, ["A SIMPLE MACHINE", "A sloping surface.", "",
                             "Example: A ramp is an", "inclined plane."]),
    ("Pulley", 110, ["A grooved wheel that is often", "used with a rope to lift objects.",
                     "", "Examples: Pulleys are used to", "raise flags and sails. Cranes",
                     "have pulleys to lift heavy objects."]),
    ("Wheel and Axle", 115, ["A wheel that turns", "or rotates around a rod.", "",
                             "Examples: A doorknob is a wheel", "and axle. Eggbeaters (manual)",
                             "and bicycles have wheels and axles."]),
    ("Wedge", 120, ["One or two inclined planes often", "used for cutting or splitting",
                    "things apart.", "", "Examples: A chisel, ax, nail,",
                    "and doorstop are wedges."]),
    ("Pendulum", 130, ["A hanging rod that", "freely swings back and forth.", "",
                       "Examples: Grandfather clocks and", "cuckoo clocks have pendulums."]),
    ("Magnet", 132, ["A piece of iron or steel that can", "attract another piece of iron",
                     "or steel.", "", "Examples: Magnets are used in",
                     "electric can openers and", "cabinet doors."]),
    ("Screw", 135, ["A winding inclined plane", "around a center rod.", "",
                    "Examples: Screws are found in", "machines and furniture."]),
    ("Lever", 140, ["A bar with a support that is", "used to lift objects.", "",
                    "Examples: A seesaw, shovel, oar,", "can opener, scissors,",
                    "and hammer are levers."]),
    ("Spring", 150, ["An object that goes back to its", "original form after being",
                     "forced out of shape.", "", "Examples: Springs are used in",
                     "clocks, pinball machines, and doors."]),
]


class Game:
    def __init__(self, data_dir):
        self.graph = assets.Archive(os.path.join(data_dir, "GRAPH"))
        self.mechs = assets.Archive(os.path.join(data_dir, "MECHS"))
        # pemilih part = 9 kategori mekanisme (nama, set id_major)
        self.mech_types = MECH_CATEGORIES
        # frame animasi per id_major MECHS (indeks record) utk Review Mechanisms
        _mraw = open(os.path.join(data_dir, "MECHS"), "rb").read()
        _n = struct.unpack_from("<I", _mraw, 8)[0] // 12
        self.mech_frames = {}
        for i in range(_n):
            self.mech_frames.setdefault(_mraw[i * 12], []).append(i)
        self.rev_i = 0            # mekanisme yg ditampilkan di Review
        self.rev_frame = 0        # frame animasi Review
        self.rev_tick = 0
        self.review_demo = False  # True saat memutar demo contraption (goal 7) dari Review
        # layout Review EKSAK (diekstrak dari data game: intro, fixed, per-mekanisme)
        # Tata letak layar Review dibaca dari DGROUP, bukan dari tangkapan
        # emulator: tabel penunjuk @0x14F6 + pencacah @0x1508, record 12 byte.
        # Diperiksa terhadap berkas tangkapan lama: 74/74 record cocok.
        self.review_layout = _res.semua()
        self.anim = anim.AnimArchive(os.path.join(data_dir, "ANIMATE"))
        self.goals = assets.parse_contrap(os.path.join(data_dir, "CONTRAP"))
        # ---- lapisan INTI terverifikasi -------------------------------------
        # Aturan arsip/penempatan yang SAMA dengan work/genscreens.py (197/197).
        # Layar tidak lagi diputar dari rekaman; ia DIBANGKITKAN dari data.
        self.k_graph = _arc.Archive(os.path.join(data_dir, "GRAPH"))
        self.k_mechs = _arc.Archive(os.path.join(data_dir, "MECHS"))
        self.k_misc = _arc.Archive(os.path.join(data_dir, "MISC"))
        self.k_goals = _con.parse(os.path.join(data_dir, "CONTRAP"))
        self.k_anim = _arc.Archive(os.path.join(data_dir, "ANIMATE"))
        # Suara PC-speaker. Angka di skrip adalah FREKUENSI dalam Hz --
        # terbaca dari `1193182 / CX` di snd2.asm, bukan pembagi PIT dan bukan
        # nomor not. Diam sendiri kalau mixer tak tersedia (mis. headless).
        self.bunyi = _bunyi.Pemutar(pygame)
        # Ikon keempat mode = MISC record 7, 8, 9, 10 -- berurutan, persis
        # urutan menu (Review, Fill Mechanisms, Fill Zany, Mix Up). Dulu empat
        # PNG hasil crop dari render gim; diperiksa piksel per piksel terhadap
        # crop itu: 1100/1100 untuk keempatnya.
        self.menu_icons = [_rend.sprite_surface(self.k_misc, self.k_misc.recs[i], pygame)
                           for i in (7, 8, 9, 10)]
        self._scene_cache = {}
        # `mode` di setupscr.c menentukan warna pita bawah:
        #     col = (mode == 0 || mode == 1) ? 1 : 0
        # Mode 0 (attract/judul) dan 1 (Review) -> cyan; 2, 3, 4 -> BIRU TUA.
        # Nilai bawaan 0 dipakai layar judul dan pembanding attract; layar
        # permainan mengoper mode aslinya sendiri.
        #
        # ⚠ Ini sempat dipatok 0 untuk SEMUA layar. Tangkapan rujukan kami
        # memang mode 0 -- emulator menambal nomor goal pada `loadcon` PERTAMA,
        # yang terjadi saat layar judul -- jadi kecocokan 100% itu diukur
        # terhadap layar attract, bukan layar permainan. Diperiksa terhadap
        # tangkapan mode 2 sungguhan (OBSERVE=fillmech): baris 160..199
        # cocok 12.800/12.800 dengan setupscr(mode=2, sub=1), dan 2.304 piksel
        # meleset kalau `sub` tidak dioper.
        self.mode_latar = 0
        self.last_variant = {}    # gid -> varian terakhir (agar tak berulang, spt 0x1e30)
        self.cur_variant = 0
        # ⭐ SATU rantai RNG yang hidup terus, seperti `seed` @0x71a di gim
        # (gim mengisinya dari jam BIOS saat mulai -- lihat `sndini`).
        # `lastgoal` @0x1e2e dan `lastvar` @0x1e30 adalah SEPASANG, bukan satu
        # per goal: aturan anti-ulang `loadcon` hanya berlaku kalau goal
        # sebelumnya SAMA. Lihat catatan panjang di start_play().
        self.rng_seed = random.randrange(0x10000)
        self.lastgoal = None
        self.lastvar = None
        self.cur_seed = 0
        self.cur_lastgoal = None      # keadaan SEBELUM undian kontraption ini
        self.cur_lastvar = None
        # LAYAR JUDUL. Dulu ini rakitan tangan: jalur bola karangan, reaksi
        # objek tebakan, dan judul "CREATIVE CONTRAPTIONS" berhuruf TrueType.
        # Sekarang TIDAK ADA yang dikarang -- layar judul memakai JALUR KODE YANG
        # SAMA dengan layar design, hanya dengan sub = 0x80 (goal 128):
        #     mode = 0; goal = 1; lvl = 1; sub = 0x80;
        #     loadcon(-1); f171f(...); loadarc x4; pickpart(); fillans();
        #     f498c(); drawslot(); animvm();
        # (main_.c:295-317). Jadi _scene_surface(128) sudah menghasilkannya.
        # Terukur 64.000/64.000 piksel vs VRAM emulator, sekali coba.
        self.title_tick = 0
        self.goal_ids = [g for g in sorted(self.goals) if g in GOAL_NAMES]
        self.state = TITLE
        self.sel = 0          # kursor pilihan
        self.mode = 0         # pilihan menu (0=Review, 1=Fill Mech, 2=Fill Zany, 3=Mix Up)
        self.anim_cache = {}  # gid -> list Surface (frame animasi)
        self.anim_frames = []
        self.anim_i = -1      # -1 = tidak main; >=0 = frame saat ini
        self.anim_speed = 2   # tick per frame (30fps/2 = 15fps ~ retrace asli)
        self.anim_tick = 0
        self.anim_from_play = False   # True bila animasi dipicu dari Fill
        self.anim_limit = None        # frame maks (None=full); utk kasus GAGAL
        self.anim_fail = None         # indeks slot yg gagal (None=menang)
        self.reach_cache = {}         # gid -> list reach-index per slot mekanisme
        self.ballpath_cache = {}      # gid -> jalur bola layar
        self.running = False          # True saat bola berjalan (mode Fill gagal)
        self.run_fail_slot = None
        self.level = 0                # 0=Apprentice, 1=Master Builder
        self.timer = None             # detik tersisa (Mix Up); None = tanpa timer
        self.fill_mode = "mech"
        # Contraption Mix Up: rentetan kontraption 1..6 (lihat _mix_mulai)
        self.mix_sub = 0
        self.mix_sisa = None
        self.mix_skor = 0
        self.petunjuk = None          # hud.Petunjuk (hintmark), hanya mode 4 Master
        self.chosen_goal = 1
        self.slots = []       # slot mekanisme yg diisi saat PLAY
        self.cur_slot = 0
        self.cur_part = 0
        self.score = 0
        self.message = ""
        self.ball_path = []       # jalur bola saat "run"
        self.ball_i = -1          # indeks waypoint target; -1 = tidak jalan
        self.ball_pos = None      # posisi kontinu (float) utk gerak halus
        self.BALL_SPEED = 3.0     # pixel/frame

    # ---------- render tiap layar ke framebuffer ----------
    def draw(self, fb):
        fb.fill(cga.PALETTE[cga.BG_INDEX])
        if self.state == TITLE:
            self._title(fb)
        elif self.state == MENU:
            self._menu_tabel(fb, "utama")
        elif self.state == LEVEL:
            self._menu_tabel(fb, "level")
        elif self.state == GOAL:
            self._menu_tabel(fb, "goal")
        elif self.state == CONTRAPTION:
            self._contraption(fb)
        elif self.state == PLAY:
            self._play(fb)
        elif self.state == PLAYANIM:
            self._playanim(fb)
        elif self.state == REVIEW:
            self._review(fb)
        elif self.state == REVIEW_DETAIL:
            self._review_detail(fb)

    # ---------- Review Mechanisms (layout EKSAK dari data game) ----------
    def _rev_text(self, fb, recs):
        """Gambar daftar record teks/sprite pada posisi EKSAK (font 8x8)."""
        ar = {0x80: "<", 0x81: "", 0x82: ">", 0x83: ""}   # glyph panah -> ganti
        for r in recs:
            if r["kind"] != "text":
                continue
            s = "".join(ar.get(ord(c), c) for c in r["s"])
            text.draw(fb, s, r["x"], r["y"], color=r["col"], size=8)

    def _review(self, fb):
        """Layar intro Review Mechanisms + strip pemilih mekanisme.

        Latar dan teksnya BUKAN karangan port: `setupscr(mode=2, sub=1)` dengan
        `nbola = 0` (jalur Review menyetel `goal = 0` sebelum memanggilnya),
        lalu ketujuh baris teks dari tabel DGROUP lewat `cc/core/resensi.py`.
        Terukur terhadap tangkapan VRAM emulator: **64.000/64.000 piksel**.

        Strip di bawah memakai `drawpal()` yang sama dengan layar isian --
        sembilan sel 32x24 berukuran tetap, urutan dibalik, tepi diisi hitam.
        Port lama menggambar sembilan kotak selebar 34 piksel dengan segitiga
        penunjuk buatan sendiri.
        """
        latar = _rend.setupscr(_rend.new_fb(), 2, nbola=0, misc=self.k_misc, sub=1)
        kfb = _rend.KanvasFB(latar)
        for r in self.review_layout["intro"]:
            kfb.teks(r["s"], r["x"], r["y"], r["col"], r["sw"], r["sh"])
        fb.blit(_rend.to_surface(latar, pygame), (0, 0))

        k = _rend.KanvasSurface(fb, pygame)

        # Urutan strip dari `rowtab` @0x870, BUKAN dari daftar kategori yang
        # ditulis tangan: rowtab memakai 141 untuk Lever, kategori memakai 140,
        # dan thumbnail keduanya berbeda.
        rt = _pal.rowtab()

        def isi(i):
            if i is None:
                return None
            for r in self.k_mechs.recs:
                if self.k_mechs.cocok(r, rt[i]):
                    return self.k_mechs, r
            return None

        _pal.drawpal(k, self.rev_i, isi, len(rt))
        _pal.penunjuk(k, self.k_misc, (self.title_tick // _pal.PENUNJUK_TIK) & 1)

    def _review_detail(self, fb):
        """Halaman satu mekanisme — `revdet()` @0x3xxx:

            setsel(ttl[cur], def[cur]);                  <- tabel per mekanisme
            blit(ytop_ + spr[cur] * 0xc0, 0x30, 0x90, 0x18, 0x20);
            show(deftxt, 3);                             <- tiga baris tetap

        `setsel()` di sini fungsi yang SAMA dengan penggambar menu, dan
        `ttl` @0x14F6 / `def` @0x1508 adalah tabel yang sudah dibaca
        `cc/core/resensi.py`. Thumbnail 32x24 di (144, 48).
        """
        key = ("revdet", self.rev_i)
        if key not in self._scene_cache:
            item = [r["item"] for r in self.review_layout["mechs"][self.rev_i]]
            fbi = _rend.new_fb()
            k = _rend.KanvasFB(fbi)
            _menu.setsel(k, item, self.k_misc)
            tipe = MECH_CATEGORIES[self.rev_i][1][0]
            for r in self.k_mechs.recs:
                if self.k_mechs.cocok(r, tipe):
                    k.blit(self.k_mechs, r, 0x90, 0x30)
                    break
            for r in self.review_layout["fixed"]:
                k.teks(r["s"], r["x"], r["y"], r["col"], r["sw"], r["sh"])
            self._scene_cache[key] = _rend.to_surface(fbi, pygame)
        fb.blit(self._scene_cache[key], (0, 0))

    def _title(self, fb):
        """Layar judul = kontraption goal 128, animasinya dijalankan VM.

        Termasuk judul "CREATIVE CONTRAPTIONS" itu sendiri: ia digambar oleh
        opcode 0x11 DI DALAM skrip animasi, bukan oleh layar statis. Terukur
        53/53 frame byte-identik vs tangkapan VRAM emulator.
        """
        fr = self._anim_surfaces(128)
        if fr:
            fb.blit(fr[(self.title_tick // 2) % len(fr)], (0, 0))
            return
        surf = self._scene_surface(128, None, True)
        if surf is not None:
            fb.blit(surf, (0, 0))

    def _menu_tabel(self, fb, mana):
        """Ketiga layar menu, dari TABEL di DGROUP -- bukan disusun port.

        `mtabmn` @0x1D48 (menu utama), `mtablv` @0x1B74 (level), `menu`
        @0x1C28 (goal). Teks, posisi, warna, ikon, dan kotak sorotan semuanya
        dari sana; port hanya menggambarkannya.

        Terukur terhadap tangkapan VRAM emulator: menu utama **64.000/64.000
        piksel**. Versi lama menyusun sendiri header, jarak baris, dan kotak
        sorotan -- tidak ada satu pun angkanya yang berasal dari gim.
        """
        key = ("menu", mana)
        if key not in self._scene_cache:
            fbi, item = _menu.layar(self.k_misc, mana)
            self._scene_cache[key] = (_rend.to_surface(fbi, pygame), item)
        surf, item = self._scene_cache[key]
        fb.blit(surf, (0, 0))
        pilih = _menu.dipilih(item)
        if pilih and (self.title_tick // 20) & 1:
            i = pilih[min(self.sel, len(pilih) - 1)]
            _menu.kotak(_rend.KanvasSurface(fb, pygame), item[i])

    def _mode_layar(self):
        """Nomor mode gim asli untuk layar yang sedang tampil.

        Menu port berindeks 0..3; gim asli memakai 1..4 (0 = attract/judul).
        """
        return getattr(self, "mode_asli", 0) if self.state in (PLAY, PLAYANIM) else 0

    def _blit_scene(self, fb, gid, draw_mech=True, archs=None):
        """Gambar contraption. Dibangkitkan dari berkas aset, bukan dari daftar
        draw hasil tangkapan emulator.

        `archs` = himpunan arsip yang digambar; None -> pakai `draw_mech`.
        """
        if archs is not None:
            draw_mech = "MECHS" in archs
        vi = getattr(self, "cur_variant", 0)
        main_play = self.state in (PLAY, PLAYANIM)
        surf = self._scene_surface(
            gid, vi, draw_mech, mode=self._mode_layar(),
            seed=(self.cur_seed if main_play else 0),
            lastgoal=(self.cur_lastgoal if main_play else None),
            lastvar=(self.cur_lastvar if main_play else None))
        if surf is not None:
            fb.blit(surf, (0, 0))

    def _scene_surface(self, gid, vi, isi_mekanisme, seed=0, mode=None,
                       lastgoal=None, lastvar=None):
        """Layar contraption DIBANGKITKAN dari CONTRAP+GRAPH+MECHS+MISC.

        Urutan panggilannya meniru game asli: loadcon() mengundi varian
        struktur, pickpart() mengundi varian tiap objek zany, fillans()
        mencocokkan mekanisme lewat id. Dari `seed` yang sama, part yang
        terpilih SAMA dengan game asli -- terukur 384.000/384.000 piksel
        identik terhadap VRAM emulator untuk keenam goal.

        `vi` dipakai hanya kalau pemanggil memang ingin varian tertentu
        (mis. navigasi menu); kalau None, undian yang menentukan.
        """
        mode = self.mode_latar if mode is None else mode
        key = (gid, vi, bool(isi_mekanisme), seed, mode, lastgoal, lastvar)
        if key in self._scene_cache:
            return self._scene_cache[key]
        # Disusun oleh cc/core/adegan.susun() -- SAMA dengan yang dipakai
        # penggenerasi animasi. Dulu blok ini menyalin logikanya sendiri, dan
        # itu langsung menggigit: nama goal di pita atas ditambahkan di
        # adegan.susun() tapi layar ini tidak ikut berubah karena jalurnya beda.
        # `lastgoal`/`lastvar` diberikan hanya oleh layar BERMAIN, supaya
        # rantai undiannya sama persis dengan yang dipakai `start_play()` untuk
        # menyusun slot. Kalau keduanya None, `varian` yang dipaksakan --
        # itulah jalur pratinjau menu, yang memang ingin varian tertentu.
        _var, _parts, fb = _adg.susun(
            gid, self.k_graph, self.k_mechs, self.k_misc, self.k_anim,
            self.k_goals, seed=seed, mode=mode,
            varian=(None if lastgoal is not None else vi), sub=gid,
            isi=bool(isi_mekanisme), nbola=1,
            lastgoal=lastgoal, lastvar=lastvar)
        if fb is None:
            self._scene_cache[key] = None
            return None
        surf = _rend.to_surface(fb, pygame)
        self._scene_cache[key] = surf
        return surf

    def _contraption(self, fb):
        gid = self.goal_ids[self.sel] if self.state == GOAL else self.chosen_goal
        self._blit_scene(fb, gid, draw_mech=True)
        text.draw(fb, GOAL_NAMES.get(gid, "?"), 4, 2, color=0, size=12)
        # Teks GIM (@0x15e3), bukan karangan: "Press SPACE BAR to run the
        # contraption." Digambar di baris pesan gim, y = 0xc0.
        k = _rend.KanvasSurface(fb, pygame)
        k.teks(_hud.teks(_hud.S_JALANKAN), 0x10, 0xC0, 2)

    # ---------- Review: putar animasi run yang benar (PER-VARIAN) ----------
    def _jalur(self, gid, vi=0):
        """(jalur bola, jangkauan per part) dari VM -- bukan dari rekaman.

        Dulu ini dua berkas tangkapan: `ball<goal>_v<n>.json` untuk jalur bola
        dan `reach<goal>_v<n>.json` untuk "bola sampai di slot ini pada langkah
        ke berapa". Keduanya hasil MENJALANKAN game, dan keduanya hanya ada
        untuk varian yang kebetulan sempat ditangkap.
        """
        key = (gid, vi)
        if key not in self.ballpath_cache:
            self.ballpath_cache[key] = _adg.jalur_bola(
                gid, self.k_graph, self.k_mechs, self.k_misc,
                self.k_anim, self.k_goals)
        return self.ballpath_cache[key]

    def _anim_surfaces(self, gid, seed=0, varian=None):
        """Frame animasi DIBANGKITKAN dari berkas aset (VM), bukan diputar dari
        rekaman `port/cc/anim/*.dat`.

        Terukur vs tangkapan VRAM emulator: tujuh layar (goal 1..6 + judul 128)
        = 381/402 frame byte-identik, 99,9988% piksel; goal 4, 5, 6 dan layar
        judul 100% frame.
        """
        key = ("vm", gid, seed, varian)
        if key in self.anim_cache:
            return self.anim_cache[key]
        fbs = _adg.frames(gid, self.k_graph, self.k_mechs, self.k_misc,
                          self.k_anim, self.k_goals, seed=seed, varian=varian)
        surf = [_rend.to_surface(fb, pygame) for fb in fbs]
        self.anim_cache[key] = surf
        return surf

    def start_review(self, gid, from_play=False):
        self.chosen_goal = gid
        self.anim_from_play = from_play
        self.review_demo = False
        # animasi run ter-pack PER-VARIAN (goalN_vV.dat). Demo (bukan from_play) pakai v0.
        vi = self.cur_variant if from_play else 0
        key = (gid, vi)
        # Dulu di sini animasi DIPILIH dari rekaman dgn mencocokkan isi frame-0,
        # karena indeks varian `draws_goalN_vI.json` dan `goalN_vI.dat` tidak
        # sejajar. Sekarang tidak ada yang perlu dicocokkan: adegan dan animasi
        # dibangkitkan dari data yang sama, oleh undian yang sama.
        self.anim_frames = self._anim_surfaces(gid)
        self.anim_i = 0 if self.anim_frames else -1
        self.anim_tick = 0
        self.state = PLAYANIM

    def start_review_demo(self, rev_i):
        """Review "how it works": putar CONTRAPTION DEMO goal 7 varian=rev_i (mekanisme
        terpilih), berjalan sendiri & non-interaktif (spt game asli 0x3b2=7 + 18db)."""
        self.chosen_goal = 7
        self.cur_variant = rev_i
        self.anim_from_play = False
        self.review_demo = True
        self.anim_frames = self._anim_surfaces(7, varian=rev_i)
        self.anim_i = 0 if self.anim_frames else -1
        self.anim_tick = 0
        self.anim_fail = None
        self.anim_limit = None
        self.state = PLAYANIM

    def _playanim(self, fb):
        if 0 <= self.anim_i < len(self.anim_frames):
            fb.blit(self.anim_frames[self.anim_i], (0, 0))
        else:
            self._blit_scene(fb, self.chosen_goal, draw_mech=True)
        last = len(self.anim_frames) - 1
        if self.anim_limit is not None:
            last = min(last, self.anim_limit)
        done = self.anim_i < 0 or self.anim_i >= last
        if self.review_demo:                          # DEMO "how it works" (non-interaktif)
            text.draw(fb, "%s - how it works" % MECH_CATEGORIES[self.rev_i][0],
                      4, 2, color=0, size=11)
            # Teks GIM: "Press SPACE BAR to see it work." (@0x14b2) dan
            # "Press ENTER to select / another mechanism." (@0xaab/@0xac1).
            k = _rend.KanvasSurface(fb, pygame)
            if done:
                k.teks(_hud.teks(_hud.S_PILIH_MEK1), 0x40, 0xAC, 2)
                k.teks(_hud.teks(_hud.S_PILIH_MEK2), 0x40, 0xB6, 2)
                k.teks(_hud.teks(_hud.S_LIHAT_LAGI), 0x10, 0xC0, 2)
            return
        text.draw(fb, GOAL_NAMES.get(self.chosen_goal, "?"), 4, 2, color=0, size=12)
        if done and self.anim_fail is not None:      # GAGAL di slot tertentu
            # Teks GIM: pesan salah dari DGROUP, lalu "Press SPACE BAR to
            # try again." (@0xa5d) -- yang dipakai `prompts()` untuk kasus
            # gagal. "ESC = keep building" itu karangan port.
            k = _rend.KanvasSurface(fb, pygame)
            _hud.gambar_pesan(k, _hud.pesan_salah(
                self.slots[self.anim_fail]["arch"] == "GRAPH",
                0x41 + self.anim_fail))
            k.teks(_hud.teks(_hud.S_COBA), 0x28, 0xC0, 2)
        elif done and self.anim_from_play:           # MENANG
            # Pesan akhir goal memakai `prompts()` gim asli: teks, posisi, dan
            # percabangannya dari DGROUP + prompts.c, bukan karangan port.
            k = _rend.KanvasSurface(fb, pygame)
            self.nbola = _hud.prompts(k, self.mode_asli, self.chosen_goal,
                                      0, self.level + 1, self.nbola)
            self._hud(fb)
            if self.mode_asli == 4 and self.nbola <= 0:
                _hud.showhint(k, self.k_misc, self.mode_asli)
        else:
            msg = "SPACE = replay  -  ESC = menu" if done else "Running..."
            text.draw_center(fb, msg, 190, color=3, size=10)

    # ---------- pemilihan varian ----------
    #
    # ⚠ DIBUANG (2026-08-02): `_pick_variant()` memilih varian dengan
    # `random.choice` atas daftar "semua kecuali yang terakhir untuk goal ini",
    # memakai satu entri per goal. Gim tidak begitu:
    #
    #     do { pick = rnd(cnt) + first; }
    #     while (lastgoal == sub && cnt >= 2 && pick == lastvar);
    #
    # `lastgoal`/`lastvar` adalah SEPASANG global, bukan satu per goal -- jadi
    # goal 1, lalu 2, lalu 1 lagi BOLEH mengulang varian. Dan undiannya memakai
    # RNG gim yang sama dengan pemilihan part, sehingga pengulangan menggeser
    # seluruh rantai sesudahnya. Sekarang `start_play()` yang mengerjakannya.

    # ---------- Contraption Mix Up: RENTETAN kontraption, bukan satu ----------
    #
    # `main_.c` case 4 tidak pernah memanggil `goalmenu()`. Ia memasang
    # `sub = 0; goal = 6; pickmax();` lalu gelung `while (goal > 0)` yang tiap
    # putaran menaikkan `sub` dan memuat kontraption berikutnya. Jadi Mix Up
    # memainkan kontraption 1..6 BERURUTAN.
    #
    # Level menentukan panjangnya, dan bentuknya halus: di puncak gelung ada
    # `if (lvl == 1) goal = 1;` dan di ekornya `if (lvl == 1) goal++;` sebelum
    # `goal--`. Pada Apprentice (lvl 1) keduanya saling meniadakan sehingga
    # gelungnya TAK BERUJUNG; pada Master (lvl 2) `goal` menghitung mundur 6
    # putaran.

    def _mix_mulai(self):
        self.mix_sub = 0
        self.mix_sisa = None if self.level == 0 else 6
        self.mix_skor = 0
        self.petunjuk = None
        self._mix_ronde()

    def _mix_ronde(self):
        self.mix_sub += 1
        if self.mix_sub > 6:
            self.mix_sub = 1                  # Apprentice: berputar lagi
        skor = self.mix_skor
        self.start_play(self.mix_sub, fill="both")
        self.score = skor                     # skor TERKUMPUL lintas ronde
        # `pickmax()` dipanggil SEKALI saat mode dimasuki (`main_.c`), dan
        # `count` yang dikurangi tiap panggilan ikut lintas ronde -- karena itu
        # objeknya dibuat sekali lalu dipakai ulang.
        #
        # Tiap RONDE, `runplay()` menyetel ulang keadaan penandanya:
        # `timer = -1; lvl6 = nmax; range = tx - (rnd(200)*0x17/199 + 2);`
        # Dua nilai itu dulu salah di port (lvl6 mulai 0, range dipatok);
        # sekarang `mulai_ronde()` yang mengerjakannya, memakai RNG gim yang
        # sama supaya `range` ikut rantai yang benar.
        nmax = max(1, len(self._postab()))
        if self.petunjuk is None:
            self.petunjuk = _hud.Petunjuk(_rng.Rng(self.rng_seed), nmax)
        self.petunjuk.rng = _rng.Rng(self.rng_seed)
        self.petunjuk.mulai_ronde(nmax, tx=self.tx or 0x140, tinit=True)
        self.rng_seed = self.petunjuk.rng.state()

    def _mix_ronde_selesai(self):
        """SPACE sesudah animasi menang: lanjut ke kontraption berikutnya."""
        self.mix_skor = self.score
        if self.mix_sisa is not None:
            self.mix_sisa -= 1
            if self.mix_sisa <= 0:
                self.state = MENU
                self.sel = 0
                return
        self._mix_ronde()

    # ---------- mode PLAY: Fill Mechanisms / Fill Zany / Mix Up (both) ----------
    def start_play(self, gid, fill="mech"):
        vs = self.k_goals.get(gid) or []
        self.fill_mode = fill                     # "mech" | "zany" | "both" (Mix Up)
        self.slots = []
        self.palette = []

        # Record sprite per slot datang dari UNDIAN yang sama dengan game
        # (loadcon untuk varian struktur, pickpart untuk objek zany, fillans
        # untuk mekanisme) -- bukan dari rekaman `draws_goal*.json`.
        #
        # ⭐ SATU rantai RNG yang HIDUP TERUS, persis seperti gim. Dulu tiap
        # `start_play` memulai `Rng(0)` baru, jadi kontraption yang sama selalu
        # memberi part yang sama; dan variannya dipilih `random.choice`, bukan
        # aturan gim. `loadcon.c` mengundinya begini:
        #
        #     do { pick = rnd(cnt) + first; }
        #     while (lastgoal == sub && cnt >= 2 && pick == lastvar);
        #
        # Perhatikan `lastgoal == sub`: yang dihindari hanya pengulangan
        # BERUNTUN pada goal yang SAMA -- memuat goal 1, lalu 2, lalu 1 lagi
        # BOLEH memberi varian yang sama, karena `lastgoal` sudah jadi 2.
        # Pengulangan itu juga MEMAJUKAN seed satu undian lagi, sehingga
        # pemilihan part sesudahnya ikut bergeser.
        #
        # Terukur: dgn seed/lastgoal/lastvar yang dibaca dari memori gim,
        # `susun()` menghasilkan layar bermain yang IDENTIK 64.000/64.000
        # piksel -- termasuk arenanya (`python work/test_play.py`).
        # ⚠ Keadaan SEBELUM undian disimpan terpisah (`cur_*`). Layar
        # dibangkitkan ulang belakangan lewat `_scene_surface()`, dan ia harus
        # MENGULANG undian yang sama -- kalau diberi keadaan SESUDAHNYA,
        # aturan anti-ulang justru memaksa varian yang BERBEDA dari slot yang
        # sudah disusun di sini. Bug "layar design != layar run" persis lahir
        # dari ketidakcocokan semacam ini.
        # ⚠ Blok ini dulu MENYALIN seluruh rantai undian dari adegan.susun().
        # Dua salinan yang harus tetap sama adalah cara paling mudah membuat
        # "layar design != layar run": begitu satu sisi menambah langkah (mis.
        # setmark()/setzany() yang memakai RNG), yang lain diam-diam melenceng.
        # Sekarang keduanya memakai `adegan.susun_lengkap()` yang SAMA.
        #
        # Keadaan SEBELUM undian disimpan terpisah (`cur_*`): layar
        # dibangkitkan ulang belakangan lewat `_scene_surface()` dan harus
        # MENGULANG undian yang sama. Diberi keadaan SESUDAHNYA, aturan
        # anti-ulang justru memaksa varian yang BERBEDA dari slot di sini.
        seed = self.rng_seed
        self.cur_seed = seed
        self.cur_lastgoal, self.cur_lastvar = self.lastgoal, self.lastvar
        mode_asli = self.mode + 1
        _var, _parts, _fb, pil = _adg.susun_lengkap(
            gid, self.k_graph, self.k_mechs, self.k_misc, self.k_anim,
            self.k_goals, seed=seed, mode=mode_asli, sub=gid,
            # Apa yang KOSONG berbeda per mode, dan ketiganya TERUKUR:
            #   mech  slot mekanisme = petak abu, objek zany utuh
            #   zany  mekanisme utuh, objek zany TIDAK digambar (kecuali yang
            #         terakhir -- itu gambar hasil goal, bukan teka-teki)
            #   both  KEDUANYA tetap digambar; yang "kosong" di Mix Up adalah
            #         slot BERTANDA, dan `pickpart()` memberinya record
            #         kelompok kedua (id >= 0x80) -- sprite PENGGANTI, bukan
            #         petak kosong. Karena itu isi/isi_zany dua-duanya True.
            isi=(fill != "mech"), isi_zany=(fill != "zany"),
            nbola=1, lastgoal=self.lastgoal, lastvar=self.lastvar,
            lvl=self.level + 1)
        vi = pil["vi"]
        rng = pil["rng"]
        self.lastgoal, self.lastvar = gid, vi
        self.cur_variant = vi
        var = vs[vi] if vi < len(vs) else vs[0]
        tz, tm = pil["tz"], pil["tm"]
        jz, jm = pil["jz"], pil["jm"]
        selz = [None if i is None else tz[i]["idx"] for i in pil["selz"]]
        selm = [None if i is None else tm[i]["idx"] for i in pil["selm"]]
        # Rantainya MAJU untuk kontraption berikutnya -- di gim `seed` @0x71a
        # memang satu nilai yang terus berjalan, tidak pernah di-reset.
        self.rng_seed = rng.state()

        def add_slots(parts, arch):
            dipilih = selm if arch == "MECHS" else selz
            for k, (y, x, typ) in enumerate(parts):
                idx = dipilih[k] if k < len(dipilih) and dipilih[k] is not None else -1
                self.slots.append(dict(y=y, x=x, correct=typ, filled=None, tries=0,
                                       arch=arch, sprite=idx))
        # entri palet = (nama, ids, arch, sprite_idx), satu per RECORD yang
        # ditawarkan `mkpal()` -- bukan per kategori tulisan tangan.
        if fill in ("mech", "both"):
            add_slots(var["mech"], "MECHS")
            # ⭐ BERAPA BANYAK PILIHAN yang ditawarkan tergantung MODE, dan port
            # lama selalu menawarkan kesembilan kategori MECH_CATEGORIES.
            # Aturannya `mkpal()` @0x3909, kini ditiru utuh di
            # cc/core/pick.py:palet_mekanisme():
            #
            #     if (lvl3 != 1 || base[i*0xc] == tab[j*3+2]) { ...masuk palet }
            #
            # `lvl3 == 1` di mode 1/2/3 -> hanya part yang DIBUTUHKAN;
            # `lvl3 == 3` di mode 4    -> SELURUH daftar, lalu dikocok & dedup.
            #
            # TERUKUR vs `nmech` @0x3ac (OBSERVE=... + CC_NOSKIP=1, tangkap di
            # RET drawpal 0x3C4E):
            #     Fill in Mechanisms  goal 1 -> 3, goal 2 -> 4, goal 4 -> 3
            #     Contraption Mix Up  goal 1 -> 13
            # dan tiruan di pick.py memberi 3, 4, 3, 13 juga.
            #
            # ⚠ Pencocokannya EKSAK per id record (`ord1[c1] != rec1[3*c1+2]`
            # di main_.c), bukan per kategori. MECH_CATEGORIES sekarang hanya
            # dipakai untuk LABEL teksnya.
            # ⚠ `mkpal()` menyusuri `base`, dan `base` BERBEDA menurut mode --
            # `main_.c` memanggil `loadarc(mechfh, base, lvl3 == 1 ? 0 : 1, ...)`:
            #     lvl3 == 1 -> tabel DISARING + DIPADATKAN (hanya jenis terpakai)
            #     lvl3 != 1 -> direktori PENUH
            # Terukur lewat CC_VSPTR=73a: goal 1 mode isian `base` = 6 record,
            # mode Mix Up = 30 record (seluruh direktori MECHS).
            lvl3 = 3 if fill == "both" else 1
            base = tm if lvl3 == 1 else self.k_mechs.recs
            for r in (base[i] for i in
                      _pick.palet_mekanisme(base, jm, lvl3, rng)):
                ci = self._cat_index(r["id"])
                nm = MECH_CATEGORIES[ci][0] if ci is not None else "Mechanism"
                self.palette.append((nm, (r["id"],), "MECHS", r["idx"]))
        if fill in ("zany", "both"):
            add_slots(var["zany"], "GRAPH")
            seen = set()
            for s in self.slots:
                if s["arch"] == "GRAPH" and s["correct"] not in seen:
                    seen.add(s["correct"])
                    idx = s["sprite"]
                    if idx < 0:
                        rec = self.graph.first_of_major(s["correct"])
                        idx = rec["idx"] if rec else -1
                    self.palette.append(("Zany Object", (s["correct"],), "GRAPH", idx))
        # ⚠ DIBUANG: dulu di sini ada `random.shuffle(self.palette)` dengan
        # komentar "spt Fisher-Yates FUN_1000_3909". Kocokannya sekarang
        # dikerjakan `pick.palet_mekanisme()` DENGAN RNG GIM, jadi kocokan
        # kedua ini justru MERUSAKNYA -- urutan yang sudah benar diacak lagi.
        # Terukur: dgn seed gim, mkpal memberi record [26, 2, 17]; sesudah
        # kocokan Python jadi [17, 26, 2], dan strip meleset 738 piksel.
        #
        # Entri ZANY di bawahnya mengikuti urutan slot. Di gim kandidat zany
        # tidak muncul di strip sama sekali -- ia berputar DI DALAM kotak lewat
        # `pickvar()` -- jadi urutannya belum pernah diadu; jangan dikocok
        # sembarangan hanya supaya "terlihat acak".
        self.fixed_archs = () if fill == "both" else \
            (("GRAPH",) if fill == "mech" else ("MECHS",))
        self.part_word = "Object" if fill == "zany" else "Part"
        # timer hanya utk Mix Up (Apprentice ~5.5mnt / Master ~2.5mnt)
        self.timer = (330.0 if self.level == 0 else 150.0) if fill == "both" else None
        # Keadaan penilaian, nama & nilai awal dari main_.c dan gdata.c:
        #   mode_asli  penomoran gim asli = indeks menu + 1 (4 = Mix Up)
        #   nbola      global `goal` @0x718 -- JUMLAH BOLA; 6 di Mix Up
        #   zcnt       @0x7e6 penghitung kesalahan untuk SELURUH kontraption
        #   tx         @0x7ee waktu TERSISA dalam piksel; main_ menyetel 0x140
        #   range/count/cur2  keadaan petunjuk Master (pickmax/hintmark)
        self.mode_asli = self.mode + 1
        self.nbola = 6 if fill == "both" else 1
        self.zcnt = 0
        self.tx = 0x140 if fill == "both" else 0
        self.range_ = 0x140 - 0x14
        self.count = 4
        self.cur2 = 0
        self.cur_slot = 0
        self.cur_part = 0
        self.score = 0
        # ⚠ Baris pesan gim KOSONG saat mulai bermain -- terukur di tangkapan
        # VRAM ketiga mode. "Pick parts to fill the empty boxes." adalah
        # karangan port; kalimat itu tidak ada di DGROUP sama sekali.
        self.message = ""
        self.chosen_goal = gid
        self.running = False
        self.run_fail_slot = None
        self.ball_i = -1
        self.ball_pos = None
        self.anim_fail = None
        self.anim_limit = None
        self.review_demo = False
        self.state = PLAY

    def _postab(self):
        """`postab[]` @0x3b6 kontraption yang sedang dimainkan.

        Isinya pasangan (a, b) posisi label huruf, satu per slot -- sumber yang
        SAMA dengan `render.labels()`. Di gim ia diisi `loadcon()`; di port ia
        `countA` hasil `contrap.parse()`, tersimpan sebagai `var["pos"]`.
        """
        vs = self.k_goals.get(self.chosen_goal) or []
        if not vs:
            return []
        var = vs[self.cur_variant] if self.cur_variant < len(vs) else vs[0]
        return var.get("pos") or []

    def _arch(self, name):
        return self.mechs if name == "MECHS" else self.graph

    def _cat_index(self, typ):
        """indeks MECH_CATEGORIES yg berisi tipe (id_major) ini."""
        for i, (nm, ids) in enumerate(MECH_CATEGORIES):
            if typ in ids:
                return i
        return None

    def _hud(self, fb):
        """Bilah status gim asli: skor di pita atas + bilah timer Mix Up.

        Digambar lewat `render.KanvasSurface` supaya `cc/core/hud.py` tidak
        perlu versi kedua -- aturan penempatannya satu, sasarannya dua.
        """
        k = _rend.KanvasSurface(fb, pygame)
        # ⚠ Pojok kanan pita atas menampung SATU dari dua hal, dan `f171f()`
        # yang memilih: skor kalau mode == 4, nama goal kalau bukan. Port lama
        # selalu memanggil `showsc()`, sehingga di mode isian skor "0"
        # tertimpa di atas nama goal -- terlihat sebagai "00' Em" alih-alih
        # "Up and At 'Em".
        _hud.judul_atau_skor(k, self.mode_asli, self.chosen_goal, self.score)
        if self.mode_asli == 4:
            _hud.timedrw(k, self.tx, self.mode_asli, self.nbola, self.chosen_goal)

    def _play(self, fb):
        """Layar bermain, digambar dengan ATURAN GIM ASLI.

        Port lama mengarang kotak sorotan, panah, dan bilah status sendiri.
        Sekarang urutannya mengikuti `main_.c`:

            setupscr() + kontraption   latar & pita (mode 2/3/4 -> pita bawah
                                       BIRU TUA, bukan cyan)
            f15d0()                    huruf A.. di postab
            drawslot()                 slot KOSONG = fillrect(x+1, y, x+0x1e,
                                       y+0x17, 3) -- petak PENUH warna 3
            drawpal()                  strip pemilih part
            drawbox()                  kotak sorotan, EMPAT garis XOR warna 3
            f171f()/showsc()/timedrw() pita atas

        Terukur vs tangkapan VRAM emulator (goal 1 mode isian, tangkap di RET
        drawpal 0x3C4E): pita atas 2.560/2.560, pita bawah 12.800/12.800
        (termasuk strip), ketiga kotak slot kosong 2.160/2.160.
        """
        gid = self.chosen_goal
        # part TETAP tampil (mech mode: zany scenery; zany: mekanisme; both: tidak ada)
        self._blit_scene(fb, gid, archs=self.fixed_archs)
        k = _rend.KanvasSurface(fb, pygame)
        inbox = (self.fill_mode == "zany")   # Zany: kandidat berputar DI DALAM kotak

        # --- slot: kosong = petak warna 3, terisi = sprite-nya ---------------
        def isi(i):
            s = self.slots[i]
            if s["filled"] is None:
                return None
            arc = self.k_mechs if s["arch"] == "MECHS" else self.k_graph
            if s["sprite"] is not None and s["sprite"] >= 0:
                return arc, arc.recs[s["sprite"]]
            return None
        _rend.drawslot(k, [(s["y"], s["x"]) for s in self.slots], isi)

        # Zany: kandidat yang sedang diputar tampil DI DALAM kotaknya
        # (`pickvar()`), bukan di strip.
        if inbox and 0 <= self.cur_slot < len(self.slots):
            s = self.slots[self.cur_slot]
            if s["filled"] is None:
                _nm, _ids, pa, pidx = self.palette[self.cur_part]
                arc = self.k_mechs if pa == "MECHS" else self.k_graph
                if pidx >= 0:
                    k.blit(arc, arc.recs[pidx], s["x"], s["y"])

        # --- huruf penanda slot: f15d0(), warna 3 di postab ------------------
        vs = self.k_goals.get(gid) or []
        var = vs[self.cur_variant] if self.cur_variant < len(vs) else (vs[0] if vs else None)
        if var:
            for i, (a, b) in enumerate(var.get("pos") or []):
                warna = 3
                # `hintmark()`: slot yang sedang ditunjuk memakai warna pilihan
                # fungsi itu -- 0 = petunjuk sungguhan (menyalakan `mflag`,
                # syarat bonus bola), 2 = penanda biasa.
                if (self.petunjuk is not None and self.mode_asli == 4
                        and self.level == 1 and i == self.petunjuk.cur2):
                    warna = self.petunjuk.warna
                k.teks(chr(0x41 + i), b, a, warna)

        # --- strip pemilih part ---------------------------------------------
        if not inbox:
            self._palette_strip(fb)

        # --- kotak sorotan: EMPAT garis XOR warna 3 --------------------------
        if 0 <= self.cur_slot < len(self.slots):
            s = self.slots[self.cur_slot]
            _rend.drawbox(k, s["y"], s["x"])

        # --- pita atas: skor / nama goal / bilah timer -----------------------
        self._hud(fb)

        # bola saat "run" (di AREA MAIN, di atas contraption)
        if self.ball_pos is not None:
            bx, by = int(self.ball_pos[0]), int(self.ball_pos[1])
            pygame.draw.circle(fb, cga.PALETTE[2], (bx, by), 2)
            fb.set_at((bx, by), cga.PALETTE[3])
        # --- baris pesan --------------------------------------------------
        # Port lama menaruhnya di y=3, DI ATAS pita atas -- dan itu menimpa
        # nama goal yang digambar `f171f()`, terlihat sebagai "00' Em" alih-alih
        # "Up and At 'Em".
        #
        # `setupscr()` membersihkan satu baris teks cyan tepat untuk keperluan
        # ini: `fillrect(0x10, 0xc0, 0x12f, 199, 1)` = y 192..199, x 16..303,
        # yaitu SATU baris 8 piksel selebar 36 karakter. Dan pesan pembuka gim
        # "Pick parts to fill the empty boxes." panjangnya tepat 35 karakter.
        #
        # ⭐ DIKONFIRMASI dari sumber byte-exact, bukan diterka: `prompts()`
        # menulis SELURUH pesannya di baris itu juga --
        #     text(S_ULANG,  0x10, 0xc0, 2)
        #     text(S_COBA,   0x28, 0xc0, 2)
        #     text(S_TERUS4, 0x38, 0xc0, 2)
        # y = 0xc0 dan x mulai 0x10, WARNA 2. Jadi baris pesan gim memang di
        # sana, dan warnanya magenta -- bukan 0 seperti tebakan pertama.
        #
        # ⚠ Yang masih belum bisa diukur: pesan DALAM permainan ("Part A does
        # not work.") keluar lewat `printf()` @0x6a48 dari MC.LIB. Emulator
        # dilengkapi `CC_TRACEDOS=1` untuk merekam keluaran teks DOS/BIOS, dan
        # hasilnya NOL peristiwa -- `printf` memang tak pernah terpanggil di
        # jalur yang bisa dijangkau harness. Jadi posisinya diturunkan dari
        # `prompts()`, yang menulis di baris yang sama.
        if self.message:
            _hud.gambar_pesan(k, self.message)

    def _palette_strip(self, fb):
        """Strip pemilih part -- `drawpal()` gim asli, lewat cc/core/palet.py.

        Port lama menggambar SELURUH daftar berjajar dengan lebar sel yang
        menyusut mengikuti banyaknya pilihan, dan menyorot yang terpilih dengan
        kotak magenta. Aslinya: jendela geser sembilan sel 32x24 berukuran
        TETAP, berpusat di pilihan sekarang, urutannya DIBALIK (item pertama
        di kanan), dan tepi di luar daftar diisi HITAM.
        """
        k = _rend.KanvasSurface(fb, pygame)

        def isi(i):
            nm, pids, parch, pidx = self.palette[i]
            if pidx < 0:
                return None
            arc = self.k_mechs if parch == "MECHS" else self.k_graph
            return arc, arc.recs[pidx]

        _pal.drawpal(k, self.cur_part, isi, len(self.palette))
        _pal.penunjuk(k, self.k_misc, (self.title_tick // _pal.PENUNJUK_TIK) & 1)

    def tick(self):
        """Advance animasi review + gerak bola PLAY."""
        if self.state == TITLE:
            self.title_tick += 1
            return
        if self.state == REVIEW:
            self.rev_tick += 1
            if self.rev_tick >= 6:       # ~5 fps animasi mekanisme
                self.rev_tick = 0
                self.rev_frame += 1
            return
        if self.state == PLAYANIM:
            last = len(self.anim_frames) - 1
            if self.anim_limit is not None:
                last = min(last, self.anim_limit)
            if 0 <= self.anim_i < last:
                self.anim_tick += 1
                if self.anim_tick >= self.anim_speed:
                    self.anim_tick = 0
                    self.anim_i += 1
            return
        # Mix Up: timer berjalan mundur saat membangun (bukan saat bola jalan)
        if self.state == PLAY and self.timer is not None and not self.running:
            self.timer -= 1.0 / 30.0
            # `tx` @0x7ee = waktu TERSISA dalam piksel (0x140 = penuh), bukan
            # detik. `timebar()` di gim asli menguranginya satu tiap tik; di
            # sini diturunkan dari sisa detik supaya lajunya sama.
            _total = 330.0 if self.level == 0 else 150.0
            self.tx = max(0, int(0x140 * max(0.0, self.timer) / _total))
            if self.timer <= 0:
                self.timer = 0
                self.message = ""      # gim tidak menulis apa pun di sini
            # `hintmark()` dipanggil dari gelung pemilih part (review.c), yaitu
            # tempat yang sama dengan `timebar()` -- bukan dari penggambar.
            # Ia hanya berbuat sesuatu di mode 4 level Master Builder.
            if self.petunjuk is not None:
                self.petunjuk.tik(self.mode_asli, self.level + 1, self.tx,
                                  self._postab())
        if self.state != PLAY or self.ball_i < 0 or self.ball_pos is None:
            return
        tx, ty = self.ball_path[self.ball_i]
        cx, cy = self.ball_pos
        dx, dy = tx - cx, ty - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= self.BALL_SPEED:
            self.ball_pos = (float(tx), float(ty))
            self.ball_i += 1
            if self.ball_i >= len(self.ball_path):
                self.ball_i = -1
                self.running = False
                if self.run_fail_slot is not None:
                    # Teks GIM, dari DGROUP @0x9dd -- lengkap dgn tujuh spasi
                    # depannya. Ekor "Fix it and try again." itu karangan port.
                    self.message = _hud.pesan_salah(
                        self.slots[self.run_fail_slot]["arch"] == "GRAPH",
                        0x41 + self.run_fail_slot)
        else:
            self.ball_pos = (cx + dx / dist * self.BALL_SPEED,
                             cy + dy / dist * self.BALL_SPEED)

    def _back_to_goal(self):
        """Kembali ke pilihan GOAL/tema (spt game asli: contraption selesai/ESC -> 3322),
        mode & level dipertahankan. Sorot goal yg barusan dimainkan."""
        self.state = GOAL
        self.sel = self.goal_ids.index(self.chosen_goal) if self.chosen_goal in self.goal_ids else 0

    def _play_key(self, k):
        if k == pygame.K_ESCAPE:
            if self.mode_asli == 4:
                self.state = MENU; self.sel = 0   # Mix Up tidak punya layar GOAL
            else:
                self._back_to_goal()         # ESC saat main -> pilihan tema (GOAL)
            return
        if k == pygame.K_SPACE:               # RUN: bola keluar & jalan (spt game asli)
            if self.running:
                return
            if self.timer is not None and self.timer <= 0:
                return
            # ⭐ Di sinilah gim memeriksa jawaban -- bukan saat part ditaruh.
            # `animvm()` menyusuri slot berurutan; yang PERTAMA salah
            # menghentikan animasi, menaikkan `zcnt`, dan mencetak pesannya.
            # Slot yang masih KOSONG juga dihitung salah.
            wrong = [i for i, s in enumerate(self.slots) if s["filled"] != s["correct"]]
            if wrong:
                self.zcnt += 1              # animvm: zcnt++ di cabang salah
                self.slots[wrong[0]]["tries"] += 1
            if not wrong:
                # lengkap & benar -> MENANG. Penilaian mengikuti animvm.c case
                # 0x10: SATU penilaian per kontraption dari `zcnt`, dan HANYA
                # di mode 4 (Contraption Mix Up). Fill in Mechanisms dan Fill
                # in Zany Objects memang latihan tanpa skor di gim asli.
                self.score, self.nbola, _tampil = _hud.skor_akhir(
                    self.score, self.zcnt, self.mode_asli, self.level + 1,
                    self.chosen_goal, self.cur2, self.tx, self.nbola)
                self.anim_fail = None
                self.anim_limit = None
                self.start_review(self.chosen_goal, from_play=True)
            elif self.fill_mode == "mech" and self._jalur(self.chosen_goal, self.cur_variant)[0]:
                # GAGAL: bola jalan DI ATAS build kamu, berhenti di kotak salah
                # yang lebih dulu DICAPAI RANTAI -- belum tentu kotak salah
                # pertama menurut urutan slot di CONTRAP.
                bp, reach = self._jalur(self.chosen_goal, self.cur_variant)
                def slot_reach(i):
                    s = self.slots[i]
                    return reach.get((s["x"], s["y"]))
                mwrong = [i for i in wrong if slot_reach(i) is not None]
                fs = min(mwrong, key=slot_reach) if mwrong else wrong[0]
                end = ((slot_reach(fs) if slot_reach(fs) is not None else len(bp) - 1)) + 1
                self.ball_path = bp[:max(2, end)]
                self.ball_pos = (float(self.ball_path[0][0]), float(self.ball_path[0][1]))
                self.ball_i = 1
                self.run_fail_slot = fs
                self.running = True
                self.message = ""
            else:
                # zany/both: beri tahu masih ada yg salah/kosong
                self.message = _hud.pesan_salah(
                    self.slots[wrong[0]]["arch"] == "GRAPH", 0x41 + wrong[0])
            return
        if self.running:                      # saat bola jalan, hanya SPACE/ESC di atas
            return
        if k == pygame.K_LEFT:
            self.cur_part = (self.cur_part - 1) % len(self.palette)
        elif k == pygame.K_RIGHT:
            self.cur_part = (self.cur_part + 1) % len(self.palette)
        elif k in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
            empties = [i for i, s in enumerate(self.slots) if s["filled"] is None]
            if empties:
                if self.cur_slot in empties:
                    j = empties.index(self.cur_slot)
                    self.cur_slot = empties[(j + (1 if k != pygame.K_UP else -1)) % len(empties)]
                else:
                    self.cur_slot = empties[0]
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._place()

    def _place(self):
        """Taruh part terpilih di kotak sekarang.

        ⭐ SELALU BERHASIL, dan itu perbaikan kesetiaan. Port dulu MENOLAK part
        yang salah di tempat dan langsung bilang "does not work" -- padahal gim
        menerima apa pun yang ditaruh dan baru memberi tahu saat kontraption
        DIJALANKAN. Satu-satunya tempat gim memeriksa jawaban adalah `animvm()`:

            if (ord1[c1] != rec1[3 * c1 + 2]) { ...; zcnt++; printf(msgmech); }

        Tidak ada pemeriksaan di `pickloop()`/`review()` sama sekali. Jadi
        seluruh ketegangan mode ini -- "aku baru tahu salah setelah dijalankan"
        -- hilang di port lama.

        `zcnt` juga ikut pindah: ia dinaikkan saat MENJALANKAN, bukan saat
        menaruh, karena di gim `animvm` yang menaikkannya.
        """
        s = self.slots[self.cur_slot]
        if s["filled"] is not None:
            return
        _nm, pids, _arch, pidx = self.palette[self.cur_part]
        s["filled"] = pids[0]              # apa pun yang dipilih, diterima
        if pidx >= 0:
            s["sprite"] = pidx
        self.message = ""                  # gim DIAM saat part ditaruh
        empties = [i for i, sl in enumerate(self.slots) if sl["filled"] is None]
        if empties:
            self.cur_slot = empties[0]

    # ---------- input ----------
    def key(self, k):
        if self.state == TITLE:
            if k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = MENU; self.sel = 0
        elif self.state in (MENU, LEVEL, GOAL):
            n = {MENU: len(MENU_OPTIONS), LEVEL: len(LEVELS),
                 GOAL: len(self.goal_ids)}[self.state]
            if k in (pygame.K_DOWN, pygame.K_UP):
                self.sel = (self.sel + (1 if k == pygame.K_DOWN else -1)) % n
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._choose()
            elif k == pygame.K_ESCAPE:
                self.state = MENU if self.state != MENU else TITLE
                self.sel = 0
        elif self.state == CONTRAPTION:
            if k == pygame.K_ESCAPE:
                self.state = MENU; self.sel = 0
            elif k == pygame.K_SPACE:
                self.start_review(self.chosen_goal)
        elif self.state == PLAYANIM:
            if self.review_demo:                 # demo "how it works" (non-interaktif)
                if k == pygame.K_ESCAPE:
                    self.review_demo = False; self.state = MENU; self.sel = 0
                elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.review_demo = False; self.state = REVIEW   # pilih mekanisme lain
                elif k == pygame.K_SPACE:        # ulang demo
                    self.anim_i = 0 if self.anim_frames else -1
                    self.anim_tick = 0
                return
            if k == pygame.K_ESCAPE:
                if self.anim_fail is not None:   # gagal dari Fill -> lanjut membangun
                    self.state = PLAY
                    self.message = _hud.pesan_salah(
                        self.slots[self.anim_fail]["arch"] == "GRAPH",
                        0x41 + self.anim_fail)
                    self.anim_fail = None
                elif self.anim_from_play and self.mode_asli == 4:
                    # Mix Up tidak punya pemilih goal untuk dituju: ESC di
                    # main_.c case 4 memasang cursel = -1 dan keluar ke menu.
                    self.state = MENU; self.sel = 0
                elif self.anim_from_play:        # MENANG di Fill -> kembali ke tema (GOAL)
                    self._back_to_goal()
                else:                            # demo dari CONTRAPTION -> menu
                    self.state = MENU; self.sel = 0
            elif k == pygame.K_SPACE:
                if self.anim_from_play and self.mode_asli == 4 \
                        and self.anim_fail is None:
                    # `do { m = getkey(); } while (m != 0x20 && m != 0x1b);`
                    # SPACE = lanjut ke kontraption berikutnya, bukan ulangi.
                    self._mix_ronde_selesai()
                else:                            # replay
                    self.anim_i = 0 if self.anim_frames else -1
                    self.anim_tick = 0
        elif self.state == REVIEW:               # browse: pilih mekanisme
            if k == pygame.K_ESCAPE:
                self.state = MENU; self.sel = 0
            elif k in (pygame.K_LEFT, pygame.K_UP):
                self.rev_i = (self.rev_i - 1) % 9
            elif k in (pygame.K_RIGHT, pygame.K_DOWN):
                self.rev_i = (self.rev_i + 1) % 9
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = REVIEW_DETAIL       # ENTER -> lihat detail
        elif self.state == REVIEW_DETAIL:        # detail satu mekanisme
            if k == pygame.K_ESCAPE:
                self.state = MENU; self.sel = 0
            elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = REVIEW              # ENTER -> pilih mekanisme lain
            elif k == pygame.K_SPACE:            # SPACE -> "how it works": DEMO contraption
                self.start_review_demo(self.rev_i)   # goal 7 varian = mekanisme terpilih
        elif self.state == PLAY:
            self._play_key(k)

    def _choose(self):
        if self.state == MENU:
            self.mode = self.sel     # ingat mode terpilih
            if self.sel == 0:        # Review Mechanisms -> ensiklopedia (tanpa level/goal)
                self.rev_i = 0; self.rev_frame = 0; self.rev_tick = 0
                self.state = REVIEW
            else:                    # Fill Mech / Fill Zany / Mix Up -> pilih LEVEL dulu
                self.state = LEVEL   # (spt game asli: ketiganya lewat Apprentice/Master)
            self.sel = 0
        elif self.state == LEVEL:
            self.level = self.sel            # 0=Apprentice, 1=Master Builder
            if self.mode == 3:
                # ⭐ Contraption Mix Up TIDAK lewat pemilih goal. Di `main_.c`
                # hanya case 2 dan 3 memanggil `sub = goalmenu()`; case 4
                # memasang `sub = 0` lalu `goal = 6` dan tiap putaran
                # `sub++` -- jadi kontraption 1..6 dimainkan BERURUTAN.
                self._mix_mulai()
            else:
                self.state = GOAL; self.sel = 0
        elif self.state == GOAL:
            gid = self.goal_ids[self.sel]
            if self.mode == 1:               # Fill in Mechanisms
                self.start_play(gid, fill="mech")
            elif self.mode == 2:             # Fill in Zany Objects
                self.start_play(gid, fill="zany")
            else:                            # Mix Up: isi mekanisme DAN zany, berwaktu
                self.start_play(gid, fill="both")


def run_window(g, scale=3):
    """Native 320x200 -> tampil di-scale integer nearest (metode DOSBox).
    Hotkey: 2-6 set skala tetap; 0 best-fit; A aspek 4:3; F fullscreen; Q keluar."""
    cga.set_dpi_aware()
    # nearest-neighbor tegas (hindari blur), untuk jalur SDL apa pun
    os.environ.setdefault("SDL_HINT_RENDER_SCALE_QUALITY", "0")
    pygame.init()
    pygame.display.set_caption("Creative Contraptions (port)")
    aspect = False
    fixed = scale                 # None = best-fit; angka = skala tetap
    fullscreen = False

    def make_screen():
        if fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        vh = 240 if aspect else cga.HEIGHT
        return pygame.display.set_mode((cga.WIDTH * (fixed or 3), vh * (fixed or 3)),
                                       pygame.RESIZABLE)

    screen = make_screen()
    fb = cga.make_framebuffer()
    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE and not fullscreen:
                screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    running = False
                elif pygame.K_2 <= e.key <= pygame.K_6:
                    fixed = e.key - pygame.K_0; screen = make_screen()
                elif e.key == pygame.K_0:
                    fixed = None
                elif e.key == pygame.K_a:
                    aspect = not aspect; screen = make_screen()
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen; screen = make_screen()
                else:
                    g.key(e.key)
        g.tick()
        g.draw(fb)                        # SEMUA render ke native 320x200
        cga.present(screen, fb, fixed, aspect)   # hanya tampilan yg di-scale
        clock.tick(30)
    pygame.quit()


def run_shots(g):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    fb = cga.make_framebuffer()
    seq = [("title", TITLE, 0), ("menu", MENU, 3), ("level", LEVEL, 1),
           ("goal", GOAL, 0), ("contraption", CONTRAPTION, 0)]
    out = os.path.dirname(__file__)
    for name, st, sel in seq:
        g.state, g.sel = st, sel
        if st == CONTRAPTION:
            g.chosen_goal = 1
        g.draw(fb)
        big = pygame.transform.scale(fb, (cga.WIDTH * 3, cga.HEIGHT * 3))
        pygame.image.save(big, os.path.join(out, "scr_%s.png" % name))
        print("scr_%s.png" % name)
    pygame.quit()


if __name__ == "__main__":
    data = assets.find_data_dir()
    g = Game(data)
    if "--shots" in sys.argv:
        run_shots(g)
    else:
        run_window(g)
