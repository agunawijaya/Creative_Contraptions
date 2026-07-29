"""Ekstrak tabel dispatch VM animasi @DS:0x23d4 (opcode, handler) x18."""
import struct

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
hdrpar = struct.unpack_from("<H", b, 8)[0]
load_base = hdrpar * 16
dgroup = load_base + 0x907 * 16     # basis DGROUP
tbl = dgroup + 0x23d4               # tabel opcode

# baca fungsi (utk memetakan handler addr -> nama)
funcs = {}
for line in open(r"C:\Projects\Creative_Contraptions\work\ghidra_out\functions.txt"):
    line = line.strip()
    if ":" in line and "FUN_" in line or "entry" in line:
        parts = line.split()
        if len(parts) >= 3 and ":" in parts[1]:
            seg, offs = parts[1].split(":")
            try:
                funcs[int(offs, 16)] = parts[2]
            except ValueError:
                pass

print("Tabel dispatch VM animasi @ DS:0x23d4 (file 0x%X):\n" % tbl)
print(" idx  opcode  handler   fungsi")
for e in range(0, 0x48, 4):
    op = struct.unpack_from("<H", b, tbl + e)[0]
    hd = struct.unpack_from("<H", b, tbl + e + 2)[0]
    name = funcs.get(hd, "?")
    ch = chr(op) if 32 <= op < 127 else "."
    print("  %2d   0x%04x('%s')  0x%04x   %s" % (e // 4, op, ch, hd, name))
