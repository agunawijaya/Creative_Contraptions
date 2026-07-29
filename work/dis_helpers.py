import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
for name,a in [("69d7",0x69d7),("7040",0x7040)]:
    print("=== %s ==="%name)
    for insn in md.disasm(b[lb+a:lb+a+0x50], a):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
        if insn.mnemonic in ("ret","retf"): break
