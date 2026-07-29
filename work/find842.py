"""Cari instruksi tulis ke 0x842 di FUN_1000_18db (slot loop)."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
lb = struct.unpack_from("<H", b, 8)[0] * 16
md = Cs(CS_ARCH_X86, CS_MODE_16)
code = b[lb + 0x18db: lb + 0x24bb]   # seluruh 18db
for insn in md.disasm(code, 0x18db):
    s = "%s %s" % (insn.mnemonic, insn.op_str)
    if "0x842" in s and insn.mnemonic == "mov" and ("0xffff" in s or ", 1" in s or "0x1" == insn.op_str.split(",")[-1].strip()):
        print("  %04x  %s" % (insn.address, s))
