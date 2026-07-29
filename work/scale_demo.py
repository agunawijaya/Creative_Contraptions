"""Demo: apa yang terjadi pada pixel CGA dengan berbagai strategi scaling."""
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


def render_cga(dec):
    img = Image.new("RGB", (320, 200), (0, 0, 0))
    px = img.load()
    for row in range(200):
        base = (0x2000 if row & 1 else 0) + (row >> 1) * 80
        if base + 80 > len(dec):
            continue
        for cb in range(80):
            b = dec[base + cb]
            for p in range(4):
                px[cb * 4 + p, row] = CGA[(b >> (6 - 2 * p)) & 3]
    return img


def scale2x(img):
    """Upscaler 'pintar' klasik: menebak diagonal dari tetangga."""
    w, h = img.size
    s = img.load()
    out = Image.new("RGB", (w * 2, h * 2))
    o = out.load()

    def g(x, y):
        return s[min(max(x, 0), w - 1), min(max(y, 0), h - 1)]

    for y in range(h):
        for x in range(w):
            E = g(x, y)
            B, Dd, F, H = g(x, y - 1), g(x - 1, y), g(x + 1, y), g(x, y + 1)
            E0 = Dd if (Dd == B and B != F and Dd != H) else E
            E1 = F if (B == F and B != Dd and F != H) else E
            E2 = Dd if (Dd == H and Dd != B and H != F) else E
            E3 = F if (H == F and Dd != H and B != F) else E
            o[x * 2, y * 2] = E0
            o[x * 2 + 1, y * 2] = E1
            o[x * 2, y * 2 + 1] = E2
            o[x * 2 + 1, y * 2 + 1] = E3
    return out


def scanlines(img, strength=0.45):
    out = img.copy()
    px = out.load()
    for y in range(0, out.height, 2):
        for x in range(out.width):
            r, g_, b = px[x, y]
            px[x, y] = (int(r * (1 - strength)), int(g_ * (1 - strength)), int(b * (1 - strength)))
    return out


raw = open(D + "\\LG.CMP", "rb").read()
full = render_cga(decode_e4(raw))

# Ambil potongan berdetail (teks logo) supaya beda filter terlihat jelas
crop = full.crop((48, 18, 128, 58))   # 80x40 px asli
S = 8
W, H = 80 * S, 40 * S

panels = []
panels.append(("1x ASLI (diperbesar nearest)\nacuan kebenaran",
               crop.resize((W, H), Image.NEAREST)))
panels.append(("NEAREST %dx\nTAJAM - rekomendasi" % S,
               crop.resize((W, H), Image.NEAREST)))
panels.append(("BILINEAR %dx\nBLUR - inilah yang Windows lakukan" % S,
               crop.resize((W, H), Image.BILINEAR)))
s2 = scale2x(scale2x(crop))           # 4x 'pintar'
panels.append(("SCALE2X (2x2 pass) lalu nearest\nMULUS tapi MENGARANG detail",
               s2.resize((W, H), Image.NEAREST)))
panels.append(("NEAREST %dx + SCANLINE\nnuansa CRT 1985" % S,
               scanlines(crop.resize((W, H), Image.NEAREST))))
ar = crop.resize((W, int(H * 1.2)), Image.NEAREST)
panels.append(("NEAREST + KOREKSI ASPEK 1:1.2\nseperti monitor CRT asli",
               ar))

maxh = max(p[1].height for p in panels)
cols = 3
rows = (len(panels) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 16), rows * (maxh + 46)), (25, 25, 25))
dr = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(panels):
    x = (i % cols) * (W + 16) + 8
    y = (i // cols) * (maxh + 46) + 34
    sheet.paste(im, (x, y))
    for j, line in enumerate(label.split("\n")):
        dr.text((x, y - 30 + j * 12), line, fill=(255, 255, 0) if j == 0 else (170, 170, 170))
sheet.save(D + "\\scale_demo.png")
print("-> scale_demo.png", sheet.size)

# Hitung: skala integer mana yang pas di layar modern
print("\n%-12s %-22s %-22s" % ("Layar", "320x200 murni", "aspek 4:3 (320x240)"))
for name, sw, sh in [("1080p", 1920, 1080), ("1440p", 2560, 1440), ("4K", 3840, 2160)]:
    n1 = min(sw // 320, sh // 200)
    n2 = min(sw // 320, sh // 240)
    print("%-12s %-22s %-22s" % (
        name,
        "%dx -> %dx%d" % (n1, 320 * n1, 200 * n1),
        "%dx -> %dx%d%s" % (n2, 320 * n2, 240 * n2, "  <- TINGGI PAS!" if 240 * n2 == sh else "")))
