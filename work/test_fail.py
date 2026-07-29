import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
import main

pygame.init()
g = main.Game(assets.find_data_dir())
fb = cga.make_framebuffer()
g.key(pygame.K_RETURN); g.key(pygame.K_DOWN); g.key(pygame.K_RETURN); g.key(pygame.K_RETURN)  # Fill goal1
tp = {t: i for i, (t, _) in enumerate(main.MECH_TYPES)}
# isi B & C benar, A biarkan KOSONG (salah)
g.cur_slot = 1; g.cur_part = tp[g.slots[1]["correct"]]; g.key(pygame.K_RETURN)
g.cur_slot = 2; g.cur_part = tp[g.slots[2]["correct"]]; g.key(pygame.K_RETURN)
print("slot filled:", [(chr(0x41+i), s["filled"], s["correct"]) for i, s in enumerate(g.slots)])
# SPACE -> GAGAL di A (kosong): bola jalan DI ATAS build, berhenti di A
g.key(pygame.K_SPACE)
print("SPACE -> running=%s fail_slot=%s ball_path_len=%d" %
      (g.running, g.run_fail_slot, len(g.ball_path)))
from PIL import Image
mid = None
for step in range(400):
    g.tick()
    if step == 8:
        g.draw(fb)
        mid = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
    if not g.running and g.ball_i < 0:
        break
print("run selesai. msg=%s" % g.message)
g.draw(fb)
end = Image.frombytes("RGB", (640, 400), pygame.image.tostring(pygame.transform.scale(fb, (640, 400)), "RGB"))
sheet = Image.new("RGB", (640, 800))
sheet.paste(mid, (0, 0)); sheet.paste(end, (0, 400))
sheet.save(r"C:\Projects\Creative_Contraptions\work\fail_A.png")
pygame.quit()
