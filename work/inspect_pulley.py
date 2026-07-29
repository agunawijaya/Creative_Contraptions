"""Baca sprite katrol pixel demi pixel. Temukan ujung tali magenta yang
SUDAH ADA di dalam sprite -- itulah titik sambungan sebenarnya, bukan tebakan.
"""
import struct
from PIL import Image

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]
CH = {0: ".", 1: "c", 2: "M", 3: "#"}   # . hitam  c cyan  M magenta  # putih


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1]); i += 3
        else:
            out.append(data[i]); i += 1
    return bytes(out)


b = open(D + "\\MECHS", "rb").read()
rec = next(struct.unpack_from("<BBBBHHI", b, i * 12)
           for i in range(31)
           if struct.unpack_from("<BBBBHHI", b, i * 12)[0] == 110)
a, bb, h, w, f, ln, off = rec
dec = decode_e4(b[off:off + ln])
wb = w // 4

# indeks warna per pixel
grid = [[0] * w for _ in range(h)]
for r in range(h):
    for cb in range(wb):
        byte = dec[r * wb + cb]
        for p in range(4):
            grid[r][cb * 4 + p] = (byte >> (6 - 2 * p)) & 3

print("Sprite katrol id=110  %dx%d\n" % (w, h))
print("   " + "".join(str(x % 10) for x in range(w)))
for r in range(h):
    print("%2d " % r + "".join(CH[grid[r][x]] for x in range(w)))

# Cari pixel magenta (tali) yang menyentuh tepi bawah / paling bawah
mag = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == 2]
print("\nJumlah pixel magenta (tali+detail): %d" % len(mag))
if mag:
    ymax = max(y for x, y in mag)
    bottom = [(x, y) for x, y in mag if y == ymax]
    print("Baris magenta paling bawah: y=%d, di x=%s" % (ymax, [x for x, y in bottom]))
    print("=> TITIK SAMBUNGAN TALI (relatif sprite): (%d, %d)"
          % (sum(x for x, y in bottom) // len(bottom), ymax))

# Simpan render besar untuk dilihat
img = Image.new("RGB", (w, h))
for r in range(h):
    for x in range(w):
        img.putpixel((x, r), CGA[grid[r][x]])
img.resize((w * 12, h * 12), Image.NEAREST).save(D + "\\pulley_zoom.png")
print("\n-> pulley_zoom.png")
