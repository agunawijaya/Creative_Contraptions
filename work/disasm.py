"""Petakan MZ hasil unpack + disassemble entry point (16-bit real mode)."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()

# --- Header MZ ---
lastpage = struct.unpack_from("<H", b, 2)[0]
pages = struct.unpack_from("<H", b, 4)[0]
nreloc = struct.unpack_from("<H", b, 6)[0]
hdrpar = struct.unpack_from("<H", b, 8)[0]
ss = struct.unpack_from("<H", b, 14)[0]
sp = struct.unpack_from("<H", b, 16)[0]
ip = struct.unpack_from("<H", b, 20)[0]
cs = struct.unpack_from("<H", b, 22)[0]
reltbl = struct.unpack_from("<H", b, 24)[0]

load_base = hdrpar * 16          # offset file tempat load module mulai
entry_off = load_base + cs * 16 + ip
print("=== STRUKTUR MZ (unpacked) ===")
print("file size      : %d" % len(b))
print("header paras   : %d  -> load module @ file 0x%X" % (hdrpar, load_base))
print("entry CS:IP    : %04X:%04X  -> file offset 0x%X" % (cs, ip, entry_off))
print("stack SS:SP    : %04X:%04X" % (ss, sp))
print("relokasi       : %d @ 0x%X" % (nreloc, reltbl))

# --- Tabel relokasi ---
print("\n=== RELOKASI ===")
relocs = []
for i in range(nreloc):
    ro, rs = struct.unpack_from("<HH", b, reltbl + i * 4)
    fileoff = load_base + rs * 16 + ro
    seg_at = struct.unpack_from("<H", b, fileoff)[0] if fileoff + 2 <= len(b) else None
    relocs.append((rs, ro, fileoff, seg_at))
    print("  seg:off %04X:%04X -> file 0x%X (nilai seg tersimpan: %04X)"
          % (rs, ro, fileoff, seg_at if seg_at is not None else 0))

# --- Disassemble entry point ---
md = Cs(CS_ARCH_X86, CS_MODE_16)
print("\n=== DISASSEMBLY dari entry point (file 0x%X) ===" % entry_off)
code = b[entry_off:entry_off + 400]
addr = ip
cnt = 0
for insn in md.disasm(code, addr):
    print("  %04X:  %-22s %s %s" % (insn.address,
          " ".join("%02x" % x for x in insn.bytes),
          insn.mnemonic, insn.op_str))
    cnt += 1
    if cnt >= 60:
        break
