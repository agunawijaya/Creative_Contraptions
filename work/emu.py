"""Emulator x86-16 (Unicorn) untuk menjalankan CONTRAP.EXE & menangkap draw call.
Tahap 1: load MZ, INT DOS/BIOS dasar, jalankan; laporkan INT tak tertangani."""
import os
import struct
from unicorn import *
from unicorn.x86_const import *

D = r"C:\Projects\Creative_Contraptions\Creative-Contraptions"
# Bawaannya biner ASLI (sumber kebenaran). CC_EXE dipakai untuk menjalankan
# EXE hasil rekonstruksi src_c lewat harness yang SAMA -- perbandingan
# PERILAKU, bukan cuma byte.
# WARNING: hook di bawah memakai offset biner ASLI. Selama `pickvar` masih
#   +2 byte, hook untuk fungsi di alamat >= 0x4515 (mis. 5035/5a5b) meleset
#   pada EXE rekonstruksi; layar yang belum menyentuhnya tetap sah.
EXE = os.environ.get("CC_EXE") or \
    r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"

PSP_SEG = 0x0100
LOAD_SEG = PSP_SEG + 0x10

b = open(EXE, "rb").read()
lastpage = struct.unpack_from("<H", b, 2)[0]
pages = struct.unpack_from("<H", b, 4)[0]
nreloc = struct.unpack_from("<H", b, 6)[0]
hdrpar = struct.unpack_from("<H", b, 8)[0]
ss = struct.unpack_from("<H", b, 14)[0]
sp = struct.unpack_from("<H", b, 16)[0]
ip = struct.unpack_from("<H", b, 20)[0]
cs = struct.unpack_from("<H", b, 22)[0]
reltbl = struct.unpack_from("<H", b, 24)[0]
imgsize = (pages - 1) * 512 + (lastpage or 512)
load = bytearray(b[hdrpar * 16:imgsize])

uc = Uc(UC_ARCH_X86, UC_MODE_16)
uc.mem_map(0, 0x110000)  # ~1MB+
# tulis load module
base = LOAD_SEG * 16
uc.mem_write(base, bytes(load))
# relokasi
for i in range(nreloc):
    ro, rs = struct.unpack_from("<HH", b, reltbl + i * 4)
    phys = (LOAD_SEG + rs) * 16 + ro
    val = struct.unpack_from("<H", bytes(uc.mem_read(phys, 2)), 0)[0]
    uc.mem_write(phys, struct.pack("<H", (val + LOAD_SEG) & 0xFFFF))
# PSP
uc.mem_write(PSP_SEG * 16, b"\xCD\x20")
uc.mem_write(PSP_SEG * 16 + 0x80, b"\x00\x0D")
# register
uc.reg_write(UC_X86_REG_CS, LOAD_SEG + cs)
uc.reg_write(UC_X86_REG_IP, ip)
uc.reg_write(UC_X86_REG_SS, LOAD_SEG + ss)
uc.reg_write(UC_X86_REG_SP, sp)
uc.reg_write(UC_X86_REG_DS, PSP_SEG)
uc.reg_write(UC_X86_REG_ES, PSP_SEG)

files = {}          # handle -> (bytes, pos)
next_h = [5]
NAMES = {}
for fn in os.listdir(D):
    NAMES[fn.upper()] = os.path.join(D, fn)

dta = [PSP_SEG, 0x80]     # disk transfer address (seg,off)
fcb_open = {}            # nama file -> bytes


def fcb_name(seg, off):
    p = seg * 16 + off
    drive = uc.mem_read(p, 1)[0]
    nm = bytes(uc.mem_read(p + 1, 8)).decode("latin1").strip()
    ext = bytes(uc.mem_read(p + 9, 3)).decode("latin1").strip()
    return (nm + ("." + ext if ext else "")).upper(), p


def rdw(p): return struct.unpack_from("<H", bytes(uc.mem_read(p, 2)), 0)[0]
def wrw(p, v): uc.mem_write(p, struct.pack("<H", v & 0xFFFF))
def rdd(p): return struct.unpack_from("<I", bytes(uc.mem_read(p, 4)), 0)[0]
def wrd(p, v): uc.mem_write(p, struct.pack("<I", v & 0xFFFFFFFF))

state = {"int21": {}, "unhandled": [], "exit": False, "steps": 0}
keyq = []            # antrian byte keyboard (0x08 read)
draws = []           # log: (major, minor, w, h, screen_x, screen_y)
DGROUP = LOAD_SEG + 0x907


def force_ret_near():
    sp = uc.reg_read(UC_X86_REG_SP); ssg = uc.reg_read(UC_X86_REG_SS)
    rip = struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + sp, 2)), 0)[0]
    uc.reg_write(UC_X86_REG_SP, sp + 2)
    uc.reg_write(UC_X86_REG_IP, rip)


def rd_str(seg, off):
    out = b""
    p = seg * 16 + off
    while True:
        c = uc.mem_read(p, 1)[0]
        if c == 0:
            break
        out += bytes([c]); p += 1
    return out.decode("latin1")


