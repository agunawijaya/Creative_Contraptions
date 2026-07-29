import struct
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
raw = b[lb+0x235a:lb+0x236a]
print("bytes 0x235a:", raw.hex())
# entri {key word, handler word} di 0x235a, 0x235e, 0x2362, 0x2366
for a in (0x235a,0x235e,0x2362,0x2366):
    key,hnd = struct.unpack_from("<HH", b, lb+a)
    print("  @%04x key=0x%04x -> handler 0x%04x"%(a,key,hnd))
