"""Disassemble penuh tiap handler opcode untuk membaca grammar operan."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
lb = struct.unpack_from("<H", b, 8)[0] * 16

H = {0x00: 0x1F11, 0x01: 0x1F49, 0x02: 0x1F8D, 0x03: 0x1FAC, 0x05: 0x2305,
     0x06: 0x2315, 0x07: 0x1F70, 0x08: 0x1F3B, 0x09: 0x1F79, 0x0A: 0x1F32,
     0x0C: 0x21E1, 0x0D: 0x2321, 0x0E: 0x2334, 0x0F: 0x233C, 0x11: 0x1E85}
md = Cs(CS_ARCH_X86, CS_MODE_16)

for op in sorted(H):
    s = H[op]
    code = b[lb + s: lb + s + 70]
    print("\n===== OP 0x%02X @0x%04X =====" % (op, s))
    cnt = 0
    for insn in md.disasm(code, s):
        print("  %04x  %s %s" % (insn.address, insn.mnemonic, insn.op_str))
        cnt += 1
        if insn.mnemonic in ("ret", "retf"):
            break
        if cnt >= 14:
            break
