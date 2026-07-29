import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
for insn in md.disasm(b[lb+0x5e3b:lb+0x5e3b+0x70], 0x5e3b):
    print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
    if insn.mnemonic in ("ret","retf"): break
