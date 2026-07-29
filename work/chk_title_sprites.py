import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
import pygame
from PIL import Image
from cc import cga, assets
pygame.init()
D = assets.find_data_dir()
graph = assets.Archive(os.path.join(D, "GRAPH"))
mechs = assets.Archive(os.path.join(D, "MECHS"))


def dump(arch, idxs, name):
    for i in idxs:
        r = arch.records[i]
        spr = arch.sprite_by_idx(i)
        big = pygame.transform.scale(spr, (r["w"] * 5, r["h"] * 5))
        Image.frombytes("RGB", (r["w"] * 5, r["h"] * 5),
                        pygame.image.tostring(big, "RGB")).save(
            r"C:\Projects\Creative_Contraptions\work\spr_%s_%d.png" % (name, i))
        print("%s idx %d: %dx%d major=%d" % (name, i, r["w"], r["h"], r["major"]))


# lever box (id141) frame 26,27 ; spring box (id150) frame 28,29
dump(mechs, [26, 27], "lever")
dump(mechs, [28, 29], "springbox")
# tiga per + cangkir (id79) semua frame
dump(graph, [i for i in graph.by_major.get(79, [])], "spring79")
# drum (id80)
dump(graph, [i for i in graph.by_major.get(80, [])], "drum80")
pygame.quit()
