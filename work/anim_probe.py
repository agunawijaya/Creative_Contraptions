"""Periksa isi file ANIMATE: apakah blob = stream opcode VM (0x00-0x11, 0xff)?"""
import struct
from collections import Counter

D = r"C:\Projects\Creative_Contraptions\work"
OPS = set(range(0x00, 0x12)) | {0xff}


def decode_e4(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0xE4 and i + 2 < n:
            out.extend(bytes([data[i + 2]]) * data[i + 1]); i += 3
        else:
            out.append(data[i]); i += 1
    return bytes(out)


b = open(D + "\\ANIMATE", "rb").read()
first = struct.unpack_from("<I", b, 8)[0]
n = first // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]
print("ANIMATE: %d record\n" % n)

# Distribusi byte pertama (opcode awal) & cek raw vs decoded
allbytes_raw = Counter()
for a, bb, h, w, f, ln, off in recs:
    if ln:
        for x in b[off:off + ln]:
            allbytes_raw[x] += 1
inset = sum(c for x, c in allbytes_raw.items() if x in OPS)
tot = sum(allbytes_raw.values())
print("Byte RAW dalam set opcode: %d/%d (%.0f%%)" % (inset, tot, 100 * inset / tot))
print("Byte RAW paling sering: %s" % allbytes_raw.most_common(12))

# tampilkan beberapa record mentah
print("\n=== Contoh record (id, ukuran, byte mentah) ===")
for a, bb, h, w, f, ln, off in recs[:6]:
    raw = b[off:off + ln]
    print("id=%d.%d w=%d h=%d len=%d:" % (a, bb, w, h, ln))
    print("   " + " ".join("%02x" % x for x in raw[:32]))
