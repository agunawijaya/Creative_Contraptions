"""Katalog komponen: tiap sprite + label, warna ASLI game (opaque, spt 672f).
Bandingkan colorkey vs opaque untuk diagnosa 'cyan menghilang'."""
import os, sys, json, glob
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))
FONT = pygame.font.SysFont("consolas", 13)
BIG = pygame.font.SysFont("consolas", 16, bold=True)

MECH_NAMES = {100: "Inclined Plane", 101: "Inclined Plane", 110: "Pulley", 111: "Pulley",
              112: "Pulley", 133: "Pulley", 115: "Wheel & Axle", 120: "Wedge",
              130: "Pendulum", 131: "Pendulum", 132: "Magnet", 135: "Screw",
              140: "Lever", 141: "Lever", 150: "Spring"}


def raw_sprite(arch, idx, opaque=True):
    """Sprite tanpa colorkey (opaque, spt game asli 672f menulis semua piksel)."""
    r = arch.records[idx]
    dec = assets.decode_rle(arch.raw[r["off"]:r["off"] + r["ln"]])
    need = (r["w"] // 4) * r["h"]
    if len(dec) < need:
        dec = dec + bytes(need - len(dec))
    surf = pygame.Surface((r["w"], r["h"]))
    for row in range(r["h"]):
        for cb in range(r["w"] // 4):
            if row * (r["w"] // 4) + cb >= len(dec):
                break
            b = dec[row * (r["w"] // 4) + cb]
            for p in range(4):
                surf.set_at((cb * 4 + p, row), cga.PALETTE[(b >> (6 - 2 * p)) & 3])
    if not opaque:
        surf.set_colorkey(cga.PALETTE[1])
    return surf


def build(entries, title, cols, cell, path):
    rows = (len(entries) + cols - 1) // cols
    W, H = cols * cell, rows * cell + 40
    canvas = pygame.Surface((W, H)); canvas.fill(cga.PALETTE[1])   # latar CYAN spt game
    canvas.blit(BIG.render(title, True, (0, 0, 0)), (8, 8))
    for i, (arch, idx, label) in enumerate(entries):
        cx = (i % cols) * cell
        cy = (i // cols) * cell + 36
        spr = raw_sprite(arch, idx, opaque=True)
        sc = min(2, (cell - 8) / max(spr.get_width(), 1), (cell - 24) / max(spr.get_height(), 1))
        sc = max(1, int(sc)) if sc >= 1 else sc
        spr2 = pygame.transform.scale(spr, (max(1, int(spr.get_width() * sc)),
                                            max(1, int(spr.get_height() * sc))))
        canvas.blit(spr2, (cx + (cell - spr2.get_width()) // 2, cy + 2))
        for j, ln in enumerate(label.split("\n")):
            canvas.blit(FONT.render(ln, True, (0, 0, 0)), (cx + 2, cy + cell - 30 + j * 13))
    Image.frombytes("RGB", (W, H), pygame.image.tostring(canvas, "RGB")).save(path)
    print("->", path, "(%d item)" % len(entries))


# --- MEKANISME: satu ikon per major MECHS ---
mech_entries = []
seen = set()
for r in mechs.records:
    mj = r["major"]
    if mj in MECH_NAMES and mj not in seen:
        seen.add(mj)
        mech_entries.append((mechs, r["idx"], "%s\nid=%d" % (MECH_NAMES[mj], mj)))
build(mech_entries, "MEKANISME (MECHS)", 5, 130,
      r"C:\Projects\Creative_Contraptions\work\catalog_mechs.png")

# --- ZANY OBJECT: major GRAPH yg muncul di goal/title ---
used = set()
for fp in glob.glob(r"C:\Projects\Creative_Contraptions\port\cc\draws\draws_*.json"):
    for d in json.load(open(fp)):
        if d.get("arch") == "GRAPH" and d["idx"] >= 0:
            used.add(graph.records[d["idx"]]["major"])
zany_entries = []
for mj in sorted(used):
    idxs = graph.by_major.get(mj, [])
    if idxs:
        zany_entries.append((graph, graph.records[idxs[0]]["idx"], "id=%d" % mj))
build(zany_entries, "ZANY OBJECT / PEMANDANGAN (GRAPH)", 8, 90,
      r"C:\Projects\Creative_Contraptions\work\catalog_zany.png")
pygame.quit()
