import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# scan seluruh code segment untuk tulis ke 0x3ae / 0x3b0 (script ptr) & 0x3b2
# code kira2 0x100..0x7000
code = b[lb+0x100: lb+0x7000]
for insn in md.disasm(code, 0x100):
    s = "%s %s"%(insn.mnemonic,insn.op_str)
    if "0x3ae" in s or "0x3b0" in s or "0x3b2" in s:
        print("  %04x  %s"%(insn.address,s))
