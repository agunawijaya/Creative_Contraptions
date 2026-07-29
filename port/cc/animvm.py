"""Animation VM (port dari FUN_1000_18db + tabel opcode @CS:0x23d4).

Interpreter bytecode skrip ANIMATE. Tahap 1 = PARSER: pecah skrip jadi daftar
(op, operands) untuk memvalidasi panjang-operand tiap opcode terhadap skrip nyata
yang diekstrak dari game (work/emu_caps/scripts_goal*.json). Rendering menyusul.

Semantik opcode (dari disassembly handler):
  0x00 waypoint bola : stream pasang (dx,dy) 2-byte, diakhiri 0xFF   (via 2714)
  0x01 frame sprite  : stream indeks-frame 1-byte,  diakhiri 0xFF   (via 278e)
  0x02 delay         : 1 byte
  0x03 reposisi bola : 2 byte (dx,dy) + set base       (kompleks, lihat catatan)
  0x04 motion/suara  : 1 byte mode + payload variabel
  0x05 grafik tetap  : 0 byte
  0x06 reset marker  : 0 byte  (0x266/0x262 = 0x140)
  0x07 reset+sprite  : 1 byte  (reset lalu 278e sekali)
  0x08 bola sekali   : 2 byte  (2714 sekali)
  0x09 sprite sekali : 1 byte  (278e sekali)
  0x0a reset+bola     : 2 byte  (reset lalu 2714 sekali)
  0x0c reposisi(2)   : payload variabel (x + count pasang)
  0x0d init-wait     : 0 byte
  0x0e enable-wait   : 0 byte
  0x0f poll-wait     : 0 byte  (tunggu SPACE/ENTER/ESC)
  0x10 skor mode4    : 0 byte
  0x11 multi-param   : payload variabel
  0xFF akhir skrip
"""

def _tdiv(a, b):
    """Pembagian integer truncate-toward-zero (konvensi C / long-div 0x7040)."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def interp_2823(fx, fy, tx, ty, N, A):
    """Port EKSAK FUN_1000_2823: gerak bola parabola dari (fx,fy) ke (tx,ty) N langkah.
    y linear; x = linear + lendutan parabola dikontrol A (grav/proyektil).
    Divalidasi 100% vs emulator (work/fit_interp)."""
    NA = -A
    xbase = (tx - fx) + _tdiv(NA * N * N, 100)
    pts = []
    for i in range(1, N):
        x = fx + _tdiv(xbase * i, N) - _tdiv(NA * i * i, 100)
        y = fy + _tdiv((ty - fy) * i, N)
        pts.append((x, y))
    pts.append((tx, ty))
    return pts


FIXED_LEN = {
    0x02: 1, 0x05: 0, 0x06: 0, 0x07: 1, 0x08: 2, 0x09: 1,
    0x0a: 2, 0x0d: 0, 0x0e: 0, 0x0f: 1, 0x10: 0, 0x03: 2, 0x0c: 2,
}
# 0x0d = tanda awal-loop; 0x0e = aktifkan mode-tunggu; 0x0f = akhir-loop, diikuti
# 1 byte hitungan (loop body op0d..op0f diulang N kali) / tombol-tunggu bila mode aktif.


def _stream_until_ff(s, i, stride):
    """op0x00/0x01: baca elemen ber-stride sampai ketemu 0xFF (yg ikut dikonsumsi)."""
    items = []
    while i < len(s):
        if s[i] == 0xFF:
            i += 1
            break
        items.append(tuple(s[i:i + stride]))
        i += stride
    return items, i


def parse_op04(s, i):
    """op0x04 (handler @0x2280): baca 1 byte mode N.
      N==1 -> payload 3 word (6 byte) tetap.
      N==2 atau 3 -> stream byte sampai penanda GANDA 0xFF 0xFF (ikut dikonsumsi).
      lainnya (mis. 0) -> tanpa payload.
    Catatan: 0xFF tunggal di dalam payload mode 2/3 BUKAN akhir skrip."""
    mode = s[i]; i += 1
    if mode == 1:
        payload = s[i:i + 6]; i += 6
        return ("op04", mode, payload), i
    if mode in (2, 3):
        start = i
        while i + 1 < len(s):
            if s[i] == 0xFF and s[i + 1] == 0xFF:
                i += 2
                break
            i += 1
        return ("op04", mode, s[start:i]), i
    return ("op04", mode, []), i


def parse(script):
    """Kembalikan daftar (op, data) + posisi akhir. Raise bila byte tak terkonsumsi rapi."""
    s = list(script)
    i = 0
    out = []
    while i < len(s):
        op = s[i]; i += 1
        if op == 0xFF:
            out.append(("end", None))
            break
        if op == 0x00:
            pts, i = _stream_until_ff(s, i, 2)
            out.append(("waypoints", pts))
        elif op == 0x01:
            fr, i = _stream_until_ff(s, i, 1)
            out.append(("frames", [f[0] for f in fr]))
        elif op == 0x04:
            node, i = parse_op04(s, i)
            out.append(node)
        elif op == 0x11:
            # multi-param: baca 4 word (dari handler baca beberapa word/byte) -- perkiraan
            vals = s[i:i + 8]; i += 8
            out.append(("op11", vals))
        elif op in FIXED_LEN:
            n = FIXED_LEN[op]
            out.append(("op%02x" % op, s[i:i + n]))
            i += n
        else:
            raise ValueError("opcode tak dikenal 0x%02x @ %d" % (op, i - 1))
    return out, i


if __name__ == "__main__":
    import json, os, sys
    goal = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    p = r"C:\Projects\Creative_Contraptions\work\emu_caps\scripts_goal%d.json" % goal
    scripts = json.load(open(p))
    ok = 0
    for n, sc in enumerate(scripts):
        b = bytes(sc["bytes"])
        tl = sc.get("true_len")
        try:
            nodes, end = parse(b)
            match = (end == tl)
            ok += match
            print("part %2d %-4s parse_len=%3d true_len=%s %s  %s" % (
                n, sc["kind"], end, tl, "OK " if match else "MISMATCH",
                " ".join(t[0] for t in nodes)))
        except Exception as e:
            print("part %2d %-4s GAGAL: %s" % (n, sc["kind"], e))
    print("COCOK true_len %d/%d" % (ok, len(scripts)))