def hook_intr(uc, intno, user):
    ah = (uc.reg_read(UC_X86_REG_AX) >> 8) & 0xFF
    ax = uc.reg_read(UC_X86_REG_AX)
    if intno == 0x20:
        state["exit"] = True; uc.emu_stop(); return
    if intno == 0x21:
        state["int21"][ah] = state["int21"].get(ah, 0) + 1
        if ah == 0x4C:
            state["exit"] = True; uc.emu_stop(); return
        if ah == 0x30:  # DOS version
            uc.reg_write(UC_X86_REG_AX, 0x0005); return
        if ah == 0x3D:  # open
            name = rd_str(uc.reg_read(UC_X86_REG_DS), uc.reg_read(UC_X86_REG_DX))
            key = os.path.basename(name).upper()
            if key in NAMES:
                h = next_h[0]; next_h[0] += 1
                files[h] = [open(NAMES[key], "rb").read(), 0]
                uc.reg_write(UC_X86_REG_AX, h)
                uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
            else:
                uc.reg_write(UC_X86_REG_AX, 2)
                uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) | 1)
            return
        if ah == 0x3F:  # read
            h = uc.reg_read(UC_X86_REG_BX); cx = uc.reg_read(UC_X86_REG_CX)
            dx = uc.reg_read(UC_X86_REG_DX); ds = uc.reg_read(UC_X86_REG_DS)
            if h in files:
                data, pos = files[h]
                chunk = data[pos:pos + cx]
                uc.mem_write(ds * 16 + dx, chunk)
                files[h][1] = pos + len(chunk)
                uc.reg_write(UC_X86_REG_AX, len(chunk))
            else:
                uc.reg_write(UC_X86_REG_AX, 0)
            uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
            return
        if ah == 0x42:  # seek
            h = uc.reg_read(UC_X86_REG_BX); al = ax & 0xFF
            cx = uc.reg_read(UC_X86_REG_CX); dx = uc.reg_read(UC_X86_REG_DX)
            off = (cx << 16) | dx
            if h in files:
                data = files[h][0]
                if al == 0: files[h][1] = off
                elif al == 1: files[h][1] += off
                else: files[h][1] = len(data) + off - (1 << 32 if off >= (1 << 31) else 0)
                p = files[h][1]
                uc.reg_write(UC_X86_REG_AX, p & 0xFFFF)
                uc.reg_write(UC_X86_REG_DX, (p >> 16) & 0xFFFF)
            uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
            return
        if ah == 0x3E:  # close
            files.pop(uc.reg_read(UC_X86_REG_BX), None)
            uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
            return
        if ah == 0x0B:  # cek status stdin
            uc.reg_write(UC_X86_REG_AX, (uc.reg_read(UC_X86_REG_AX) & 0xFF00) | (0xFF if keyq else 0x00))
            return
        if ah in (0x01, 0x06, 0x07, 0x08):  # baca char stdin
            ch = keyq.pop(0) if keyq else 0
            uc.reg_write(UC_X86_REG_AX, (uc.reg_read(UC_X86_REG_AX) & 0xFF00) | (ch & 0xFF))
            return
        if ah == 0x1A:  # set DTA
            dta[0] = uc.reg_read(UC_X86_REG_DS); dta[1] = uc.reg_read(UC_X86_REG_DX)
            return
        if ah == 0x0F:  # FCB open
            name, p = fcb_name(uc.reg_read(UC_X86_REG_DS), uc.reg_read(UC_X86_REG_DX))
            key = name if name in NAMES else name.split(".")[0]
            if key in NAMES:
                data = open(NAMES[key], "rb").read()
                fcb_open[p] = data
                wrw(p + 0x0C, 0)            # current block
                wrw(p + 0x0E, 128)          # record size default
                wrd(p + 0x10, len(data))    # file size
                uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)  # AL=0
            else:
                uc.reg_write(UC_X86_REG_AX, (uc.reg_read(UC_X86_REG_AX) & 0xFF00) | 0xFF)
            return
        if ah == 0x10:  # FCB close
            _, p = fcb_name(uc.reg_read(UC_X86_REG_DS), uc.reg_read(UC_X86_REG_DX))
            fcb_open.pop(p, None)
            uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)
            return
        if ah in (0x14, 0x21, 0x27):  # FCB read (seq / random / random block)
            _, p = fcb_name(uc.reg_read(UC_X86_REG_DS), uc.reg_read(UC_X86_REG_DX))
            data = fcb_open.get(p, b"")
            recsz = rdw(p + 0x0E) or 128
            if ah == 0x14:
                blk = rdw(p + 0x0C); cur = uc.mem_read(p + 0x20, 1)[0]
                recno = blk * 128 + cur; count = 1
            elif ah == 0x21:
                recno = rdd(p + 0x21); count = 1
            else:
                recno = rdd(p + 0x21); count = uc.reg_read(UC_X86_REG_CX)
            start = recno * recsz
            nread = 0
            dbase = dta[0] * 16 + dta[1]
            for r in range(count):
                chunk = data[start + r * recsz: start + (r + 1) * recsz]
                if not chunk:
                    break
                uc.mem_write(dbase + r * recsz, chunk)
                nread += 1
            al = 0 if nread == count else (1 if nread == 0 else 3)
            if ah == 0x27:
                uc.reg_write(UC_X86_REG_CX, nread)
                wrd(p + 0x21, recno + nread)
            elif ah == 0x21:
                pass
            else:
                cur = (recno + 1) % 128
                uc.mem_write(p + 0x20, bytes([cur]))
                wrw(p + 0x0C, (recno + 1) // 128)
            uc.reg_write(UC_X86_REG_AX, (uc.reg_read(UC_X86_REG_AX) & 0xFF00) | al)
            return
        if ah == 0x24:  # set relative record from current block/record
            _, p = fcb_name(uc.reg_read(UC_X86_REG_DS), uc.reg_read(UC_X86_REG_DX))
            blk = rdw(p + 0x0C); cur = uc.mem_read(p + 0x20, 1)[0]
            wrd(p + 0x21, blk * 128 + cur)
            return
        if ah in (0x25, 0x35, 0x44, 0x09, 0x02, 0x48, 0x49, 0x4A, 0x19, 0x2C, 0x16):
            uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
            if ah == 0x48: uc.reg_write(UC_X86_REG_AX, 0x2000)
            return
        uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) & ~1)
        return
    if intno == 0x10:
        return
    if intno == 0x16:
        # keyboard: kembalikan ENTER agar maju
        if ah in (0x00, 0x10):
            uc.reg_write(UC_X86_REG_AX, 0x1C0D)
        else:
            uc.reg_write(UC_X86_REG_EFLAGS, uc.reg_read(UC_X86_REG_EFLAGS) | 0x40)  # ZF (no key)
        return
    state["unhandled"].append((intno, ah))


uc.hook_add(UC_HOOK_INTR, hook_intr)


# IN hook: port 0x3DA (CGA status) -> alternate bit 3
def hook_in(uc, port, size, user):
    if port == 0x3DA:
        hook_in.t = getattr(hook_in, "t", 0) ^ 8
        return hook_in.t
    return 0xFF


uc.hook_add(UC_HOOK_INSN, hook_in, None, 1, 0, UC_X86_INS_IN)

CODE = LOAD_SEG * 16
SS_ = lambda: uc.reg_read(UC_X86_REG_SS)

# Pemetaan alamat untuk EXE REKONSTRUKSI (src_c). Semua offset di berkas ini
# adalah offset biner ASLI; pada EXE rekonstruksi `pickvar` masih 2 byte lebih
# panjang, jadi apa pun di alamat >= CC_SHIFT_AT bergeser CC_SHIFT_BY. Tanpa
# pemetaan ini hook mendarat di TENGAH instruksi dan hasilnya terbaca seperti
# "EXE rekonstruksi rusak" padahal harness-nya yang meleset.
# Tanpa CC_SHIFT_AT, A() adalah identitas -- perilaku bawaan tidak berubah.
CC_SHIFT_AT = int(os.environ.get("CC_SHIFT_AT", "0"), 0)
CC_SHIFT_BY = int(os.environ.get("CC_SHIFT_BY", "0"), 0)


def A(off):
    """offset di biner ASLI -> offset di biner yang sedang dijalankan."""
    return off + CC_SHIFT_BY if (CC_SHIFT_AT and off >= CC_SHIFT_AT) else off


def sgn8(v): return v - 256 if v >= 128 else v


