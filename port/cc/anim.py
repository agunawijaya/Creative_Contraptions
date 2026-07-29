"""Interpreter animasi ANIMATE (VM) — fase awal: jalur gerak bola.

Model (hasil RE): tiap part contraption punya skrip animasi ber-id_major = tipe part,
diputar RELATIF ke posisi (x,y) part. Bola mengalir dari part ke part.
Grammar opcode: lihat CODE_MAP.md. Fokus modul ini: op0x00/0x08 (waypoint bola),
op0x03/0x0C (set basis). Opcode lain di-skip byte-nya dgn benar.
"""
import struct


def _sgn(v):
    return v - 0x100 if v >= 0xC8 else v


class AnimArchive:
    def __init__(self, path):
        b = open(path, "rb").read()
        self.raw = b
        n = struct.unpack_from("<I", b, 8)[0] // 12
        self.by_major = {}
        for i in range(n):
            a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
            if ln:
                self.by_major.setdefault(a, []).append((off, ln))

    def ball_points(self, major):
        """Semua titik bola relatif dari skrip milik tipe `major`."""
        pts = []
        for off, ln in self.by_major.get(major, []):
            pts += _parse_points(self.raw[off:off + ln])
        return pts


def _parse_points(s):
    """Kembalikan titik bola relatif (dx,dy) mengikuti basis dari op0x03/0x0C."""
    i, n = 0, len(s)
    bx = by = 0
    pts = []
    while i < n:
        op = s[i]; i += 1
        if op == 0xFF:
            break
        if op == 0x00:                       # daftar (dx,dy) bola
            while i + 1 < n and s[i] != 0xFF:
                pts.append((bx + _sgn(s[i]), by + _sgn(s[i + 1]))); i += 2
            i += 1
        elif op == 0x08:
            if i + 1 < n:
                pts.append((bx + _sgn(s[i]), by + _sgn(s[i + 1]))); i += 2
        elif op in (0x03, 0x0C):
            if i + 1 < n:
                bx = _sgn(s[i]); by = _sgn(s[i + 1]); i += 2
        elif op == 0x01:
            while i < n and s[i] != 0xFF:
                i += 1
            i += 1
        elif op == 0x02:
            i += 1
        elif op == 0x04:
            mode = s[i]; i += 1
            if mode == 1:
                i += 6
            elif mode in (2, 3):
                while i + 1 < n and not (s[i] == 0xFF and s[i + 1] == 0xFF):
                    i += 1
                i += 2
        elif op in (0x07, 0x09):
            i += 1
        elif op == 0x0A:
            i += 2
        elif op == 0x11:
            i += 4
        elif op in (0x05, 0x06, 0x0D, 0x0E, 0x0F, 0x10):
            pass
        else:
            break
    return pts


def build_ball_path(anim, parts):
    """parts = list (y,x,tipe) urut. Rangkai titik bola tiap part -> jalur penuh.
    Titik kembar berturut di-dedupe (agar gerak halus, bukan diam berkedip)."""
    path = []
    for (py, px, typ) in parts:
        for (dx, dy) in anim.ball_points(typ):
            p = (px + dx, py + dy)
            if 0 <= p[0] < 320 and 0 <= p[1] < 200:
                if not path or path[-1] != p:
                    path.append(p)
    return path

