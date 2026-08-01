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
            self._mainmenu(fb)
        elif self.state == LEVEL:
            self._menu(fb, "WHAT LEVEL WOULD YOU LIKE?", LEVELS)
        elif self.state == GOAL:
            self._menu(fb, "WHAT IS YOUR GOAL?",
                       [GOAL_NAMES[g] for g in self.goal_ids])
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

        def isi(i):
            tipe = MECH_CATEGORIES[i][1][0]
            for r in self.k_mechs.recs:
                if self.k_mechs.cocok(r, tipe):
                    return self.k_mechs, r
            return None

        _pal.drawpal(k, self.rev_i, isi, len(MECH_CATEGORIES))
        _pal.penunjuk(k, self.k_misc, (self.title_tick // _pal.PENUNJUK_TIK) & 1)

    def _review_detail(self, fb):
        """Layar detail satu mekanisme: judul + sprite (statis) + definisi + contoh.
        SPACE = "how it works" -> memutar CONTRAPTION DEMO (goal 7 varian = mekanisme ini)
        yg berjalan sendiri (spt game asli: 0x3b2=7, 5035+18db)."""
        m = self.review_layout["mechs"].get(self.rev_i)
        if m:
            self._rev_text(fb, m)
        # sprite mekanisme statis di (144,48) spt 3020
        name, ids = MECH_CATEGORIES[self.rev_i]
        rec = self.mechs.first_of_major(ids[0])
        if rec:
            fb.blit(self.mechs.sprite(rec), (144, 48))
        self._rev_text(fb, self.review_layout["fixed"])

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

    def _mainmenu(self, fb):
        """Menu utama dgn IKON tiap pilihan (spt game asli)."""
        text.draw_center(fb, "WHAT DO YOU WANT TO DO?", 16, color=0, size=12)
        for i, opt in enumerate(MENU_OPTIONS):
            y = 39 + i * 27
            # kotak ikon + border magenta (tebal bila terpilih)
            pygame.draw.rect(fb, cga.PALETTE[2], (46, y - 2, 48, 29), 2 if i == self.sel else 1)
            if self.menu_icons[i]:
                fb.blit(self.menu_icons[i], (48, y))
            text.draw(fb, opt, 110, y + 8, color=0 if i != self.sel else 3, size=11)
        text.draw_center(fb, "Press UP/DOWN to move box.", 168, color=2, size=10)
        text.draw_center(fb, "Press ENTER to choose.", 182, color=2, size=10)

    def _menu(self, fb, header, options):
        text.draw_center(fb, header, 20, color=2, size=14)
        n = len(options)
        step = 18 if n <= 4 else 15
        y0 = 56
        for i, opt in enumerate(options):
            yy = y0 + i * step
            col = 3 if i == self.sel else 0
            if i == self.sel:
                w = text._font(13).size(opt)[0]
                pygame.draw.rect(fb, cga.PALETTE[2],
                                 (cga.WIDTH // 2 - w // 2 - 6, yy - 2, w + 12, 16), 1)
            text.draw_center(fb, opt, yy, color=col, size=13)
        text.draw_center(fb, "Up/Down to move, ENTER to choose", 186, color=2, size=10)

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
        surf = self._scene_surface(gid, vi, draw_mech, mode=self._mode_layar())
        if surf is not None:
            fb.blit(surf, (0, 0))

    def _scene_surface(self, gid, vi, isi_mekanisme, seed=0, mode=None):
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
        key = (gid, vi, bool(isi_mekanisme), seed, mode)
        if key in self._scene_cache:
            return self._scene_cache[key]
        # Disusun oleh cc/core/adegan.susun() -- SAMA dengan yang dipakai
        # penggenerasi animasi. Dulu blok ini menyalin logikanya sendiri, dan
        # itu langsung menggigit: nama goal di pita atas ditambahkan di
        # adegan.susun() tapi layar ini tidak ikut berubah karena jalurnya beda.
        _var, _parts, fb = _adg.susun(
            gid, self.k_graph, self.k_mechs, self.k_misc, self.k_anim,
            self.k_goals, seed=seed, mode=mode, varian=vi, sub=gid,
            isi=bool(isi_mekanisme), nbola=1)
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
        text.draw_center(fb, "Press SPACE to run  -  ESC for menu", 190, color=3, size=10)

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
            msg = "SPACE=replay  ENTER=pick another  ESC=menu" if done else "Watching..."
            text.draw_center(fb, msg, 190, color=3, size=9)
            return
        text.draw(fb, GOAL_NAMES.get(self.chosen_goal, "?"), 4, 2, color=0, size=12)
        if done and self.anim_fail is not None:      # GAGAL di slot tertentu
            text.draw_center(fb, "Mechanism %c does not work!" % (0x41 + self.anim_fail),
                             178, color=2, size=12)
            text.draw_center(fb, "ESC = keep building", 190, color=3, size=10)
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

    # ---------- pemilihan varian (spt loader FUN_1000_5035: acak, hindari ulang) ----------
    def _pick_variant(self, gid):
        # Jumlah varian datang dari CONTRAP, bukan dari berapa banyak berkas
        # tangkapan yang kebetulan ada. Dulu `len(self.draws_var[gid])`, dan
        # itu berarti sebuah varian yang belum sempat ditangkap emulator
        # TIDAK PERNAH terpilih -- data game dibatasi oleh alat ukur kita.
        n = len(self.k_goals.get(gid) or ()) or 1
        if n <= 1:
            self.last_variant[gid] = 0
            return 0
        last = self.last_variant.get(gid)
        choices = [v for v in range(n) if v != last] or list(range(n))
        vi = random.choice(choices)
        self.last_variant[gid] = vi
        return vi

    # ---------- mode PLAY: Fill Mechanisms / Fill Zany / Mix Up (both) ----------
    def start_play(self, gid, fill="mech"):
        vi = self._pick_variant(gid)
        self.cur_variant = vi
        vs = self.k_goals.get(gid) or []
        var = vs[vi] if vi < len(vs) else vs[0]
        self.fill_mode = fill                     # "mech" | "zany" | "both" (Mix Up)
        self.slots = []
        self.palette = []

        # Record sprite per slot datang dari UNDIAN yang sama dengan game
        # (pickpart untuk objek zany, fillans untuk mekanisme) -- bukan dari
        # rekaman `draws_goal*.json`. Dulu posisi slot dicocokkan ke daftar
        # blit hasil tangkapan; sekarang tidak ada yang perlu dicocokkan.
        rng = _rng.Rng(0)
        _pick.loadcon_pick(rng, max(1, len(vs)))
        jz = [t for (y, x, t) in var["zany"]]
        tz = _pick.tabel(self.k_graph, jz)
        selz = [None if i is None else tz[i]["idx"]
                for i in _pick.pickpart(rng, tz, jz, sub=gid)]
        jm = [t for (y, x, t) in var["mech"]]
        tm = _pick.tabel(self.k_mechs, jm)
        selm = [None if i is None else tm[i]["idx"]
                for i in _pick.fillans(tm, jm)]

        def add_slots(parts, arch):
            dipilih = selm if arch == "MECHS" else selz
            for k, (y, x, typ) in enumerate(parts):
                idx = dipilih[k] if k < len(dipilih) and dipilih[k] is not None else -1
                self.slots.append(dict(y=y, x=x, correct=typ, filled=None, tries=0,
                                       arch=arch, sprite=idx))
        # entri palet = (nama, ids, arch, sprite_idx). sprite_idx = gambar EKSAK yg akan
        # DITEMPATKAN utk kategori itu di contraption ini (dari slot), supaya ikon palet
        # SAMA dgn gambar yg muncul saat ditaruh (mis. Inclined Plane -> id 101, bukan 100).
        if fill in ("mech", "both"):
            add_slots(var["mech"], "MECHS")
            catspr = {}
            for s in self.slots:
                if s["arch"] == "MECHS":
                    ci = self._cat_index(s["correct"])
                    if ci is not None and ci not in catspr and s["sprite"] >= 0:
                        catspr[ci] = s["sprite"]
            for ci, (nm, ids) in enumerate(MECH_CATEGORIES):
                idx = catspr.get(ci, -1)
                if idx < 0:
                    rec = self.mechs.first_of_major(ids[0])
                    idx = rec["idx"] if rec else -1
                self.palette.append((nm, ids, "MECHS", idx))
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
        # KOCOK palet acak tiap load (spt Fisher-Yates FUN_1000_3909), termasuk pengecoh
        random.shuffle(self.palette)
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
        self.message = "Pick parts to fill the empty boxes."
        self.chosen_goal = gid
        self.running = False
        self.run_fail_slot = None
        self.ball_i = -1
        self.ball_pos = None
        self.anim_fail = None
        self.anim_limit = None
        self.review_demo = False
        self.state = PLAY

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
        _hud.showsc(k, self.score)
        if self.mode_asli == 4:
            _hud.timedrw(k, self.tx, self.mode_asli, self.nbola, self.chosen_goal)

    def _play(self, fb):
        gid = self.chosen_goal
        # part TETAP tampil (mech mode: zany scenery; zany: mekanisme; both: tidak ada)
        self._blit_scene(fb, gid, archs=self.fixed_archs)
        self._hud(fb)
        inbox = (self.fill_mode == "zany")   # Zany: kandidat berputar DI DALAM kotak
        for i, s in enumerate(self.slots):
            arch = self._arch(s["arch"])
            if s["filled"] is not None:
                spr = arch.sprite_by_idx(s["sprite"]) if s["sprite"] >= 0 \
                    else arch.sprite(arch.first_of_major(s["filled"]))
                if spr:
                    fb.blit(spr, (s["x"], s["y"]))
            elif inbox and i == self.cur_slot:
                # tampilkan kandidat saat ini DI DALAM kotak (blink), + panah
                pn, pid, pa, pidx = self.palette[self.cur_part]
                spr = self._arch(pa).sprite_by_idx(pidx) if pidx >= 0 else None
                if spr:
                    fb.blit(spr, (s["x"], s["y"]))
                pygame.draw.rect(fb, cga.PALETTE[2], (s["x"] - 2, s["y"] - 2, 36, 28), 1)
                text.draw(fb, "<", s["x"] - 10, s["y"] + 8, color=2, size=10)
                text.draw(fb, ">", s["x"] + 34, s["y"] + 8, color=2, size=10)
            else:
                color = 2 if i == self.cur_slot else 3
                pygame.draw.rect(fb, cga.PALETTE[color], (s["x"], s["y"], 32, 24), 1)
                text.draw(fb, chr(0x41 + i), s["x"] + 12, s["y"] + 7, color=color, size=11)
        # bola saat "run" (di AREA MAIN, di atas contraption) — magenta spt bola asli
        if self.ball_pos is not None:
            bx, by = int(self.ball_pos[0]), int(self.ball_pos[1])
            pygame.draw.circle(fb, cga.PALETTE[2], (bx, by), 2)
            fb.set_at((bx, by), cga.PALETTE[3])
        # BILAH STATUS bawah (y=166..199) — di bawah play area, tak menutupi slot/scenery
        pygame.draw.rect(fb, cga.PALETTE[0], (0, 166, 320, 34))
        if not inbox:
            self._palette_strip(fb)                       # STRIP semua opsi (spt 4e3e)
            label = self.palette[self.cur_part][0]
        else:
            text.draw(fb, "Cycle < > in box, ENTER to place", 40, 172, color=3, size=9)
            label = ""
        text.draw(fb, label, 4, 191, color=3, size=8)
        text.draw(fb, "Score:%d" % self.score, 120, 191, color=1, size=8)
        if self.timer is not None:
            t = max(0, int(self.timer))
            text.draw(fb, "%d:%02d" % (t // 60, t % 60), 290, 191, color=2, size=8)
        # pesan feedback di ATAS area main (tak mengganggu bilah)
        if self.message:
            text.draw_center(fb, self.message, 3, color=2, size=9)

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
                self.message = "TIME'S UP! ESC for menu."
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
                    self.message = "Mechanism %c does not work! Fix it and try again." \
                        % (0x41 + self.run_fail_slot)
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
            self._back_to_goal()             # ESC saat main -> kembali ke pilihan tema (GOAL)
            return
        if k == pygame.K_SPACE:               # RUN: bola keluar & jalan (spt game asli)
            if self.running:
                return
            if self.timer is not None and self.timer <= 0:
                return
            wrong = [i for i, s in enumerate(self.slots) if s["filled"] != s["correct"]]
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
                self.message = "The ball is running..."
            else:
                # zany/both: beri tahu masih ada yg salah/kosong
                self.message = "Box %c isn't right yet - fix it." % (0x41 + wrong[0])
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
        s = self.slots[self.cur_slot]
        if s["filled"] is not None:
            return
        pname, pids, parch, pidx = self.palette[self.cur_part]
        if s["correct"] in pids:          # mech: cocok by-KATEGORI; zany: id eksak
            s["filled"] = s["correct"]    # simpan id jawaban
            if pidx >= 0:
                s["sprite"] = pidx        # tempatkan gambar EKSAK yg tampil di palet
            self.message = "Correct!"
            empties = [i for i, sl in enumerate(self.slots) if sl["filled"] is None]
            if empties:
                self.cur_slot = empties[0]
            else:
                self.message = "GREAT! Contraption complete."
        else:
            # `zcnt` @0x7e6 = penghitung kesalahan untuk SELURUH kontraption.
            # Skornya dihitung SEKALI di akhir goal dari angka ini, bukan
            # per kotak -- lihat cc/core/hud.py:skor_akhir().
            self.zcnt += 1
            s["tries"] += 1
            self.message = "%s %c does not work." % (self.part_word, 0x41 + self.cur_slot)

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
                    self.message = "Try again - fix Box %c." % (0x41 + self.anim_fail)
                    self.anim_fail = None
                elif self.anim_from_play:        # MENANG di Fill/Mix Up -> kembali ke tema (GOAL)
                    self._back_to_goal()
                else:                            # demo dari CONTRAPTION -> menu
                    self.state = MENU; self.sel = 0
            elif k == pygame.K_SPACE:            # replay
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
