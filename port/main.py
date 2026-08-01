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


def decode_dat(fp, maxframes=None):
    """Decode file frame ter-pack (CCA1, 2bpp+zlib) -> list Surface 320x200.
    maxframes: batasi jumlah frame yg di-decode (utk pencocokan frame-0 yg murah)."""
    if not fp or not os.path.exists(fp):
        return []
    raw = open(fp, "rb").read()
    assert raw[:4] == b"CCA1"
    _, nfr = struct.unpack_from("<HH", raw, 4)
    if maxframes is not None:
        nfr = min(nfr, maxframes)
    blob = zlib.decompress(raw[8:])
    pal = cga.PALETTE
    frames = []
    fsize = 320 * 200 // 4
    for fi in range(nfr):
        surf = pygame.Surface((320, 200))
        foff = fi * fsize
        for y in range(200):
            row = foff + y * 80
            for xb in range(80):
                b = blob[row + xb]
                x = xb * 4
                surf.set_at((x, y), pal[(b >> 6) & 3])
                surf.set_at((x + 1, y), pal[(b >> 4) & 3])
                surf.set_at((x + 2, y), pal[(b >> 2) & 3])
                surf.set_at((x + 3, y), pal[b & 3])
        frames.append(surf)
    return frames


def load_anim_frames(gid, vi=0):
    """Muat frame animasi run PER-VARIAN (goalN_vV.dat), fallback goalN.dat."""
    base = os.path.join(os.path.dirname(__file__), "cc", "anim")
    for cand in ("goal%d_v%d.dat" % (gid, vi), "goal%d.dat" % gid):
        p = os.path.join(base, cand)
        if os.path.exists(p):
            return decode_dat(p)
    return []


def _anim_candidates(gid):
    """Semua file animasi kandidat utk sebuah goal: goalN_vI.dat (semua I) + goalN.dat."""
    base = os.path.join(os.path.dirname(__file__), "cc", "anim")
    out = []
    vi = 0
    while os.path.exists(os.path.join(base, "goal%d_v%d.dat" % (gid, vi))):
        out.append(os.path.join(base, "goal%d_v%d.dat" % (gid, vi)))
        vi += 1
    p = os.path.join(base, "goal%d.dat" % gid)
    if os.path.exists(p):
        out.append(p)
    return out


