import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from cc import cga, assets
import main
pygame.init()
random.seed(5)
g = main.Game(assets.find_data_dir())


def pal_idx(idm):
    for i, p in enumerate(g.palette):
        if idm in p[1]:
            return i
    return None


NAMES = {main.MENU: "MENU", main.LEVEL: "LEVEL", main.GOAL: "GOAL",
         main.PLAY: "PLAY", main.PLAYANIM: "PLAYANIM"}

# navigasi ke Fill Mech, main 1 goal, menang, lalu ESC
# ⚠ Sejak layar INSTRUKSI ada (menu9/11/12 -- gim menampilkannya sekali per
# mode, `if (k == 1)`), alurnya MENU -> LEVEL -> INSTRUKSI -> GOAL.
g.state = main.MENU; g.sel = 1; g._choose()   # Fill Mech -> LEVEL
g.sel = 0; g._choose()                          # Apprentice -> INSTRUKSI
assert g.state == main.INSTRUKSI, g.state
g._choose()                                     # ENTER -> GOAL
g.sel = 0; g._choose()                          # goal pertama -> PLAY
assert g.state == main.PLAY
gid_played = g.chosen_goal
for i, s in enumerate(g.slots):                 # isi semua benar
    g.cur_slot = i; g.cur_part = pal_idx(s["correct"]); g.key(pygame.K_RETURN)
g.key(pygame.K_SPACE)                           # -> menang (PLAYANIM)
print("setelah menang: state =", NAMES.get(g.state))
g.key(pygame.K_ESCAPE)                           # ESC setelah menang
print("ESC setelah menang -> state =", NAMES.get(g.state),
      "(harusnya GOAL)  sel-goal =", g.goal_ids[g.sel] if g.state == main.GOAL else "-")
assert g.state == main.GOAL, "GAGAL: harusnya GOAL!"

# dari GOAL, ESC -> MENU (naik satu tingkat)
g.key(pygame.K_ESCAPE)
print("ESC dari GOAL -> state =", NAMES.get(g.state), "(harusnya MENU)")
assert g.state == main.MENU

# ESC saat sedang main (PLAY) -> GOAL
g.state = main.MENU; g.sel = 1; g._choose(); g.sel = 0; g._choose(); g.sel = 0; g._choose()
assert g.state == main.PLAY
g.key(pygame.K_ESCAPE)
print("ESC saat PLAY -> state =", NAMES.get(g.state), "(harusnya GOAL)")
assert g.state == main.GOAL

print("\nNAV OK: menang/ESC -> GOAL; GOAL ESC -> MENU")
pygame.quit()
