from PIL import Image
import sys

D = r"C:\Projects\Creative_Contraptions\work\shots"
# Area game CGA 320x200 di pojok kanan-bawah jendela DOSBox
src = Image.open(D + "\\04_enter.png")
W, H = src.size
gx, gy = W - 322, H - 210
game = src.crop((gx, gy, W, H))
game.resize((game.width * 3, game.height * 3), Image.NEAREST).save(D + "\\zoom_04_full.png")

# Bar ikon mekanisme di baris paling bawah
bar = src.crop((gx, H - 40, W, H))
bar.resize((bar.width * 5, bar.height * 5), Image.NEAREST).save(D + "\\zoom_04_bar.png")
print("game area:", game.size, " bar:", bar.size)
