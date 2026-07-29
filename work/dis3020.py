import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
for name,lo,hi in [("3020",0x3020,0x3105),("2fde",0x2fde,0x300b)]:
    print("=== %s ==="%name)
    for insn in md.disasm(b[lb+lo:lb+hi], lo):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
        if insn.mnemonic=="ret": break