def hook_code(uc, addr, size, user):
    off = addr - CODE
    if off == 0x2692:            # FUN_1000_2692 delay -> lewati
        force_ret_near(); return
    if off == 0x27b4:            # 0x278e: SI=record ptr, gambar sprite (op0x01/zany)
        si = uc.reg_read(UC_X86_REG_SI)
        rec = bytes(uc.mem_read(si, 12))
        bp = uc.reg_read(UC_X86_REG_BP)
        bx_ = struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + 0x14, 2)), 0)[0]
        by_ = struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + 0x16, 2)), 0)[0]
        draws.append((rec[0], rec[1], rec[3], rec[2], bx_ + sgn8(rec[4]), by_ + sgn8(rec[5])))


# Penelusuran diagnostik: CC_TRACE=N mencetak N offset PERTAMA yang dieksekusi.
# Dipakai untuk mencari titik DIVERGENSI antara biner asli dan EXE rekonstruksi.
# Tanpa CC_TRACE, tidak ada hook tambahan -- perilaku bawaan tidak berubah.
CC_TRACE = int(os.environ.get("CC_TRACE", "0"), 0)
if CC_TRACE:
    _tr = [0]

    def hook_trace(uc, addr, size, user):
        if _tr[0] < CC_TRACE:
            _tr[0] += 1
            print("  [tr%04d] %04x" % (_tr[0], addr - CODE))

    uc.hook_add(UC_HOOK_CODE, hook_trace, None, CODE, CODE + 0x9064)

# CC_REGS=0x8754[,0x876e] -- cetak register + isi memori yang ditunjuk SI/BX
# setiap kali offset itu dieksekusi. Untuk menjawab "nilainya yang beda, atau
# tabelnya?" tanpa menebak.
# CC_RNGLOG=<berkas> -- catat setiap panggilan rnd() @0x5A5B: seed sebelum,
# argumen n, dan hasilnya. Dipakai untuk MEMBUKTIKAN bahwa tiruan RNG di port
# menghasilkan urutan yang sama, bukan cuma rumus yang mirip.
CC_RNGLOG = os.environ.get("CC_RNGLOG")
if CC_RNGLOG:
    _rl = open(CC_RNGLOG, "w")
    _rpend = []

    def _seed():
        return rdw(uc.reg_read(UC_X86_REG_DS) * 16 + 0x71A)

    def hook_rnd_masuk(uc, addr, size, user):
        sp = uc.reg_read(UC_X86_REG_SP)
        n = rdw(SS_() * 16 + sp + 2)          # argumen: [SP+2] sesudah call near
        _rpend.append((_seed(), n))

    def hook_rnd_keluar(uc, addr, size, user):
        if _rpend:
            s0, n = _rpend.pop()
            _rl.write("%04x %d %d\n" % (s0, n, uc.reg_read(UC_X86_REG_DX)))

    uc.hook_add(UC_HOOK_CODE, hook_rnd_masuk, None, CODE + 0x5A5B, CODE + 0x5A5B)
    uc.hook_add(UC_HOOK_CODE, hook_rnd_keluar, None, CODE + 0x5A71, CODE + 0x5A71)

CC_REGS = [int(x, 0) for x in os.environ.get("CC_REGS", "").split(",") if x.strip()]
if CC_REGS:
    def hook_regs(uc, addr, size, user):
        si = uc.reg_read(UC_X86_REG_SI)
        ds = uc.reg_read(UC_X86_REG_DS)
        try:
            mem = bytes(uc.mem_read(ds * 16 + si, 16))
        except Exception:
            mem = b""
        print("  [regs %04x] ax=%04x bx=%04x cx=%04x si=%04x ds=%04x [ds:si]=%s |%s|"
              % (addr - CODE, uc.reg_read(UC_X86_REG_AX), uc.reg_read(UC_X86_REG_BX),
                 uc.reg_read(UC_X86_REG_CX), si, ds,
                 " ".join("%02x" % c for c in mem),
                 "".join(chr(c) if 32 <= c < 127 else "." for c in mem)))

    for _a in CC_REGS:
        uc.hook_add(UC_HOOK_CODE, hook_regs, None, CODE + _a, CODE + _a)

uc.hook_add(UC_HOOK_CODE, hook_code, None, CODE + 0x2692, CODE + 0x2692)
uc.hook_add(UC_HOOK_CODE, hook_code, None, CODE + 0x27b4, CODE + 0x27b4)

# diagnosa: hitung entry tiap fungsi gambar
drawcnt = {}
def mk_counter(name):
    def h(uc, addr, size, user):
        if name not in drawcnt:
            print("  [trace] first %s (phase=%s s5035=%d)" % (name, phase[0], s5035[0]))
        drawcnt[name] = drawcnt.get(name, 0) + 1
    return h
for nm, a in [("278e", 0x278e), ("2714", 0x2714), ("672f", 0x672f),
              ("6869", 0x6869), ("18db", 0x18db), ("3f0f", 0x3f0f), ("5035", 0x5035),
              ("131a", 0x131a), ("498c", 0x498c), ("2e90", 0x2e90), ("58c9", 0x58c9),
              ("5911", 0x5911), ("26ae", 0x26ae)]:
    uc.hook_add(UC_HOOK_CODE, mk_counter(nm), None, CODE + A(a), CODE + A(a))

from PIL import Image
CGA = [(0, 0, 170), (0, 170, 170), (170, 0, 170), (170, 170, 170)]


def capture_cga(path):
    vram = bytes(uc.mem_read(0xB8000, 0x4000))
    im = Image.new("RGB", (320, 200))
    px = im.load()
    for row in range(200):
        base = (0x2000 if row & 1 else 0) + (row >> 1) * 80
        for cb in range(80):
            byte = vram[base + cb]
            for p in range(4):
                px[cb * 4 + p, row] = CGA[(byte >> (6 - 2 * p)) & 3]
    im.save(path)


# Bypass menu: hook fungsi keputusan (341a=mode, 32bb=level, 3322=goal) untuk
# langsung memilih, lalu di mode play feed SPACE utk jalankan bola.
import sys
import json
GOAL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
MODE = int(sys.argv[2]) if len(sys.argv) > 2 else 2
# ⚠ work/emu_caps adalah GROUND TRUTH (dirujuk port/*.py dan work/*.py).
# Saat menjalankan EXE REKONSTRUKSI, WAJIB arahkan CC_OUT ke folder lain --
# kalau tidak, keluaran parsialnya menimpa sumber kebenaran.
OUT = os.environ.get("CC_OUT") or \
    r"C:\Projects\Creative_Contraptions\work\emu_caps"
os.makedirs(OUT, exist_ok=True)

