"""Cari lokasi kunci di kode: video CGA (0xB800), INT 10h/21h, dan referensi
string aset -> temukan fungsi render (komposisi) & fungsi loader file."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
hdrpar = struct.unpack_from("<H", b, 8)[0]
load_base = hdrpar * 16          # 0x200
DGROUP_seg = 0x907
dgroup_file = load_base + DGROUP_seg * 16   # basis file utk data DS-relative

# Perkiraan batas segmen kode: dari load_base sampai awal DGROUP
code_start = load_base
code_end = dgroup_file
code = b[code_start:code_end]
print("Segmen kode: file 0x%X..0x%X  (%d byte)" % (code_start, code_end, len(code)))
print("DGROUP (data) mulai file 0x%X (DS=0x%04X)\n" % (dgroup_file, DGROUP_seg))

# 1. Cari immediate 0x00B8 dalam 'mov ax,0xB800' (b8 00 b8) atau push 0xB800 (68 00 b8)
print("=== Referensi video CGA 0xB800 (kode render) ===")
vids = []
i = 0
while i < len(code) - 2:
    if code[i] == 0xB8 and code[i+1] == 0x00 and code[i+2] == 0xB8:
        vids.append(i)
    i += 1
for off in vids[:20]:
    print("  file 0x%X (CS off 0x%X): mov ax,0xB800" % (code_start + off, off))
print("  total: %d" % len(vids))

# 2. INT 10h dan INT 21h
def find(pat):
    r = []
    i = 0
    while i < len(code) - len(pat):
        if code[i:i+len(pat)] == pat:
            r.append(i)
        i += 1
    return r

i10 = find(b"\xcd\x10")
i21 = find(b"\xcd\x21")
print("\n=== INT 10h (BIOS video): %d lokasi ===" % len(i10))
for o in i10[:12]:
    print("  file 0x%X (CS off 0x%X)" % (code_start + o, o))
print("\n=== INT 21h (DOS/file I/O): %d lokasi ===" % len(i21))
for o in i21[:12]:
    print("  file 0x%X (CS off 0x%X)" % (code_start + o, o))

# 3. Referensi string aset: hitung DS-offset tiap nama file, cari di kode
print("\n=== Referensi nama file aset di kode ===")
targets = {"graph": 0x9BD9, "mechs": 0x9BD3, "misc": 0x9BC2,
           "animate": 0x9BFF if False else None, "contrap": 0xB0AD}
# hitung DS offset dari file offset string yg kita tahu
known = {"graph": 0x9BD9, "mechs": 0x9BD3, "misc": 0x9BC2, "contrap": 0xB0AD}
for name, foff in known.items():
    ds_off = foff - dgroup_file
    pat_mov = bytes([0xB8]) + struct.pack("<H", ds_off)   # mov ax, ds_off
    pat_push = bytes([0x68]) + struct.pack("<H", ds_off)  # push ds_off
    hits = find(pat_mov) + find(pat_push)
    print("  '%s' DS off=0x%X -> %d referensi di kode: %s"
          % (name, ds_off, len(hits), ["0x%X" % (code_start+h) for h in hits[:6]]))
