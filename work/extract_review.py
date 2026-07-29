import struct, json
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE", "rb").read()
# region teks review mekanisme ~0x9F36..0xA6D0; string null-terminated
def strings_in(lo, hi):
    out = []; cur = bytearray(); start = lo
    i = lo
    while i < hi:
        ch = b[i]
        if 32 <= ch < 127:
            if not cur: start = i
            cur.append(ch)
        else:
            if len(cur) >= 2:
                out.append((start, cur.decode("latin1")))
            cur = bytearray()
        i += 1
    return out
for off, s in strings_in(0x9F30, 0xA6E0):
    print("0x%04X  %r" % (off, s))
