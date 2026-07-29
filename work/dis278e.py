import struct, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
a0 = int(sys.argv[1],16) if len(sys.argv)>1 else 0x278e
a1 = int(sys.argv[2],16) if len(sys.argv)>2 else 0x2823
md = Cs(CS_ARCH_X86, CS_MODE_16)
for insn in md.disasm(b[lb+a0:lb+a1], a0):
    print("  %04x  %-8s %s"%(insn.address,insn.mnemonic,insn.op_str))
