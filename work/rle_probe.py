"""Uji hipotesis: 0xE4 = escape RLE, diikuti <count> <value>."""
import collections

D = r"C:\Projects\Creative_Contraptions\work"


def decode_e4(data, start=0):
    """RLE: 0xE4 <count> <value> => value*count ; selain itu literal."""
    out = bytearray()
    i = start
    n = len(data)
    while i < n:
        b = data[i]
        if b == 0xE4:
            if i + 2 >= n:
                out.append(b)
                i += 1
                continue
            cnt = data[i + 1]
            val = data[i + 2]
            out.extend(bytes([val]) * cnt)
            i += 3
        else:
            out.append(b)
            i += 1
    return bytes(out)


for name, skip in [("BLOGO.CMP", 0), ("LG.CMP", 0), ("LG.CMP", 2)]:
    raw = open(D + "\\" + name, "rb").read()
    dec = decode_e4(raw, skip)
    print("=== %s (skip=%d) ===" % (name, skip))
    print("  compressed=%d -> decoded=%d  (ratio %.2fx)"
          % (len(raw), len(dec), len(dec) / len(raw)))
    # Kandidat geometri CGA: 2bpp -> width_px = bytes_per_row*4
    for w_bytes in (80, 40, 20):
        if len(dec) % w_bytes == 0:
            print("     %d bytes/row (%dpx lebar) -> %d baris  <-- pas"
                  % (w_bytes, w_bytes * 4, len(dec) // w_bytes))
    print("  byte histogram top: %s"
          % collections.Counter(dec).most_common(6))
    print()
