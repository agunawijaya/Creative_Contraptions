"""Sampel 4 warna dominan dari screenshot game asli."""
from PIL import Image
from collections import Counter

im = Image.open(r"C:\Projects\Creative_Contraptions\sceenshots\original_01.png").convert("RGB")
c = Counter(im.getdata())
print("Warna paling sering di screenshot asli:")
for rgb, n in c.most_common(10):
    print("  rgb%s : %d" % (rgb, n))
