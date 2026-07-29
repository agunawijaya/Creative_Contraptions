import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
for lo,hi in [(0x1af0,0x1b60),(0x1cd0,0x1d40)]:
    print("=== %04x-%04x ==="%(lo,hi))
    for insn in md.disasm(b[lb+lo:lb+hi], lo):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
