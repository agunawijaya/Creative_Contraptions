"""Uji hipotesis: indeks op0x01 di skrip ANIMATE = posisi record yg benar di by_major.
Bandingkan dgn hasil matching ground truth goal 1."""
import os
import sys
import struct
sys.path.insert(0, os.path.dirname(__file__))
from cc import assets

D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
b = open(os.path.join(D, "ANIMATE"), "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
anim = {}
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
    if ln:
        anim.setdefault(a, []).append((off, ln))


def op01_indices(script):
    """Kumpulkan semua indeks sprite dari op0x01/0x07/0x09 (draw sprite)."""
    i, N = 0, len(script)
    idxs = []
    while i < N:
        op = script[i]; i += 1
        if op == 0xFF:
            break
        if op == 0x01:
            while i < N and script[i] != 0xFF:
                idxs.append(script[i]); i += 1
            i += 1
        elif op in (0x07, 0x09):
            if i < N:
                idxs.append(script[i]); i += 1
        elif op == 0x00:
            while i + 1 < N and script[i] != 0xFF:
                i += 2
            i += 1
        elif op == 0x08:
            i += 2
        elif op in (0x03, 0x0C):
            i += 2
        elif op == 0x02:
            i += 1
        elif op == 0x04:
            m = script[i]; i += 1
            if m == 1:
                i += 6
            elif m in (2, 3):
                while i + 1 < N and not (script[i] == 0xFF and script[i + 1] == 0xFF):
                    i += 1
                i += 2
        elif op == 0x0A:
            i += 2
        elif op == 0x11:
            i += 4
    return idxs


# posisi benar (dari matching ground truth) di by_major
correct = {1: 1, 2: 0, 5: 0, 8: 4, 10: 0}   # type -> posisi record benar
for typ in (1, 2, 5, 8, 10):
    allidx = []
    for off, ln in anim.get(typ, []):
        allidx += op01_indices(b[off:off + ln])
    bm = graph.by_major.get(typ, [])
    print("type=%2d: by_major punya %d record; op01 indices=%s ; posisi benar(GT)=%d"
          % (typ, len(bm), sorted(set(allidx))[:12], correct[typ]))
