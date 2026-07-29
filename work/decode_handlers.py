"""Disassemble tiap handler opcode; hitung akses ke pointer skrip 0x3ae = jumlah operand."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()
load_base = struct.unpack_from("<H", b, 8)[0] * 16   # 0x200

handlers = {0x00: 0x1F11, 0x01: 0x1F49, 0x02: 0x1F8D, 0x03: 0x1FAC, 0x04: 0x2280,
            0x05: 0x2305, 0x06: 0x2315, 0x07: 0x1F70, 0x08: 0x1F3B, 0x09: 0x1F79,
            0x0A: 0x1F32, 0x0C: 0x21E1, 0x0D: 0x2321, 0x0E: 0x2334, 0x0F: 0x233C,
            0x10: 0x1D09, 0x11: 0x1E85, 0xFF: 0x23D1}

md = Cs(CS_ARCH_X86, CS_MODE_16)
md.detail = True

for op in sorted(handlers):
    start = handlers[op]
    code = b[load_base + start: load_base + start + 120]
    reads_3ae = 0
    calls = []
    lines = []
    for insn in md.disasm(code, start):
        lines.append("%04x %s %s" % (insn.address, insn.mnemonic, insn.op_str))
        if "0x3ae" in insn.op_str:
            reads_3ae += 1
        if insn.mnemonic == "call":
            calls.append(insn.op_str)
        if insn.mnemonic in ("ret", "retf"):
            break
    print("OP 0x%02X @0x%04X: akses 0x3ae=%d, call=%s"
          % (op, start, reads_3ae, calls[:3]))
    # tampilkan asm ringkas utk 2 opcode contoh
    if op in (0x08, 0x04):
        print("   " + "\n   ".join(lines[:16]))