def build_title_anim():
    """Rakit animasi bola RUBE-GOLDBERG utk layar judul (dari deskripsi user, bukan rekaman
    goal-128 yg janggal). Dua jalur bergantian, loop:
      KIRI : ayam -> jatuh & memantul 2 DRUM(id80, tiap pantul 'BOOM') -> LEVER(id141)
             -> LEVER melontar bola ke atas -> GAJAH.
      KANAN: gajah -> jatuh & memantul 3 CANGKIR di atas tiga per(id79) -> SPRING box(id150)
             -> SPRING melontar bola ke atas -> AYAM.
    Kembalikan (ball, react): ball[i]=(x,y,visible); react[i]=dict penanda (lever/spring/
    elephant/chicken/boom). Titik kontak diselaraskan posisi sprite goal 128 (draws_title)."""
    ball, react = [], []

    def _seg(p0, p1, n, kind, h=0):
        for i in range(n):
            t = i / n
            x = p0[0] + (p1[0] - p0[0]) * t
            if kind == "fall":                 # percepatan ke bawah (gravitasi)
                y = p0[1] + (p1[1] - p0[1]) * (t * t)
            else:                              # "arc": parabola memuncak h di atas tali busur
                y = p0[1] + (p1[1] - p0[1]) * t - h * 4 * t * (1 - t)
            ball.append((x, y, True)); react.append({})

    def _hold(p, n, vis):
        for _ in range(n):
            ball.append((p[0], p[1], vis)); react.append({})

    def _tag(i0, n, key, val=True):
        for i in range(i0, min(i0 + n, len(ball))):
            react[i][key] = val

    # titik kontak (selaras draws_title.json). Kotak lever(124,128) & spring(168,128) = 32x24;
    # bola mendarat DI DALAM kotak (di atas mekanismenya), bukan di tepi frame.
    CHICK = (56, 52)
    DRUM1, DRUM2 = (72, 100), (102, 112)          # 2 drum id80 (kiri-tengah)
    LEVER = (139, 133)                            # DI DALAM lever box id141 (di batang jungkat2)
    ELEPH, ELEPH_OUT = (282, 44), (272, 56)       # gajah id78 (kanan-atas)
    # 3 cangkir di atas tiga per id79 (216,82) — TANGGA: kanan tinggi -> kiri rendah
    # (posisi dari analisa sprite 467: rim kanan y86, tengah y94, kiri y103)
    CUP_R, CUP_M, CUP_L = (271, 89), (249, 97), (224, 106)
    # reaksi cangkir miring: (rect HAPUS base-cup penuh, posisi overlay cangkir-miring).
    # base-cup dihapus total lalu digambar cangkir-miring di posisi rim yg sama -> bersih.
    TILT_R = ((261, 85, 24, 16), (261, 82))
    TILT_M = ((240, 93, 24, 16), (240, 90))
    TILT_L = ((216, 102, 24, 16), (216, 99))
    SPRINGBOX = (184, 138)                        # DI DALAM spring box id150 (di per)

    def _tagcup(i0, n, td):                        # tag cuptilt (pakai 468: miring lembut,
        er, pos = td                               # gagang menempel — 469/470 gagangnya lepas)
        for k in range(n):
            if i0 + k < len(ball):
                react[i0 + k]["cuptilt"] = (er, pos, 0)

    # ---- JALUR KIRI: ayam -> drum(BOOM) -> lever -> gajah ----
    _seg(CHICK, DRUM1, 16, "fall")                # jatuh ke drum1
    i0 = len(ball); _seg(DRUM1, DRUM2, 12, "arc", 14)     # pantul drum1 -> drum2
    _tag(i0, 8, "boom", (DRUM1[0] - 6, DRUM1[1] - 18))    # BOOM! di drum1
    i0 = len(ball); _seg(DRUM2, LEVER, 14, "fall")        # drum2 -> masuk lever box
    _tag(i0, 8, "boom", (DRUM2[0] - 6, DRUM2[1] - 18))    # BOOM! di drum2
    i0 = len(ball); _hold(LEVER, 6, True); _tag(i0, 99, "lever")   # jungkat-jungkit menggentak
    i0 = len(ball); _seg(LEVER, ELEPH, 34, "arc", 36)     # LONTAR ke gajah
    _tag(i0, 6, "lever")
    i0 = len(ball); _hold(ELEPH, 12, False); _tag(i0, 99, "elephant")  # gajah telan+react

    # ---- JALUR KANAN: gajah -> 3 cangkir (miring saat kena) -> spring box -> ayam ----
    _seg(ELEPH_OUT, CUP_R, 12, "fall")            # keluar gajah -> cangkir kanan (tertinggi)
    i0 = len(ball); _seg(CUP_R, CUP_M, 9, "arc", 10)      # pantul cangkir kanan -> tengah
    _tagcup(i0, 9, TILT_R)                                # cangkir kanan MIRING
    i0 = len(ball); _seg(CUP_M, CUP_L, 9, "arc", 10)      # pantul tengah -> kiri
    _tagcup(i0, 9, TILT_M)                                # cangkir tengah MIRING
    i0 = len(ball); _seg(CUP_L, SPRINGBOX, 14, "fall")    # kiri -> masuk spring box
    _tagcup(i0, 9, TILT_L)                                # cangkir kiri MIRING
    i0 = len(ball); _hold(SPRINGBOX, 6, True); _tag(i0, 99, "spring")  # per menekan
    i0 = len(ball); _seg(SPRINGBOX, CHICK, 36, "arc", 40)  # LONTAR ke ayam
    _tag(i0, 6, "spring")
    i0 = len(ball); _hold(CHICK, 10, False); _tag(i0, 99, "chicken")   # ayam terima+kepak
    return ball, react


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
        rlp = os.path.join(os.path.dirname(__file__), "cc", "anim", "review_layout.json")
        self.review_layout = json.load(open(rlp)) if os.path.exists(rlp) else None
        # ikon menu (di-crop dari render game asli)
        icdir = os.path.join(os.path.dirname(__file__), "cc", "anim", "icons")
        self.menu_icons = []
        for nm in ("review", "fillmech", "zany", "mixup"):
            fp = os.path.join(icdir, nm + ".png")
            self.menu_icons.append(pygame.image.load(fp) if os.path.exists(fp) else None)
        self.anim = anim.AnimArchive(os.path.join(data_dir, "ANIMATE"))
        self.goals = assets.parse_contrap(os.path.join(data_dir, "CONTRAP"))
        # ---- lapisan INTI terverifikasi -------------------------------------
        # Aturan arsip/penempatan yang SAMA dengan work/genscreens.py (197/197).
        # Layar tidak lagi diputar dari rekaman; ia DIBANGKITKAN dari data.
        self.k_graph = _arc.Archive(os.path.join(data_dir, "GRAPH"))
        self.k_mechs = _arc.Archive(os.path.join(data_dir, "MECHS"))
        self.k_misc = _arc.Archive(os.path.join(data_dir, "MISC"))
        self.k_goals = _con.parse(os.path.join(data_dir, "CONTRAP"))
        self._scene_cache = {}
        # daftar gambar DETERMINISTIK (diekstrak dari eksekusi game asli via emulator):
        # per goal, daftar {arch, idx, x, y} = record & posisi EKSAK. Tanpa tebakan.
        self.draws = {}
        ddir = os.path.join(os.path.dirname(__file__), "cc", "draws")
        for g in range(1, 8):
            fp = os.path.join(ddir, "draws_goal%d.json" % g)
            if os.path.exists(fp):
                self.draws[g] = json.load(open(fp))
        # daftar gambar PER-VARIAN (draws_goalG_vV.json). Fill in Mechanisms memuat
        # varian ACAK tiap load (spt FUN_1000_5035 di game asli) -> starting screen
        # berbeda-beda utk goal yg sama. v0 = referensi terverifikasi (rest pose).
        self.draws_var = {}       # gid -> {vi -> daftar draw}
        for g in range(1, 8):
            vm = {}
            vi = 0
            while True:
                fp = os.path.join(ddir, "draws_goal%d_v%d.json" % (g, vi))
                if not os.path.exists(fp):
                    break
                vm[vi] = json.load(open(fp))
                vi += 1
            if vm:
                self.draws_var[g] = vm
        self.last_variant = {}    # gid -> varian terakhir (agar tak berulang, spt 0x1e30)
        self.cur_variant = 0
        self.cur_draws = []       # draw varian yg sedang dimainkan
        # LAYAR JUDUL: komposisi sprite = CONTRAP goal 128 (ayam, gajah, kaleng, per,
        # kotak lever & spring) — cocok persis screenshot Title.png. Teks ditumpuk oleh port.
        tp = os.path.join(ddir, "draws_title.json")
        self.title_draws = json.load(open(tp)) if os.path.exists(tp) else []
        self.title_tick = 0
        # ANIMASI judul = bola LOGIS berantai (ayam->jungkat-jungkit->gajah->per->ayam, loop),
        # digambar di atas sprite statis goal 128. Fisika parabola + reaksi objek.
        self.title_ball, self.title_react = build_title_anim()
        # bola judul IDENTIK bola game: ambil HANYA piksel bola dari sprite lever (idx26)
        # area (20,10) 8x8 — magenta = badan bola, gray = highlight HANYA jika di DALAM bola
        # (tetangga magenta), selebihnya (latar kotak abu / bar biru) -> transparan (cyan).
        _lev = self.mechs.sprite_by_idx(26)
        MAG, GRY = cga.PALETTE[2], cga.PALETTE[3]
        # bbox bola TEPAT = x22..29, y10..17 (bukan x20 — dulu terpotong 2px di kanan)
        _reg = [[tuple(_lev.get_at((22 + x, 10 + y)))[:3] for x in range(8)] for y in range(8)]
        self.title_ballspr = pygame.Surface((8, 8))
        self.title_ballspr.fill(cga.PALETTE[cga.BG_INDEX])
        for _y in range(8):
            for _x in range(8):
                c = _reg[_y][_x]
                if c == MAG:
                    self.title_ballspr.set_at((_x, _y), MAG)
                elif c == GRY:                      # highlight hanya jika dikelilingi magenta
                    nb = sum(1 for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                             if 0 <= _x + dx < 8 and 0 <= _y + dy < 8 and _reg[_y + dy][_x + dx] == MAG)
                    if nb >= 2:
                        self.title_ballspr.set_at((_x, _y), GRY)
        self.title_ballspr.set_colorkey(cga.PALETTE[cga.BG_INDEX])
        # sprite cangkir-miring (id79 idx468/469/470 = frame kemiringan bertahap) transparan
        self.title_cupsprs = []
        for _i in (468, 469, 470):
            _c = self.graph.sprite_by_idx(_i).copy()
            _c.set_colorkey(cga.PALETTE[cga.BG_INDEX])
            self.title_cupsprs.append(_c)
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
        """Layar intro/browse: instruksi (atas) + SLIDER 9 ikon mekanisme (bawah) + pointer."""
        if self.review_layout:
            self._rev_text(fb, self.review_layout["intro"])
        # bilah slider dark-blue di bawah (spt game)
        pygame.draw.rect(fb, cga.PALETTE[0], (0, 152, 320, 48))
        n = len(MECH_CATEGORIES)
        cw = 34
        x0 = (cga.WIDTH - n * cw) // 2
        for i, (name, ids) in enumerate(MECH_CATEGORIES):
            bx = x0 + i * cw
            pygame.draw.rect(fb, cga.PALETTE[3], (bx, 156, cw - 2, 30))   # kotak abu ikon
            rec = self.mechs.first_of_major(ids[0])
            if rec:
                spr = self.mechs.sprite(rec)
                fb.blit(spr, (bx + (cw - 2 - spr.get_width()) // 2,
                              156 + (30 - spr.get_height()) // 2))
        # pointer segitiga MENGHADAP ATAS (apex di atas) di bawah mekanisme terpilih
        px = x0 + self.rev_i * cw + (cw - 2) // 2
        pygame.draw.polygon(fb, cga.PALETTE[3], [(px, 188), (px - 5, 195), (px + 5, 195)])

    def _review_detail(self, fb):
        """Layar detail satu mekanisme: judul + sprite (statis) + definisi + contoh.
        SPACE = "how it works" -> memutar CONTRAPTION DEMO (goal 7 varian = mekanisme ini)
        yg berjalan sendiri (spt game asli: 0x3b2=7, 5035+18db)."""
        m = self.review_layout["mechs"].get(str(self.rev_i))
        if m:
            self._rev_text(fb, m["recs"])
        # sprite mekanisme statis di (144,48) spt 3020
        name, ids = MECH_CATEGORIES[self.rev_i]
        rec = self.mechs.first_of_major(ids[0])
        if rec:
            fb.blit(self.mechs.sprite(rec), (144, 48))
        self._rev_text(fb, self.review_layout["fixed"])

    def _title(self, fb):
        # sprite judul statis (goal 128) + REAKSI objek pd frame tertentu (swap frame)
        f = (self.title_tick // 2) % len(self.title_ball)   # ~15fps
        rc = self.title_react[f]
        for d in self.title_draws:
            if d["idx"] < 0:
                continue
            arch = self.mechs if d["arch"] == "MECHS" else self.graph
            idx, dy = d["idx"], 0
            if d["idx"] == 26 and rc.get("lever"):        # lever id141 melontar (miring)
                idx = 27
            elif d["idx"] == 28 and rc.get("spring"):     # spring box id150 melontar
                idx = 29
            elif d["idx"] == 465 and rc.get("elephant"):  # gajah bereaksi (belalai/telinga)
                idx = 466
            elif d["idx"] == 475 and rc.get("chicken"):   # ayam berkepak (bob)
                dy = -3
            spr = arch.sprite_by_idx(idx)
            if spr:
                fb.blit(spr, (d["x"], d["y"] + dy))
        # CANGKIR MIRING saat kena bola: hapus base-cup dulu (biar tak ada pixel ketinggalan),
        # lalu overlay sprite cangkir-miring (id79 idx468)
        cup = rc.get("cuptilt")
        if cup:
            erase, pos, ti = cup
            fb.fill(cga.PALETTE[cga.BG_INDEX], erase)       # hapus base-cup total
            fb.blit(self.title_cupsprs[ti], pos)            # cangkir-miring bertahap (468/469/470)
        # BOLA menyusuri jalur Rube-Goldberg — sprite IDENTIK bola game (8x8 dari lever)
        bx, by, vis = self.title_ball[f]
        if vis:
            fb.blit(self.title_ballspr, (int(bx) - 4, int(by) - 4))
        boom = rc.get("boom")                             # tulisan BOOM! hanya di drum (kiri)
        if boom:
            text.draw(fb, "BOOM!", boom[0], boom[1], color=2, size=11)
        # judul "CREATIVE CONTRAPTIONS" (biru, spt Title.png) + prompt (magenta)
        text.draw_center(fb, "CREATIVE", 12, color=0, size=30)
        text.draw_center(fb, "CONTRAPTIONS", 40, color=0, size=30)
        if (self.title_tick // 15) % 2:                  # prompt berkedip
            text.draw_center(fb, "Press ENTER to go on.", 182, color=2, size=12)

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

    def _blit_scene(self, fb, gid, draw_mech=True, archs=None, draws=None):
        """Gambar contraption dari daftar draw DETERMINISTIK (record & posisi eksak).
        archs=None -> pakai draw_mech (kompat lama); else set arch yg digambar.
        draws=None -> per-goal (default v0); else daftar draw varian terpilih."""
        if archs is not None:
            draw_mech = "MECHS" in archs
        vi = getattr(self, "cur_variant", 0)
        surf = self._scene_surface(gid, vi, draw_mech)
        if surf is not None:
            fb.blit(surf, (0, 0))

    def _scene_surface(self, gid, vi, isi_mekanisme):
        """Layar contraption DIBANGKITKAN dari CONTRAP+GRAPH+MECHS+MISC.

        Memakai lapisan inti yang sama dengan alat bukti, jadi hasilnya identik
        piksel dengan work/screens_gen/*.png. Di-cache per (gid, varian, isi).
        """
        key = (gid, vi, bool(isi_mekanisme))
        if key in self._scene_cache:
            return self._scene_cache[key]
        vs = self.k_goals.get(gid)
        if not vs:
            self._scene_cache[key] = None
            return None
        var = vs[min(vi, len(vs) - 1)]
        dl = _con.draw_list(var, self.k_graph, self.k_mechs, self.k_misc,
                            0, bool(isi_mekanisme))
        fb = _rend.apply(_rend.new_fb(), dl)
        surf = _rend.to_surface(fb, pygame)
        self._scene_cache[key] = surf
        return surf

    def _contraption(self, fb):
        gid = self.goal_ids[self.sel] if self.state == GOAL else self.chosen_goal
        self._blit_scene(fb, gid, draw_mech=True)
        text.draw(fb, GOAL_NAMES.get(gid, "?"), 4, 2, color=0, size=12)
        text.draw_center(fb, "Press SPACE to run  -  ESC for menu", 190, color=3, size=10)

    # ---------- Review: putar animasi run yang benar (PER-VARIAN) ----------
    def _anim_file(self, base, gid, vi):
        """path file anim per-varian dgn fallback ke per-goal lama."""
        d = os.path.join(os.path.dirname(__file__), "cc", "anim")
        for cand in ("%s%d_v%d.json" % (base, gid, vi), "%s%d.json" % (base, gid)):
            p = os.path.join(d, cand)
            if os.path.exists(p):
                return p
        return None

    def _reach(self, gid, vi=0):
        """reach-index per slot mekanisme (dict {(x,y): reach}) — cocok by POSISI karena
        urutan slot (CONTRAP) bisa beda dgn urutan draw."""
        key = (gid, vi)
        if key not in self.reach_cache:
            fp = self._anim_file("reach", gid, vi)
            data = json.load(open(fp)) if fp else []
            self.reach_cache[key] = {(d["x"], d["y"]): d["reach"] for d in data}
        return self.reach_cache[key]

    def _ballpath(self, gid, vi=0):
        """jalur bola LAYAR (koord layar sebenarnya) utk render bola-di-atas-build."""
        key = (gid, vi)
        if key not in self.ballpath_cache:
            fp = self._anim_file("ball", gid, vi)
            self.ballpath_cache[key] = json.load(open(fp)) if fp else []
        return self.ballpath_cache[key]

    def _match_anim(self, gid, design_draws):
        """Pilih file animasi yg frame-0 nya PALING cocok dgn scene design (design_draws),
        di antara semua kandidat dat goal ini. Indeks varian layer DESIGN (draws_goalN_vI.json)
        dan layer ANIMASI (goalN_vI.dat) diekstrak dari run ACAK terpisah, jadi goalN_vI.dat
        belum tentu contraption yg sama dgn draws_goalN_vI.json (mis. goal1 v0). Pencocokan
        by-KONTEN menjamin animasi run == yg dilihat pemain saat design."""
        ref = cga.make_framebuffer()
        ref.fill(cga.PALETTE[cga.BG_INDEX])
        for d in (design_draws or []):
            if d["idx"] < 0:
                continue
            spr = self._arch(d["arch"]).sprite_by_idx(d["idx"])
            if spr:
                ref.blit(spr, (d["x"], d["y"]))

        def framediff(a, b):
            n = 0
            for y in range(0, cga.HEIGHT, 4):
                for x in range(0, cga.WIDTH, 4):
                    if a.get_at((x, y)) != b.get_at((x, y)):
                        n += 1
            return n

        best_fp, best_score = None, None
        for fp in _anim_candidates(gid):
            f0 = decode_dat(fp, maxframes=1)          # decode HANYA frame-0 (murah)
            if not f0:
                continue
            s = framediff(ref, f0[0])
            if best_score is None or s < best_score:
                best_score, best_fp = s, fp
        return decode_dat(best_fp) if best_fp else load_anim_frames(gid, self.cur_variant)

    def start_review(self, gid, from_play=False):
        self.chosen_goal = gid
        self.anim_from_play = from_play
        self.review_demo = False
        # animasi run ter-pack PER-VARIAN (goalN_vV.dat). Demo (bukan from_play) pakai v0.
        vi = self.cur_variant if from_play else 0
        key = (gid, vi)
        if key not in self.anim_cache:
            # from_play: cocokkan animasi ke SCENE design by-KONTEN (indeks varian draws vs
            # dat TAK sinkron). Demo (CONTRAPTION): pertahankan v0 lama.
            self.anim_cache[key] = (self._match_anim(gid, self.cur_draws)
                                    if from_play else load_anim_frames(gid, vi))
        self.anim_frames = self.anim_cache[key]
        self.anim_i = 0 if self.anim_frames else -1
        self.anim_tick = 0
        self.state = PLAYANIM

    def start_review_demo(self, rev_i):
        """Review "how it works": putar CONTRAPTION DEMO goal 7 varian=rev_i (mekanisme
        terpilih), berjalan sendiri & non-interaktif (spt game asli 0x3b2=7 + 18db)."""
        self.chosen_goal = 7
        self.cur_variant = rev_i
        self.cur_draws = self.draws_var.get(7, {}).get(rev_i, [])
        self.anim_from_play = False
        self.review_demo = True
        key = (7, rev_i)
        if key not in self.anim_cache:
            self.anim_cache[key] = load_anim_frames(7, rev_i)
        self.anim_frames = self.anim_cache[key]
        self.anim_i = 0 if self.anim_frames else -1
        self.anim_tick = 0
        self.anim_fail = None
        self.anim_limit = None
        self.state = PLAYANIM

    def _playanim(self, fb):
        if 0 <= self.anim_i < len(self.anim_frames):
            fb.blit(self.anim_frames[self.anim_i], (0, 0))
        else:
            self._blit_scene(fb, self.chosen_goal, draw_mech=True, draws=self.cur_draws)
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
            text.draw_center(fb, "IT WORKS!  Score: %d" % self.score, 178, color=3, size=12)
            text.draw_center(fb, "SPACE = watch again  -  ESC = pick goal", 190, color=2, size=10)
        else:
            msg = "SPACE = replay  -  ESC = menu" if done else "Running..."
            text.draw_center(fb, msg, 190, color=3, size=10)

    # ---------- pemilihan varian (spt loader FUN_1000_5035: acak, hindari ulang) ----------
    def _pick_variant(self, gid):
        vm = self.draws_var.get(gid)
        n = len(vm) if vm else 1
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
        var = self.goals[gid][vi] if vi < len(self.goals[gid]) else self.goals[gid][0]
        # draw varian terpilih (fallback ke per-goal lama bila belum ada)
        self.cur_draws = (self.draws_var.get(gid, {}).get(vi)
                          or self.draws.get(gid, []))
        self.fill_mode = fill                     # "mech" | "zany" | "both" (Mix Up)
        self.slots = []
        self.palette = []

        def idx_at(arch, x, y):
            """idx sprite draw pada posisi (x,y) utk arch (CONTRAP x,y == draws x,y)."""
            for d in self.cur_draws:
                if d["arch"] == arch and d["x"] == x and d["y"] == y:
                    return d["idx"]
            return -1

        def add_slots(parts, arch):
            for (y, x, typ) in parts:
                self.slots.append(dict(y=y, x=x, correct=typ, filled=None, tries=0,
                                       arch=arch, sprite=idx_at(arch, x, y)))
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

    def _play(self, fb):
        gid = self.chosen_goal
        # part TETAP tampil (mech mode: zany scenery; zany: mekanisme; both: tidak ada)
        self._blit_scene(fb, gid, archs=self.fixed_archs, draws=self.cur_draws)
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
        """Gambar SEMUA opsi palet berjajar horizontal (spt game asli FUN_1000_4e3e),
        kotak terpilih disorot magenta. Muat di bilah 166..189."""
        n = len(self.palette)
        cw = max(18, min(32, 316 // max(1, n)))
        x0 = (cga.WIDTH - n * cw) // 2
        y, ch = 168, 20
        for i, (nm, pids, parch, pidx) in enumerate(self.palette):
            bx = x0 + i * cw
            pygame.draw.rect(fb, cga.PALETTE[3], (bx, y, cw - 2, ch))     # kotak abu
            spr = self._arch(parch).sprite_by_idx(pidx) if pidx >= 0 else None
            if spr:
                sc = min((cw - 4) / spr.get_width(), (ch - 2) / spr.get_height(), 1.0)
                if sc < 1:
                    spr = pygame.transform.scale(
                        spr, (max(1, int(spr.get_width() * sc)), max(1, int(spr.get_height() * sc))))
                fb.blit(spr, (bx + (cw - 2 - spr.get_width()) // 2,
                              y + (ch - spr.get_height()) // 2))
            if i == self.cur_part:                                        # sorot terpilih
                pygame.draw.rect(fb, cga.PALETTE[2], (bx - 1, y - 1, cw, ch + 2), 2)

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
                # lengkap & benar -> MENANG. Bonus waktu (Mix Up): 1000/detik tersisa.
                if self.timer is not None:
                    self.score += int(self.timer) * 1000
                self.anim_fail = None
                self.anim_limit = None
                self.start_review(self.chosen_goal, from_play=True)
            elif self.fill_mode == "mech" and self._ballpath(self.chosen_goal, self.cur_variant):
                # GAGAL: bola jalan DI ATAS build kamu, berhenti di kotak salah pertama.
                # Jalur bola & reach PER-VARIAN (dari eksekusi game asli). reach dicocokkan
                # by-POSISI karena urutan slot (CONTRAP) bisa beda dari urutan draw.
                bp = self._ballpath(self.chosen_goal, self.cur_variant)
                reach = self._reach(self.chosen_goal, self.cur_variant)
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
            pts = (10000, 5000)[min(s["tries"], 1)] if s["tries"] < 2 else 2500
            self.score += pts
            s["filled"] = s["correct"]    # simpan id jawaban
            if pidx >= 0:
                s["sprite"] = pidx        # tempatkan gambar EKSAK yg tampil di palet
            self.message = "Correct! +%d" % pts
            empties = [i for i, sl in enumerate(self.slots) if sl["filled"] is None]
            if empties:
                self.cur_slot = empties[0]
            else:
                self.score += 100000
                self.message = "GREAT! Contraption complete! +100000"
        else:
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
