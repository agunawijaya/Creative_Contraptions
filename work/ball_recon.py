"""Rekonstruksi jalur bola dari data op0x00 ANIMATE + urutan part (draw list emulator).
Cek koherensi: apakah membentuk jalur mengalir lewat mesin."""
import os, sys, struct, json
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from cc import cga, assets

pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
gg = open(os.path.join(D, "GRAPH"), "rb").read()
mm = open(os.path.join(D, "MECHS"), "rb").read()
ab = open(os.path.join(D, "ANIMATE"), "rb").read()
n = struct.unpack_from("<I", ab, 8)[0] // 12
anim = {}
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", ab, i * 12)
    if ln:
        anim.setdefault(a, []).append((off, ln))


def sgn(v): return v - 0x100 if v >= 0xc8 else v


def op00_points(typ):
    """waypoint bola relatif (dx,dy) dari op0x00 skrip type (basis via op0x03/0c)."""
    pts = []
    for off, ln in anim.get(typ, []):
        s = ab[off:off + ln]
        i, N = 0, len(s); bx = by = 0
        while i < N:
            op = s[i]; i += 1
            if op == 0xFF: break
            if op == 0x00:
                while i + 1 < N and s[i] != 0xFF:
                    pts.append((bx + sgn(s[i]), by + sgn(s[i + 1]))); i += 2
                i += 1
            elif op == 0x08:
                if i + 1 < N: pts.append((bx + sgn(s[i]), by + sgn(s[i + 1]))); i += 2
            elif op in (0x03, 0x0C):
                if i + 1 < N: bx = sgn(s[i]); by = sgn(s[i + 1]); i += 2
            elif op == 0x01:
                while i < N and s[i] != 0xFF: i += 1
                i += 1
            elif op == 0x02: i += 1
            elif op == 0x04:
                m = s[i]; i += 1
                if m == 1: i += 6
                elif m in (2, 3):
                    while i + 1 < N and not (s[i] == 0xFF and s[i + 1] == 0xFF): i += 1
                    i += 2
            elif op in (0x07, 0x09): i += 1
            elif op == 0x0A: i += 2
            elif op == 0x11: i += 4
    return pts


def major_of(arch, idx):
    raw = gg if arch == "GRAPH" else mm
    return raw[idx * 12]


draws = json.load(open(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal1.json"))
fb = cga.make_framebuffer()
g_ = __import__("main", fromlist=["Game"])
# gambar contraption sbg latar
for d in draws:
    if d["idx"] < 0: continue
    spr = (graph if d["arch"] == "GRAPH" else mechs).sprite_by_idx(d["idx"])
    if spr: fb.blit(spr, (d["x"], d["y"]))

# jalur bola: per part (urut draw), op0x00 offset ke posisi part
allpts = []
for d in draws:
    if d["idx"] < 0: continue
    typ = major_of(d["arch"], d["idx"])
    for (dx, dy) in op00_points(typ):
        allpts.append((d["x"] + dx, d["y"] + dy))
print("titik bola:", len(allpts), "contoh:", allpts[:10])
for (x, y) in allpts:
    if 0 <= x < 320 and 0 <= y < 200:
        pygame.draw.circle(fb, (255, 255, 0), (x, y), 1)
pygame.image.save(pygame.transform.scale(fb, (640, 400)), r"C:\Projects\Creative_Contraptions\work\ball_recon.png")
pygame.quit()
print("-> ball_recon.png")
