"""Hasilkan file PNG scaled yang bisa dibuka & diperiksa sendiri.

Adegan disusun dari sprite ASLI game (katrol MECHS, ember GRAPH) di 320x200,
dengan tali yang menyambung ke titik pixel yang diketahui persis. Lalu diskala
beberapa cara dan diverifikasi secara numerik.
"""
import struct
import os
from PIL import Image, ImageDraw

D = r"C:\Projects\Creative_Contraptions\work"
OUT = D + r"\scaled_samples"
os.makedirs(OUT, exist_ok=True)
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


def sprite_from(fname, rid_major, wbytes_interleave=False):
    b = open(D + "\\" + fname, "rb").read()
    first = struct.unpack_from("<I", b, 8)[0]
    n = first // 12
    for i in range(n):
        a, bb, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, i * 12)
        if a == rid_major and w and h:
            dec = decode_e4(b[off:off + ln])
            img = Image.new("RGB", (w, h))
            px = img.load()
            wb = w // 4
            for r in range(h):
                for cb in range(wb):
                    if r * wb + cb >= len(dec):
                        break
                    byte = dec[r * wb + cb]
                    for p in range(4):
                        px[cb * 4 + p, r] = CGA[(byte >> (6 - 2 * p)) & 3]
            return img, (w, h)
    raise ValueError("tak ketemu")


# --- Susun adegan 320x200 dari sprite asli ---
pulley, (pw, ph) = sprite_from("MECHS", 110)      # katrol asli 32x24
bucket, (bw, bh) = sprite_from("GRAPH", 9)        # objek dari GRAPH (ember/mesin)

scene = Image.new("RGB", (320, 200), CGA[1])
PULLEY_AT = (120, 30)
scene.paste(pulley, PULLEY_AT)

# Titik di mana tali menyentuh katrol (kita tentukan & catat)
JUNCTION_TOP = (PULLEY_AT[0] + pw // 2, PULLEY_AT[1] + ph - 2)
BUCKET_AT = (JUNCTION_TOP[0] - bw // 2, 150)
scene.paste(bucket, BUCKET_AT)
JUNCTION_BOT = (JUNCTION_TOP[0], BUCKET_AT[1] + 2)

dr = ImageDraw.Draw(scene)
dr.line([JUNCTION_TOP, JUNCTION_BOT], fill=CGA[3], width=1)   # tali putih vertikal

# tandai kedua sambungan dg 1 pixel magenta agar bisa dilacak numerik
scene.putpixel(JUNCTION_TOP, CGA[2])
scene.putpixel(JUNCTION_BOT, CGA[2])

scene.save(OUT + r"\sample_320x200_1x_NATIVE.png")


def verify(img, scale, label):
    """Cek: penanda magenta ada tepat di koordinat prediksi?"""
    ok = True
    for (jx, jy) in (JUNCTION_TOP, JUNCTION_BOT):
        px, py = int(jx * scale), int(jy * scale)
        # cari magenta di blok scale x scale mulai (px,py)
        found = False
        for dy in range(max(1, int(scale))):
            for dx in range(max(1, int(scale))):
                if 0 <= px + dx < img.width and 0 <= py + dy < img.height:
                    if img.getpixel((px + dx, py + dy)) == CGA[2]:
                        found = True
        if not found:
            ok = False
    print("  %-40s sambungan presisi: %s" % (label, "YA" if ok else "TIDAK"))
    return ok


print("Junction ASLI (320x200): atas=%s bawah=%s\n" % (JUNCTION_TOP, JUNCTION_BOT))
print("Verifikasi tiap file:")

# Integer nearest di beberapa skala -> file terpisah
for s in (2, 3, 5):
    im = scene.resize((320 * s, 200 * s), Image.NEAREST)
    fn = OUT + r"\sample_%dx%d_%dx_NEAREST.png" % (320 * s, 200 * s, s)
    im.save(fn)
    verify(im, s, "%dx nearest (%dx%d)" % (s, 320 * s, 200 * s))

# Koreksi aspek 4:3 integer (6x lebar, tinggi disesuaikan ke 4:3)
aspect = scene.resize((320 * 6, 240 * 6), Image.NEAREST)   # 1920x1440
aspect.save(OUT + r"\sample_1920x1440_6x_ASPEK43.png")
# verifikasi butuh skala Y berbeda; cek manual
okA = True
for (jx, jy) in (JUNCTION_TOP, JUNCTION_BOT):
    px, py = jx * 6, int(jy * (240 * 6) / 200)
    found = any(aspect.getpixel((px + dx, py + dy)) == CGA[2]
                for dy in range(8) for dx in range(6)
                if px + dx < aspect.width and py + dy < aspect.height)
    okA = okA and found
print("  %-40s sambungan presisi: %s" % ("6x aspek 4:3 (1920x1440)", "YA" if okA else "TIDAK"))

# KONTRAS: bilinear (yang MERUSAK) -> file terpisah biar kelihatan bedanya
bad = scene.resize((320 * 5, 200 * 5), Image.BILINEAR)
bad.save(OUT + r"\sample_1600x1000_5x_BILINEAR_BURUK.png")
print("  %-40s (sengaja buruk, utk perbandingan)" % "5x BILINEAR")

print("\nSemua file di: %s" % OUT)
for f in sorted(os.listdir(OUT)):
    sz = os.path.getsize(os.path.join(OUT, f))
    print("  %-42s %6d B" % (f, sz))
