"""BUKTI: apakah scaling merusak sambungan tali-katrol?

Metode: ambil sprite katrol ASLI dari MECHS, sambungkan tali ke titik pixel
tertentu, komposit di 320x200, lalu skala dengan berbagai cara. Ukur secara
numerik apakah titik sambungan tetap presisi.
"""
import struct
from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
CGA = [(0, 0, 0), (85, 255, 255), (255, 85, 255), (255, 255, 255)]


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1])
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


def sprite(dec, w, h):
    img = Image.new("RGB", (w, h), (0, 0, 0))
    px = img.load()
    wb = w // 4
    for r in range(h):
        for cb in range(wb):
            if r * wb + cb >= len(dec):
                break
            b = dec[r * wb + cb]
            for p in range(4):
                px[cb * 4 + p, r] = CGA[(b >> (6 - 2 * p)) & 3]
    return img


# Ambil sprite katrol asli (MECHS id 110)
b = open(D + "\\MECHS", "rb").read()
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(31)]
pulley_rec = next(r for r in recs if r[0] == 110)
a, bb, h, w, f, ln, off = pulley_rec
pulley = sprite(decode_e4(b[off:off + ln]), w, h)  # 32x24

# --- KOMPOSISI di 320x200 (meniru apa yang dilakukan game) ---
# Titik sambungan tali ke katrol: satu pixel yang kita tentukan persis.
PULLEY_POS = (140, 40)          # posisi sprite katrol di layar
JUNCTION = (PULLEY_POS[0] + 16, PULLEY_POS[1] + 20)  # tempat tali menyentuh katrol
ANCHOR = (150, 150)             # ujung bawah tali (mis. beban)

scene = Image.new("RGB", (320, 200), CGA[1])
scene.paste(pulley, PULLEY_POS)
dr = ImageDraw.Draw(scene)
dr.line([JUNCTION, ANCHOR], fill=CGA[3], width=1)   # tali putih
scene.putpixel(JUNCTION, CGA[2])                     # tandai junction (magenta)


def junction_color_at(img, x, y):
    return img.getpixel((x, y))


print("=== BUKTI PRESISI SAMBUNGAN ===")
print("Junction di framebuffer 320x200 = %s\n" % (JUNCTION,))

variants = []

# 1. Integer nearest 5x  -> junction HARUS di 5x koordinat
s5 = scene.resize((320 * 5, 200 * 5), Image.NEAREST)
jx, jy = JUNCTION[0] * 5, JUNCTION[1] * 5
c = junction_color_at(s5, jx + 2, jy + 2)
print("[1] INTEGER NEAREST 5x")
print("    prediksi junction: (%d,%d) -> aktual warna magenta di sana? %s"
      % (jx, jy, "YA (utuh)" if c == CGA[2] else "warna=%s" % (c,)))
variants.append(("INTEGER 5x NEAREST\nsambungan UTUH", s5, (jx, jy)))

# 2. Non-integer 5.5x  -> pixel tidak rata, sambungan bergeser tak seragam
sf = scene.resize((int(320 * 5.5), int(200 * 5.5)), Image.NEAREST)
print("\n[2] NON-INTEGER 5.5x NEAREST")
print("    320*5.5=%d, 200*5.5=%d  -> baris pixel TIDAK rata (ada yg digandakan 5x, ada 6x)"
      % (int(320 * 5.5), int(200 * 5.5)))
variants.append(("NON-INTEGER 5.5x\nbaris tidak rata", sf, (int(JUNCTION[0] * 5.5), int(JUNCTION[1] * 5.5))))

# 3. Bilinear 5x -> junction jadi kabur, tepi tali melebar
sb = scene.resize((320 * 5, 200 * 5), Image.BILINEAR)
print("\n[3] BILINEAR 5x")
print("    tali & katrol jadi kabur, tepi sambungan melebar (bukan hilang, tapi tidak tajam)")
variants.append(("BILINEAR 5x\nkabur di sambungan", sb, (jx, jy)))

# --- Zoom ke area sambungan untuk tiap varian ---
CROP = 34  # pixel asli di sekitar junction
panels = []
for label, img, (cx, cy) in variants:
    scale = img.width / 320.0
    half = int(CROP * scale / 2)
    box = (max(0, cx - half), max(0, cy - half), cx + half, cy + half)
    z = img.crop(box).resize((300, 300), Image.NEAREST)
    panels.append((label, z))

sheet = Image.new("RGB", (len(panels) * 316, 360), (25, 25, 25))
drs = ImageDraw.Draw(sheet)
for i, (label, z) in enumerate(panels):
    x = i * 316 + 8
    sheet.paste(z, (x, 44))
    for j, line in enumerate(label.split("\n")):
        drs.text((x, 6 + j * 15), line, fill=(255, 255, 0) if j == 0 else (170, 170, 170))
sheet.save(D + "\\align_proof.png")
print("\n-> align_proof.png (zoom ke titik sambungan)")

# Simpan juga scene asli diperbesar utuh
scene.resize((320 * 3, 200 * 3), Image.NEAREST).save(D + "\\align_scene.png")
print("-> align_scene.png (adegan penuh)")