# --- OBSERVE mode: navigasi ke mode game & tangkap layar asli (ground truth) ---
# OBSERVE=review|zany|mixup|fillmech ; tangkap VRAM tiap flip, umpan tombol tiap getchar.
OBSERVE = os.environ.get("OBSERVE")
OBS_GAMEMODE = {"review": 1, "fillmech": 2, "zany": 3, "mixup": 4, "menu": 0}.get(OBSERVE, 0)
# urutan tombol (nilai balik 1814 berturut); ENTER=0x0d SPACE=0x20 ESC=0x1b; panah=0x00,scancode
_R = [0x00, 0x4D]   # panah kanan
OBS_KEYS = {
    "review":  [0x0D] * 24 + [0x1B],
    "zany":    _R * 4 + [0x0D] + _R * 3 + [0x0D] + _R * 3 + [0x0D, 0x1B],
    "fillmech": _R * 3 + [0x0D] + _R * 2 + [0x0D, 0x1B],
    "mixup":   _R * 3 + [0x0D] + _R * 3 + [0x0D, 0x1B],
    "menu":    [0x1B],
    "title":   [0x1B],
}.get(OBSERVE, [])
obs_keyq = list(OBS_KEYS)
OBSDIR = r"C:\Projects\Creative_Contraptions\work\obs_%s" % (OBSERVE or "none")
obs_n = [0]
obs_last = [None]


rev_mech = [0]
P_51C = DGROUP * 16 + 0x51c
review_layout = {"intro": None, "fixed": None, "mechs": {}}


def _dg_str(ptr):
    out = b""
    p = DGROUP * 16 + ptr
    for _ in range(200):
        c = uc.mem_read(p, 1)[0]
        if c == 0:
            break
        out += bytes([c]); p += 1
    return out.decode("latin1")


def _dump_381a(off, n):
    """Decode n record 12-byte tabel gambar teks/sprite (format 381a/3769)."""
    recs = []
    for i in range(n):
        r = bytes(uc.mem_read(DGROUP * 16 + off + i * 12, 12))
        y = struct.unpack_from("<H", r, 2)[0]
        x = struct.unpack_from("<H", r, 4)[0]
        ptr = struct.unpack_from("<H", r, 10)[0]
        if r[0] < 0x80:
            recs.append({"kind": "text", "x": x, "y": y, "sw": r[7], "sh": r[6],
                         "col": r[8], "s": _dg_str(ptr)})
        else:
            recs.append({"kind": "sprite", "x": y, "y": x, "sptr": ptr,
                         "w": r[7], "h": r[6]})
    return recs
def hook_obs_3020_entry(uc, addr, size, user):   # 0x3020: paksa mekanisme rev_mech
    if OBSERVE:
        print("  [obs] 3020 entry, set 0x51c=%d" % rev_mech[0])
        uc.mem_write(P_51C, struct.pack("<H", rev_mech[0]))
def hook_obs_3020_draw(uc, addr, size, user):    # 0x3075: layar detail selesai digambar
    if OBSERVE:
        idx = rev_mech[0]
        _obs_cap()
        if idx not in review_layout["mechs"]:
            tbl = struct.unpack_from("<H", bytes(uc.mem_read(DGROUP * 16 + 0x14f6 + idx * 2, 2)), 0)[0]
            cnt = struct.unpack_from("<H", bytes(uc.mem_read(DGROUP * 16 + 0x1508 + idx * 2, 2)), 0)[0]
            cnt = min(cnt, 30)
            review_layout["mechs"][idx] = {"tbl": tbl, "cnt": cnt, "recs": _dump_381a(tbl, cnt)}
            if review_layout["fixed"] is None:
                review_layout["fixed"] = _dump_381a(0x14d2, 3)
        rev_mech[0] = (rev_mech[0] + 1) % 9
def hook_obs_2fde(uc, addr, size, user):         # 0x3009: layar intro selesai
    if OBSERVE:
        _obs_cap()
        if review_layout["intro"] is None:
            review_layout["intro"] = _dump_381a(0xc04, 7)


def _obs_cap():
    """Tangkap layar VRAM saat ini (dedupe) ke OBSDIR."""
    if obs_n[0] >= 60:
        return
    vr = bytes(uc.mem_read(0xB8000, 0x4000))
    if vr == obs_last[0]:
        return
    obs_last[0] = vr
    if obs_n[0] == 0:
        os.makedirs(OBSDIR, exist_ok=True)
    capture_cga(os.path.join(OBSDIR, "obs%02d.png" % obs_n[0]))
    obs_n[0] += 1
patched = [False]          # True setelah masuk contraption mode (5035 ke-2)
s5035 = [0]
phase = ["nav"]
space_sent = [False]
icnt = [0]
ballpath = []
draws672 = []
scene672 = []        # rakitan contraption statis (sebelum bola) utk latar per-varian
scene_frozen = [False]  # True setelah layar-awal selesai (poll input pertama)
title672 = []        # sprite LAYAR JUDUL (digambar sebelum contraption pertama dimuat)
title_frozen = [False]
draworder = []
frameno = [0]        # dihitung tiap 6869 flip saat started
ballframes = []      # (x, y, frame) bola per gambar
inplay = [False]           # True setelah mode dipilih (341a)
started = [False]          # True saat 18db play-mode berjalan (mulai capture)
balldone = [False]         # True saat run bola selesai (0x2450) -> 1791 boleh balikan key
c1814 = [0]
CAP_ATTRACT = (os.environ.get("ATTRACT", "1") == "1") and not OBSERVE


def ret_ax(v):
    uc.reg_write(UC_X86_REG_AX, v & 0xFFFF)
    force_ret_near()


P_3B2 = DGROUP * 16 + 0x3b2
def hook_5035(uc, addr, size, user):
    s5035[0] += 1
    if s5035[0] == 1:                          # attract: patch goal -> demo goal N
        uc.mem_write(P_3B2, struct.pack("<H", GOAL))
        patched[0] = True


# Paksa varian tertentu: hook RNG 5a5b; bila dipanggil DARI DALAM 5035
# (return-addr di [0x5035,0x5318)) balikan VARIANT -> loader pilih varian itu
# secara deterministik (bukan acak). VARIANT<0 = biarkan acak (perilaku asli).
VARIANT = int(os.environ.get("VARIANT", "-1"))
VTAG = "" if VARIANT < 0 else "_v%d" % VARIANT   # suffix output per-varian
def hook_5a5b(uc, addr, size, user):
    if VARIANT < 0:
        return
    ssg = uc.reg_read(UC_X86_REG_SS); spx = uc.reg_read(UC_X86_REG_SP)
    reta = struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + spx, 2)), 0)[0]
    if 0x5035 <= reta < 0x5318:                # RNG pemilihan varian di dalam 5035
        ret_ax(VARIANT)


