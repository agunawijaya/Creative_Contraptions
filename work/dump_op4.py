import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
lb = struct.unpack_from("<H", b, 8)[0] * 16
md = Cs(CS_ARCH_X86, CS_MODE_16)
code = b[lb + 0x2280: lb + 0x2305]
for insn in md.disasm(code, 0x2280):
    print("  %04x  %s %s" % (insn.address, insn.mnemonic, insn.op_str))
