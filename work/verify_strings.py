"""Verifikasi string kunci dalam konteks hex mentah."""
f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()


def dump(off, length, title):
    print("\n=== %s @ 0x%06X ===" % (title, off))
    for i in range(off, off + length, 16):
        chunk = b[i:i + 16]
        hx = " ".join("%02x" % x for x in chunk)
        asc = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        print("%06X  %-47s |%s|" % (i, hx, asc))


dump(0x0001F8, 32, "String compiler")
dump(0x009AB0, 48, "Kredit programmer")
dump(0x009B40, 80, "Nama contraption")
dump(0x00B080, 48, "String 'E4s in animate' (konfirmasi RLE)")