P_2E4 = DGROUP * 16 + 0x2e4
def hook_input(uc, addr, size, user):
    off = addr - CODE
    if not patched[0]:               # poll input pertama saat layar judul -> bekukan capture
        title_frozen[0] = True
    if OBSERVE and inplay[0]:
        # 1791 poll: balikan "tak ada tombol" saat FLUSH (36ef, ret 0x36f8/0x36ff) agar
        # loop-flush selesai; "ada tombol" utk input asli (3c4f/3020) agar tombol terkirim.
        if off == 0x1791:
            ssg = uc.reg_read(UC_X86_REG_SS); spx = uc.reg_read(UC_X86_REG_SP)
            reta = struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + spx, 2)), 0)[0]
            ret_ax(0x00 if reta in (0x36f8, 0x36ff) else 0x0D)
            return
        if off == 0x1814:
            scene_frozen[0] = True          # layar-awal selesai -> bekukan capture latar
            ssg = uc.reg_read(UC_X86_REG_SS); spx = uc.reg_read(UC_X86_REG_SP)
            reta = struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + spx, 2)), 0)[0]
            if len(obs_keyq) >= len(OBS_KEYS) - 6:
                print("  [obs] 1814 called from ret=0x%04x (queue=%d)" % (reta, len(obs_keyq)))
            if OBSERVE != "review":
                _obs_cap()
            if not obs_keyq:
                uc.emu_stop(); return
            ret_ax(obs_keyq.pop(0)); return
    if off == 0x1814:
        c1814[0] += 1
        if started[0] and CAP_ATTRACT:
            print("  [attract] 18db selesai, stop capture")
            uc.emu_stop()
            return
        ret_ax(0x0D)
        return
    # 1791 = poll input. Bedakan berdasarkan RETURN ADDRESS:
    #  - dari op0x0F wait (call@0x2342 -> ret 0x2345): balikan SPACE utk majukan.
    #  - dari final-wait (call@0x248e -> ret 0x2491): balikan SPACE utk keluar.
    #  - lainnya (poll ESC / delay saat run bola): no-key (0), agar run tak terganggu.
    ssg = uc.reg_read(UC_X86_REG_SS); spx = uc.reg_read(UC_X86_REG_SP)
    reta = struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + spx, 2)), 0)[0]
    if reta in (0x2345, 0x2491):
        ret_ax(0x20)
        return
    v = struct.unpack_from("<h", bytes(uc.mem_read(P_2E4, 2)), 0)[0]
    if v > 0:
        uc.mem_write(P_2E4, struct.pack("<h", v - 1))
    icnt[0] += 1
    if icnt[0] < 400000 and len(ballpath) < 40000:
        ret_ax(0)                              # no-key: biarkan run bola berjalan
        return
    uc.emu_stop()


def hook_balldone(uc, addr, size, user):    # 0x2450: run bola selesai
    balldone[0] = True


scripts = []    # (kind, script_offset, bytes) per part sesuai urutan eksekusi
def _dump_script(kind):
    pc = struct.unpack_from("<H", bytes(uc.mem_read(P_3AE, 2)), 0)[0]
    if pc == 0:
        return
    raw = bytes(uc.mem_read(DGROUP * 16 + pc, 600))
    scripts.append((kind, pc, raw, None))   # true_len diisi hook_vm saat op0xFF

c2823 = []       # (params, [ball points]) tiap panggilan 2823 (interpolator parabola)
cur2823 = [None]
pending_op = [None]
def _snap_op(kind):
    if not started[0]:
        return
    bp = uc.reg_read(UC_X86_REG_BP)
    def w(a): return struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + a, 2)), 0)[0]
    pc = struct.unpack_from("<H", bytes(uc.mem_read(P_3AE, 2)), 0)[0]
    ob = list(uc.mem_read(DGROUP * 16 + pc, 4))     # sd 4 byte operand
    cx = struct.unpack_from("<h", bytes(uc.mem_read(DGROUP * 16 + 0x260, 2)), 0)[0]
    cy = struct.unpack_from("<h", bytes(uc.mem_read(DGROUP * 16 + 0x25e, 2)), 0)[0]
    pending_op[0] = {"op": kind, "base_x": w(0x22), "base_y": w(0x24),
                     "cur_x": cx, "cur_y": cy, "operand": ob}
def hook_op03_entry(uc, addr, size, user):
    _snap_op("op03")
def hook_op0c_entry2(uc, addr, size, user):
    _snap_op("op0c")
def hook_2823_entry(uc, addr, size, user):   # 0x2829: setelah mov bp,sp
    if not started[0]:
        return
    bp = uc.reg_read(UC_X86_REG_BP)
    def w(off):
        return struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + off, 2)), 0)[0]
    params = {"A": w(0x2c), "fx": w(0x2e), "fy": w(0x30),
              "p32": w(0x32), "p34": w(0x34), "N": w(0x36), "flag": w(0x38)}
    cur2823[0] = {"params": params, "pts": [], "trig": pending_op[0]}
    c2823.append(cur2823[0])


part_idx = [-1]
ballbases = []   # (part_idx, base_x, base_y) tiap panggilan 2714
def hook_2823_exit(uc, addr, size, user):    # 0x29af: ret 2823
    cur2823[0] = None


# --- tangkap frame animasi NYATA: VRAM tiap langkah gambar (bola+part), dedupe ---
VF = r"C:\Projects\Creative_Contraptions\work\vframes_goal%d%s" % (GOAL, VTAG)
vframe_last = [None]
vframe_n = [0]
VCAP = os.environ.get("VCAP") == "1"
def _capture_vframe():
    if not (started[0] and VCAP):
        return
    vr = bytes(uc.mem_read(0xB8000, 0x4000))
    if vr == vframe_last[0]:
        return
    vframe_last[0] = vr
    if vframe_n[0] == 0:
        os.makedirs(VF, exist_ok=True)
    if vframe_n[0] < int(os.environ.get("VFMAX", "600")):
        capture_cga(os.path.join(VF, "v%04d.png" % vframe_n[0]))
        vframe_n[0] += 1
def hook_278e_vframe(uc, addr, size, user):  # 0x2822 ret 278e
    _capture_vframe()


# --- tangkap posisi bola SEBENARNYA di layar via diff VRAM tiap gambar 26ae ---
ball_screen = []       # (cx, cy) pusat bola baru per gambar
vframe_ball = []       # (vframe_index, x, y) posisi bola pd tiap packed-frame bola
ball_sprite_saved = [None]
dbg_before = [None]
def _vram():
    return bytes(uc.mem_read(0xB8000, 0x4000))
def hook_ball_dbg_entry(uc, addr, size, user):
    if started[0]:
        dbg_before[0] = _vram()
