"""Disassemble FUN_1000_18db untuk temukan offset launch bola & titik keluar awal."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
lb = struct.unpack_from("<H", b, 8)[0] * 16
md = Cs(CS_ARCH_X86, CS_MODE_16)
code = b[lb + 0x18db: lb + 0x18db + 0x180]   # bagian awal 18db
for insn in md.disasm(code, 0x18db):
    m = "%04x  %s %s" % (insn.address, insn.mnemonic, insn.op_str)
    # tandai call & ret & referensi menarik
    print(m)
    if insn.address > 0x19d0:
        break
