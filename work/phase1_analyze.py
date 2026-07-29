"""Analisa presisi header PKLITE keempat EXE -> tentukan versi & mode kompresi."""
import struct

D = r"C:\Projects\Creative_Contraptions\work"


def mz(b):
    return dict(
        lastpage=struct.unpack_from("<H", b, 2)[0],
        pages=struct.unpack_from("<H", b, 4)[0],
        nreloc=struct.unpack_from("<H", b, 6)[0],
        hdrpar=struct.unpack_from("<H", b, 8)[0],
        minalloc=struct.unpack_from("<H", b, 10)[0],
        maxalloc=struct.unpack_from("<H", b, 12)[0],
        ss=struct.unpack_from("<H", b, 14)[0],
        sp=struct.unpack_from("<H", b, 16)[0],
        ip=struct.unpack_from("<H", b, 20)[0],
        cs=struct.unpack_from("<H", b, 22)[0],
        reltbl=struct.unpack_from("<H", b, 24)[0],
        ovno=struct.unpack_from("<H", b, 26)[0],
    )


for name in ["CONTRAP.EXE", "BANTAM.EXE", "BANTLOGO.EXE", "LGLOGO.EXE"]:
    b = open(D + "\\" + name, "rb").read()
    h = mz(b)
    imgsize = (h["pages"] - 1) * 512 + (h["lastpage"] or 512)
    # PKLITE version word di offset 0x1C
    ver = struct.unpack_from("<H", b, 0x1C)[0]
    sig = b[0x1E:0x24]
    major = (ver >> 8) & 0x0F
    minor = ver & 0xFF
    extra = bool(ver & 0x1000)      # extra/large compression
    large = bool(ver & 0x2000)
    print("=" * 58)
    print("%s  (%d byte)" % (name, len(b)))
    print("  PKLITE version word @0x1C = 0x%04X  -> v%d.%02x" % (ver, major, minor))
    print("  sig @0x1E = %r" % sig)
    print("  flag extra-compression (0x1000) = %s" % extra)
    print("  flag large-model      (0x2000) = %s" % large)
    print("  header paras = %d -> stub decompressor mulai di 0x%X"
          % (h["hdrpar"], h["hdrpar"] * 16))
    print("  entry CS:IP = %04X:%04X   stack SS:SP = %04X:%04X"
          % (h["cs"], h["ip"], h["ss"], h["sp"]))
    print("  relokasi = %d (asli pasti jauh lebih banyak)" % h["nreloc"])
    print("  image MZ = %d byte; file = %d; SELISIH (overlay?) = %d"
          % (imgsize, len(b), len(b) - imgsize))
    print("  minalloc = %d para (%.1f KB) -> perkiraan ukuran setelah unpack"
          % (h["minalloc"], h["minalloc"] * 16 / 1024))
