"""Disassemble sub-fungsi gambar 0x2714 & 0x278e -> berapa byte skrip dikonsumsi/item."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
lb = struct.unpack_from("<H", b, 8)[0] * 16
md = Cs(CS_ARCH_X86, CS_MODE_16)

for name, addr, size in [("draw 0x2714", 0x2714, 0x7a), ("draw 0x278e", 0x278e, 0x80)]:
    print("\n===== %s =====" % name)
    code = b[lb + addr: lb + addr + size]
    for insn in md.disasm(code, addr):
        print("  %04x  %s %s" % (insn.address, insn.mnemonic, insn.op_str))
        if insn.mnemonic in ("ret", "retf"):
            break
