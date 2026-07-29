"""Eksekutor VM: jalankan skrip tiap part sampai delay pertama (frame istirahat),
komposit semua op0x01 draw di posisi part+record.offset. Uji goal 1 vs ground truth."""
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
b = open(os.path.join(D, "ANIMATE"), "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
anim = {}
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
    if ln:
        anim.setdefault(a, []).append((off, ln))


def rec_off(idx):
    p = idx * 12
    return struct.unpack_from("<b", gb, p + 4)[0], struct.unpack_from("<b", gb, p + 5)[0]


def first_frame_draws(typ):
    """Jalankan skrip type sampai delay(op0x02) pertama; kumpulkan indeks op0x01 draw."""
    for off, ln in anim.get(typ, []):
        s = b[off:off + ln]
        i, N = 0, len(s)
        draws = []
        while i < N:
            op = s[i]; i += 1
            if op == 0xFF:
                break
            if op == 0x02:            # delay -> akhir frame pertama
                return draws
            if op == 0x01:
                while i < N and s[i] != 0xFF:
                    draws.append(s[i]); i += 1
                i += 1
            elif op in (0x07, 0x09):
                if i < N: draws.append(s[i]); i += 1
            elif op == 0x00:
                while i + 1 < N and s[i] != 0xFF: i += 2
                i += 1
            elif op in (0x03, 0x0C, 0x08, 0x0A): i += 2
            elif op == 0x04:
                m = s[i]; i += 1
                if m == 1: i += 6
                elif m in (2, 3):
                    while i + 1 < N and not (s[i] == 0xFF and s[i + 1] == 0xFF): i += 1
                    i += 2
            elif op == 0x11: i += 4
        if draws:
            return draws
    return []


goals = assets.parse_contrap(os.path.join(D, "CONTRAP"))
var = goals[1][0]
fb = cga.make_framebuffer()
for (y, x, typ) in var["zany"]:
    bm = graph.by_major.get(typ, [])
    draws = first_frame_draws(typ)
    print("type=%d (%d,%d) draws=%s (by_major=%d)" % (typ, x, y, draws, len(bm)))
    for idx in draws:
        if idx < len(bm):
            rec = graph.records[bm[idx]]
            ox, oy = rec_off(rec["idx"])
            fb.blit(graph.sprite(rec), (x + ox, y + oy))
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\vm_test2.png")
pygame.quit()
print("-> vm_test2.png")
