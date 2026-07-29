import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# VM dispatch head 0x1c66, dan tail/part-advance 0x2400-0x24c0, plus 0x2433/0x2450/0x2495
for lo,hi in [(0x1c60,0x1cd2),(0x2420,0x24c0)]:
    print("=== %04x-%04x ==="%(lo,hi))
    for insn in md.disasm(b[lb+lo:lb+hi], lo):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
