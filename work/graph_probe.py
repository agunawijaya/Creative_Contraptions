"""Serang anomali GRAPH: 138 pelanggaran contiguity + ~60KB tak terjangkau."""
import struct

D = r"C:\Projects\Creative_Contraptions\work"
b = open(D + "\\GRAPH", "rb").read()
print("GRAPH size = %d" % len(b))

# 1. Cari record terminator (12 byte nol) di dalam tabel
first_off = struct.unpack_from("<I", b, 8)[0]
print("offset blob pertama = %d -> asumsi %d record" % (first_off, first_off // 12))

term = None
for i in range(0, first_off, 12):
    if b[i:i + 12] == b"\x00" * 12:
        term = i
        break
print("record terminator (12 byte nol) pertama di tabel: %s" % (term if term is not None else "TIDAK ADA"))

# 2. Baca semua record, abaikan contiguity
n = first_off // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]

# 3. Cek: apakah offset+len selalu dalam file?
oob = [r for r in recs if r[6] + r[5] > len(b)]
print("record yang menunjuk ke luar file: %d" % len(oob))

# 4. Coverage: byte mana saja yang tersentuh blob?
cov = bytearray(len(b))
for a, bb, h, w, f, ln, off in recs:
    for k in range(off, min(off + ln, len(b))):
        cov[k] = 1
covered = sum(cov[first_off:])
total = len(b) - first_off
print("area blob: %d byte; tercakup %d (%.1f%%), TIDAK tercakup %d"
      % (total, covered, 100 * covered / total, total - covered))

# 5. Apakah ada blob yang di-share (offset dipakai >1 record)?
from collections import Counter
offs = Counter(r[6] for r in recs)
dup = [(o, c) for o, c in offs.items() if c > 1]
print("offset yang dipakai lebih dari satu record: %d" % len(dup))

# 6. Lubang pertama yang tidak tercakup
holes = []
i = first_off
while i < len(b):
    if not cov[i]:
        j = i
        while j < len(b) and not cov[j]:
            j += 1
        holes.append((i, j - i))
        i = j
    else:
        i += 1
print("jumlah lubang: %d" % len(holes))
for o, l in sorted(holes, key=lambda x: -x[1])[:5]:
    print("   lubang @0x%06x len=%d" % (o, l))

# 7. Apakah lubang terbesar berisi tabel directory kedua?
if holes:
    big = max(holes, key=lambda x: x[1])
    o = big[0]
    print("\nHex di awal lubang terbesar @0x%06x:" % o)
    for r in range(3):
        chunk = b[o + r * 16: o + r * 16 + 16]
        print("   " + " ".join("%02x" % x for x in chunk))
    # tes: apakah terlihat seperti record 12-byte?
    a, bb, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", b, o)
    print("   ditafsir sbg record: id=%d.%d h=%d w=%d flags=%#x len=%d off=%#x" % (a, bb, h, w, f, ln, off))

# 8. Statistik ukuran vs kebutuhan raw
print("\nUji: apakah decoded length == (w/4)*h ?")


def decode_e4(data):
    out = bytearray()
    i, n2 = 0, len(data)
    while i < n2:
        if data[i] == 0xE4 and i + 2 < n2:
            out.extend(bytes([data[i + 2]]) * data[i + 1])
            i += 3
        else:
            out.append(data[i])
            i += 1
    return bytes(out)


ok = bad = 0
for a, bb, h, w, f, ln, off in recs[:80]:
    if w == 0 or ln == 0:
        continue
    d = decode_e4(b[off:off + ln])
    need = (w // 4) * h
    if len(d) == need:
        ok += 1
    else:
        bad += 1
        if bad <= 5:
            print("   MELESET id=%d.%d %dx%d flags=%#x decoded=%d butuh=%d" % (a, bb, w, h, f, len(d), need))
print("   dari 80 record pertama: cocok=%d meleset=%d" % (ok, bad))