def hook_ball_dbg_exit(uc, addr, size, user):   # 0x2713 ret 26ae
    if dbg_before[0] is None:
        return
    before = dbg_before[0]; after = _vram()
    xs = []; ys = []
    for row in range(200):
        base = (0x2000 if row & 1 else 0) + (row >> 1) * 80
        for cb in range(80):
            bb = before[base + cb]; aa = after[base + cb]
            if bb == aa:
                continue
            for p in range(4):
                pv = (aa >> (6 - 2 * p)) & 3
                pvb = (bb >> (6 - 2 * p)) & 3
                if pv != pvb and pv != 1:      # piksel baru jadi non-bg = bola baru
                    xs.append(cb * 4 + p); ys.append(row)
    if xs:
        cx = round(sum(xs) / len(xs)); cy = round(sum(ys) / len(ys))
        ball_screen.append((cx, cy, frameno[0]))
        vframe_ball.append((vframe_n[0], cx, cy))   # posisi bola pd indeks packed-frame
        # simpan sprite bola: pola piksel bola baru (bbox kecil) sekali
        if ball_sprite_saved[0] is None:
            minx, maxx = min(xs), max(xs); miny, maxy = min(ys), max(ys)
            if maxx - minx <= 12 and maxy - miny <= 12:
                w = maxx - minx + 1; h = maxy - miny + 1
                grid = [[-1] * w for _ in range(h)]
                after = _vram()
                for row in range(miny, maxy + 1):
                    base = (0x2000 if row & 1 else 0) + (row >> 1) * 80
                    for col in range(minx, maxx + 1):
                        cb = col >> 2; p = col & 3
                        pv = (after[base + cb] >> (6 - 2 * p)) & 3
                        if pv != 1:
                            grid[row - miny][col - minx] = pv
                ball_sprite_saved[0] = grid
    dbg_before[0] = None
    _capture_vframe()

def hook_2714_entry(uc, addr, size, user):   # 0x271a: setelah prologue 2714
    if not started[0]:
        return
    bp = uc.reg_read(UC_X86_REG_BP)
    bx = struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + 8, 2)), 0)[0]
    by = struct.unpack_from("<h", bytes(uc.mem_read(SS_() * 16 + bp + 0xa, 2)), 0)[0]
    ballbases.append((part_idx[0], bx, by))


c0c = [0]
def hook_op0c_entry(uc, addr, size, user):
    if started[0]:
        c0c[0] = struct.unpack_from("<H", bytes(uc.mem_read(P_3AE, 2)), 0)[0]
def hook_op0c_exit(uc, addr, size, user):
    if started[0] and c0c[0]:
        now = struct.unpack_from("<H", bytes(uc.mem_read(P_3AE, 2)), 0)[0]
        print("  [op0c] konsumsi %d byte (start byte setelah 0x0c)" % (now - c0c[0]))
        c0c[0] = 0

def hook_mechscript(uc, addr, size, user):  # 0x1b7d: setelah set 0x3ae (mekanisme)
    if started[0]:
        part_idx[0] += 1
        _dump_script("mech")

def hook_zanyscript(uc, addr, size, user):  # 0x1c44: setelah set 0x3ae (zany)
    if started[0]:
        part_idx[0] += 1
        _dump_script("zany")


def hook_delay26ba(uc, addr, size, user):   # spin-wait timer 0x2e4 -> decrement 1 (pacing benar)
    v = struct.unpack_from("<h", bytes(uc.mem_read(P_2E4, 2)), 0)[0]
    if v > 0:
        uc.mem_write(P_2E4, struct.pack("<h", v - 1))


