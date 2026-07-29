import struct
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
# tabel {key word, handler word} 4-byte, dari 0x3edc offset 0..0x18
print("3c4f key table @0x3edc:")
for a in range(0x3edc, 0x3edc + 0x1c, 4):
    key, hnd = struct.unpack_from("<HH", b, lb + a)
    print("  @%04x key=0x%04x -> handler 0x%04x" % (a, key, hnd))
