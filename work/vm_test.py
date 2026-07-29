"""Uji hipotesis deterministik: sprite zany = eksekusi op0x01 (komposit record
by_major[type][idx]) di posisi part + record.offset(byte4,5 signed). vs ground truth goal1."""
import os
import sys
import struct
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from PIL import Image
from cc import cga, assets

pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
gb = open(os.path.join(D, "GRAPH"), "rb").read()


def rec_offset(rec):
    """byte 4,5 record = offset (x,y) bertanda."""
    p = rec["idx"] * 12
    ox = struct.unpack_from("<b", gb, p + 4)[0]
    oy = struct.unpack_from("<b", gb, p + 5)[0]
    return ox, oy


# ANIMATE op0x01 lists per type
b = open(os.path.join(D, "ANIMATE"), "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
anim = {}
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
    if ln:
        anim.setdefault(a, []).append((off, ln))


def first_op01_list(typ):
    """Kembalikan daftar indeks sprite dari op0x01 PERTAMA di skrip type."""
    for off, ln in anim.get(typ, []):
        s = b[off:off + ln]
        i, N = 0, len(s)
        while i < N:
            op = s[i]; i += 1
            if op == 0xFF:
                break
            if op == 0x01:
                lst = []
                while i < N and s[i] != 0xFF:
                    lst.append(s[i]); i += 1
                return lst
            elif op in (0x07, 0x09):
                return [s[i]] if i < N else []
            elif op == 0x00:
                while i + 1 < N and s[i] != 0xFF: i += 2
                i += 1
            elif op in (0x03, 0x0C, 0x08, 0x0A): i += 2
            elif op == 0x02: i += 1
            elif op == 0x04:
                m = s[i]; i += 1
                if m == 1: i += 6
                elif m in (2, 3):
                    while i + 1 < N and not (s[i] == 0xFF and s[i + 1] == 0xFF): i += 1
                    i += 2
            elif op == 0x11: i += 4
    return []


goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
var = goals[1][0]
fb = cga.make_framebuffer()
BG = cga.PALETTE[cga.BG_INDEX]
for (y, x, typ) in var["zany"]:
    bm = graph.by_major.get(typ, [])
    lst = first_op01_list(typ)
    print("type=%d part(%d,%d) by_major=%d op01=%s" % (typ, x, y, len(bm), lst))
    for idx in lst:
        if idx < len(bm):
            rec = graph.records[bm[idx]]
            ox, oy = rec_offset(rec)
            fb.blit(graph.sprite(rec), (x + ox, y + oy))
big = pygame.transform.scale(fb, (640, 400))
pygame.image.save(big, r"C:\Projects\Creative_Contraptions\work\vm_test_goal1.png")
pygame.quit()
print("-> vm_test_goal1.png")