def hook_672f(uc, addr, size, user):
    sp = uc.reg_read(UC_X86_REG_SP); ssg = uc.reg_read(UC_X86_REG_SS)
    def a(n): return struct.unpack_from("<H", bytes(uc.mem_read(ssg * 16 + sp + n, 2)), 0)[0]
    sptr, y, x, h, w = a(2), a(4), a(6), a(8), a(10)
    ys = y - 65536 if y >= 32768 else y
    xs = x - 65536 if x >= 32768 else x
    nb = (w // 4) * h
    data = bytes(uc.mem_read(DGROUP * 16 + sptr, nb)) if nb and nb < 5000 else b""
    # LAYAR JUDUL: sprite yg digambar sebelum contraption pertama dimuat (patched).
    if not patched[0] and not title_frozen[0]:
        title672.append((xs, ys, w, h, data))
    # ADEGAN STATIS: rakitan contraption pd LAYAR-AWAL (sebelum bola / sebelum input
    # pertama). scene_frozen menutup capture agar animasi demo tak mengotori.
    if patched[0] and not started[0] and not scene_frozen[0]:
        scene672.append((xs, ys, w, h, data))
    if not (started[0] or OBSERVE):
        return
    draws672.append((xs, ys, w, h, data))
    draworder.append((sptr, xs, ys, w, h, frameno[0]))


def hook_ball(uc, addr, size, user):   # FUN_1000_26ae = ball drawer
    if not started[0]:
        return
    x = struct.unpack_from("<h", bytes(uc.mem_read(DGROUP * 16 + 0x260, 2)), 0)[0]
    y = struct.unpack_from("<h", bytes(uc.mem_read(DGROUP * 16 + 0x25e, 2)), 0)[0]
    ballpath.append((x, y))
    ballframes.append((x, y, frameno[0]))
    if cur2823[0] is not None:
        cur2823[0]["pts"].append((x, y))


P_3AE = DGROUP * 16 + 0x3ae
vmtrace = []
c278e = [0]
def hook_vm(uc, addr, size, user):     # 0x1cd2: VM dispatch head
    if not started[0]:
        return
    pc = struct.unpack_from("<H", bytes(uc.mem_read(P_3AE, 2)), 0)[0]
    op = uc.mem_read(DGROUP * 16 + pc, 1)[0]
    vmtrace.append((pc, op))
    if op == 0xFF and scripts:          # akhir skrip part sekarang -> catat true_len
        k, off, raw, _ = scripts[-1]
        scripts[-1] = (k, off, raw, pc - off + 1)

def hook_278e_stop(uc, addr, size, user):
    if not started[0]:
        return
    c278e[0] += 1
    if c278e[0] > 1500:
        print("  [loop] 278e>1500, stop. last VM (pc,op):", vmtrace[-30:])
        uc.emu_stop()


slotpass = [0, 0]
def hook_mechmatch(uc, addr, size, user):
    # 0x1b13: mekanisme salah -> gagal & abort. Paksa ke 0x1b51 (path "cocok").
    slotpass[0] += 1
    uc.reg_write(UC_X86_REG_IP, 0x1b51)

def hook_zanymatch(uc, addr, size, user):
    # 0x1bcd: zany salah -> set 0x842 (abort di iterasi berikut). Paksa ke 0x1c0b (cocok).
    slotpass[1] += 1
    uc.reg_write(UC_X86_REG_IP, 0x1c0b)


# --- Navigasi menu deterministik menuju PLAY mode (case 2 Fill Mechanisms) ---
def hook_menu_mode(uc, addr, size, user):   # 341a -> pilih mode
    inplay[0] = True
    if OBSERVE == "menu":
        return                    # biarkan 341a menggambar menu; input hook tangkap + ESC
    m = OBS_GAMEMODE if OBSERVE else MODE
    print("  [nav] 341a -> mode", m)
    ret_ax(m)

def hook_menu_level(uc, addr, size, user):  # 32bb -> pilih level 1
    print("  [nav] 32bb -> level 1")
    ret_ax(1)

def hook_menu_goal(uc, addr, size, user):   # 3322 -> pilih goal N
    print("  [nav] 3322 -> goal", GOAL)
    ret_ax(GOAL)

def hook_30bb(uc, addr, size, user):        # konfirmasi mode 2 -> !=-1
    print("  [nav] 30bb")
    ret_ax(0)

def hook_ret0(uc, addr, size, user):        # 312a/31da -> !=-1 agar lanjut ke menu
    print("  [nav] ret0 @ off=0x%x" % (addr - CODE))
    ret_ax(0)

def hook_2e90(uc, addr, size, user):        # skip penempatan part -> 0x2e8=0 (!= -1)
    if inplay[0]:
        print("  [nav] 2e90 skip")
        ret_ax(0)

def hook_18db_entry(uc, addr, size, user):  # mulai capture pada 18db pertama
    balldone[0] = False
    if CAP_ATTRACT:
        # capture 18db ATTRACT (contraption sudah solved dgn part benar)
        if not started[0]:
            print("  [attract] 18db start capture (solved contraption)")
            started[0] = True
        return
    if not inplay[0]:
        force_ret_near()                    # lewati 18db attract (loop tak berujung)
        return
    if not started[0]:
        print("  [nav] 18db PLAY start capture")
        started[0] = True

def hook_58c9(uc, addr, size, user):        # dipanggil tepat setelah 18db play -> selesai
    if started[0]:
        # dump & stop
        _dump_and_stop()

def _dump_and_stop():
    uc.emu_stop()


FRAMES = os.path.join(r"C:\Projects\Creative_Contraptions\work\playframes")
CAP = os.environ.get("CAPFRAMES") == "1"
def hook_flip(uc, addr, size, user):   # 6869 = frame flip/refresh (hitung frame)
    if OBSERVE == "title":             # tangkap SEMUA flip awal (cari layar judul)
        _obs_cap()
    elif OBSERVE and OBSERVE != "review" and inplay[0]:
        _obs_cap()
    if not started[0]:
        return
    frameno[0] += 1


hooks = [(0x5035, hook_5035), (0x5a5b, hook_5a5b), (0x1791, hook_input), (0x1814, hook_input),
         (0x672f, hook_672f), (0x26ae, hook_ball),
         (0x1b13, hook_mechmatch), (0x1bcd, hook_zanymatch),
         (0x341a, hook_menu_mode), (0x32bb, hook_menu_level),
         (0x3322, hook_menu_goal), (0x30bb, hook_30bb),
         (0x2e90, hook_2e90), (0x18db, hook_18db_entry), (0x58c9, hook_58c9),
         (0x312a, hook_ret0), (0x31da, hook_ret0), (0x2450, hook_balldone),
         (0x26a2, hook_delay26ba), (0x26ba, hook_delay26ba), (0x27ec, hook_delay26ba),
         (0x1cd2, hook_vm), (0x278e, hook_278e_stop),
         (0x1b7d, hook_mechscript), (0x1c44, hook_zanyscript),
         (0x21e1, hook_op0c_entry), (0x227d, hook_op0c_exit),
         (0x271a, hook_2714_entry), (0x2829, hook_2823_entry), (0x29af, hook_2823_exit),
         (0x1fac, hook_op03_entry), (0x21e1, hook_op0c_entry2),
         (0x26ae, hook_ball_dbg_entry), (0x2713, hook_ball_dbg_exit),
         (0x2822, hook_278e_vframe)]
hooks.append((0x6869, hook_flip))
if OBSERVE:
    hooks += [(0x3020, hook_obs_3020_entry), (0x3075, hook_obs_3020_draw),
              (0x3009, hook_obs_2fde)]
for off, fn in hooks:
    uc.hook_add(UC_HOOK_CODE, fn, None, CODE + A(off), CODE + A(off))

start = uc.reg_read(UC_X86_REG_CS) * 16 + uc.reg_read(UC_X86_REG_IP)
try:
    uc.emu_start(start, 0, 0, 60000000)
except UcError as e:
    csnow = uc.reg_read(UC_X86_REG_CS); ipnow = uc.reg_read(UC_X86_REG_IP)
    print("UcError:", e, "CS:IP=%04X:%04X off=0x%X" % (csnow, ipnow, (csnow - LOAD_SEG) * 16 + ipnow))
csf = uc.reg_read(UC_X86_REG_CS); ipf = uc.reg_read(UC_X86_REG_IP)
print("FINAL CS:IP=%04X:%04X off=0x%X  balldone=%s inplay=%s started=%s" %
      (csf, ipf, (csf - LOAD_SEG) * 16 + ipf, balldone[0], inplay[0], started[0]))

print("EXIT state:", state["exit"], "unhandled INT:", state["unhandled"][:5], "1814count=", c1814[0])
print("entry fungsi gambar:", drawcnt, "GOAL", GOAL, "mech/zany pass=", slotpass)

if OBSERVE == "review":
    import json as _json
    _json.dump(review_layout, open(os.path.join(OUT, "review_layout.json"), "w"), indent=1)
    print("REVIEW LAYOUT: intro=%s fixed=%s mechs=%d" %
          (review_layout["intro"] is not None, review_layout["fixed"] is not None,
           len(review_layout["mechs"])))
    for idx in sorted(review_layout["mechs"]):
        m = review_layout["mechs"][idx]
        print("  mech %d (cnt=%d):" % (idx, m["cnt"]))
        for r in m["recs"]:
            if r["kind"] == "text":
                print("     text (%3d,%3d) sc=%dx%d col=%d  %r" %
                      (r["x"], r["y"], r["sw"], r["sh"], r["col"], r["s"]))
            else:
                print("     sprite (%3d,%3d) ptr=0x%04x" % (r["x"], r["y"], r["sptr"]))

# cocokkan sprite draw ke record GRAPH/MECHS (pencocokan byte EKSAK)
import json
def decode_rle(d):
    o = bytearray(); i = 0
    while i < len(d):
        if d[i] == 0xE4 and i + 2 < len(d):
            o.extend(bytes([d[i + 2]]) * d[i + 1]); i += 3
        else:
            o.append(d[i]); i += 1
    return bytes(o)

lookup = {}   # (w,h,bytes) -> (arch, idx)
for arch in ("GRAPH", "MECHS"):
    ab = open(os.path.join(D, arch), "rb").read()
    nrec = struct.unpack_from("<I", ab, 8)[0] // 12
    for i in range(nrec):
        a, mi, hh, ww, f, ln, off = struct.unpack_from("<BBBBHHI", ab, i * 12)
        if ww and hh and ln:
            dec = decode_rle(ab[off:off + ln])
            need = (ww // 4) * hh
            if len(dec) >= need:
                lookup[(ww, hh, dec[:need])] = (arch, i)

result = []
for (x, y, w, h, data) in draws672:
    key = (w, h, data)
    m = lookup.get(key)
    result.append({"x": x, "y": y, "w": w, "h": h,
                   "arch": m[0] if m else None, "idx": m[1] if m else -1})
matched = sum(1 for r in result if r["idx"] >= 0)
print("MODE %d GOAL %d: draw672=%d cocok=%d" % (MODE, GOAL, len(result), matched))

if OBSERVE in ("menu", "title"):
    import json as _json
    _json.dump(result, open(os.path.join(OUT, "sprites_%s.json" % OBSERVE), "w"))
    print("OBSERVE %s sprites (arch,idx,x,y,w,h):" % OBSERVE)
    for r in result:
        print("   %-6s idx=%-4s (%3d,%3d) %dx%d" %
              (r["arch"], r["idx"], r["x"], r["y"], r["w"], r["h"]))
# dump animasi part: (arch, idx, x, y, frame) per gambar sprite
anim = []
for r, do in zip(result, draworder):
    anim.append({"arch": r["arch"], "idx": r["idx"], "x": r["x"], "y": r["y"], "frame": do[5]})
json.dump(anim, open(os.path.join(OUT, "anim_goal%d%s.json" % (GOAL, VTAG)), "w"))
print("MAXFRAME: %d" % (frameno[0]))
# ADEGAN STATIS = rakitan contraption sebelum bola jalan (scene672), dedupe per
# posisi ambil GAMBAR TERAKHIR (part akhir menimpa animasi rakitan). Ini latar
# per-varian yang dipakai port (format sama draws_goalN.json: {arch,idx,x,y,w,h}).
_seen = {}
for (x, y, w, h, data) in scene672:
    _seen.setdefault((x, y), (w, h, data))   # keep FIRST pose per posisi (= frame awal)
_scene = []
for (x, y), (w, h, data) in _seen.items():
    m = lookup.get((w, h, data))
    _scene.append({"x": x, "y": y, "w": w, "h": h,
                   "arch": m[0] if m else None, "idx": m[1] if m else -1})
json.dump(_scene, open(os.path.join(OUT, "draws_goal%d%s.json" % (GOAL, VTAG)), "w"))
_sm = sum(1 for r in _scene if r["idx"] >= 0)
print("SCENE static: %d sprite (cocok=%d) -> draws_goal%d%s.json" %
      (len(_scene), _sm, GOAL, VTAG))

# LAYAR JUDUL: dedupe per posisi (gambar pertama), cocokkan, dump.
_tseen = {}
for (x, y, w, h, data) in title672:
    _tseen.setdefault((x, y), (w, h, data))
_title = []
for (x, y), (w, h, data) in _tseen.items():
    m = lookup.get((w, h, data))
    _title.append({"x": x, "y": y, "w": w, "h": h,
                   "arch": m[0] if m else None, "idx": m[1] if m else -1})
json.dump(_title, open(os.path.join(OUT, "title_sprites.json"), "w"))
print("TITLE sprites: %d (cocok=%d) -> title_sprites.json" %
      (len(_title), sum(1 for r in _title if r["idx"] >= 0)))
# jalur bola (dedupe kembar)
bp = []
for p in ballpath:
    if not bp or bp[-1] != list(p):
        bp.append(list(p))
json.dump(bp, open(os.path.join(OUT, "ball_mode%d_goal%d%s.json" % (MODE, GOAL, VTAG)), "w"))
print("BALL PATH: %d titik (%d mentah); contoh: %s" % (len(bp), len(ballpath), bp[:12]))
json.dump(draworder, open(os.path.join(OUT, "draworder_goal%d%s.json" % (GOAL, VTAG)), "w"))
json.dump(ballframes, open(os.path.join(OUT, "ballframes_goal%d%s.json" % (GOAL, VTAG)), "w"))
json.dump(ball_screen, open(os.path.join(OUT, "ballscreen_goal%d%s.json" % (GOAL, VTAG)), "w"))
json.dump(vframe_ball, open(os.path.join(OUT, "vframeball_goal%d%s.json" % (GOAL, VTAG)), "w"))
if ball_sprite_saved[0]:
    json.dump(ball_sprite_saved[0], open(os.path.join(OUT, "ball_physics_sprite.json"), "w"))
print("BALL SCREEN (VRAM) titik: %d; sprite bola %s; contoh: %s" %
      (len(ball_screen), "OK" if ball_sprite_saved[0] else "-", ball_screen[:12]))
# skrip animasi per part (urut eksekusi); true_len = panjang nyata (dari 0x3ae)
sc = [{"kind": k, "off": o, "true_len": tl, "bytes": list(bts[:(tl or 600)])}
      for (k, o, bts, tl) in scripts]
json.dump(sc, open(os.path.join(OUT, "scripts_goal%d.json" % GOAL), "w"))
json.dump(ballbases, open(os.path.join(OUT, "ballbases_goal%d.json" % GOAL), "w"))
json.dump(c2823, open(os.path.join(OUT, "interp_goal%d.json" % GOAL), "w"))
# simpan sprite bola gulir 0x5e6 (16x8) dari draws672
for (xs, ys, w, h, data) in draws672:
    if w == 16 and h == 8 and data:
        px = Image.new("RGB", (16, 8))
        pp = px.load()
        for row in range(8):
            for cb in range(4):
                byte = data[row * 4 + cb] if row * 4 + cb < len(data) else 0
                for pxi in range(4):
                    pp[cb * 4 + pxi, row] = CGA[(byte >> (6 - 2 * pxi)) & 3]
        px.save(os.path.join(OUT, "ball_sprite_5e6.png"))
        with open(os.path.join(OUT, "ball_sprite_5e6.bin"), "wb") as f:
            f.write(bytes(data))
        break
print("2823 CALLS: %d" % len(c2823))
for c in c2823[:9]:
    print("  ", c.get("trig"), "=>", c["params"])
print("PART SCRIPTS: %d" % len(scripts))
for (k, o, bts, tl) in scripts:
    print("  %-4s off=0x%04x true_len=%s" % (k, o, tl))
# ringkas: histogram sprite-ptr (ball = sptr yg muncul banyak dgn posisi berubah)
from collections import defaultdict
byptr = defaultdict(list)
for (sptr, x, y, w, h, fr) in draworder:
    byptr[(sptr, w, h)].append((x, y))
print("SPRITE-PTR yang bergerak (>=4 posisi berbeda):")
for k, pts in sorted(byptr.items(), key=lambda kv: -len(set(kv[1]))):
    uniq = list(dict.fromkeys(pts))
    if len(uniq) >= 4:
        print("  sptr=0x%04x w=%d h=%d  n=%d uniq=%d  %s" % (k[0], k[1], k[2], len(pts), len(uniq), uniq[:12]))
