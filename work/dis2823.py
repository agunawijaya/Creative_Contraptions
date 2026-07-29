import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
print("=== FUN_2823 ===")
for insn in md.disasm(b[lb+0x2823:lb+0x29b0], 0x2823):
    print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
    if insn.mnemonic=="ret": break
