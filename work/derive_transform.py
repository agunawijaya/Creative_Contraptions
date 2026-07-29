"""Pasangkan koord LOGIS (ballpath 0x260/0x25e) dgn koord LAYAR (ballscreen VRAM),
per 26ae, utk menurunkan transform logis->layar (mungkin per-part / affine)."""
import json
OUT = r"C:\Projects\Creative_Contraptions\work\emu_caps"
logic = json.load(open(OUT + r"\ball_mode2_goal1.json"))   # logis (deduped)
screen = json.load(open(OUT + r"\ballscreen_goal1.json"))  # layar (x,y,frame)
print("logic:", len(logic), "screen:", len(screen))
n = min(len(logic), len(screen))
print(" i  logis     ->  layar    dx   dy")
prev = None
for i in range(n):
    lx, ly = logic[i]
    sx, sy = screen[i][0], screen[i][1]
    dx, dy = sx - lx, sy - ly
    mark = ""
    if prev and (abs(lx - prev[0]) > 20 or abs(ly - prev[1]) > 20):
        mark = "  <-- lompatan logis (part baru?)"
    print("%3d (%4d,%4d) -> (%3d,%3d)  %4d %4d%s" % (i, lx, ly, sx, sy, dx, dy, mark))
    prev = (lx, ly)
