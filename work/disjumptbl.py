import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# tabel {opcode word, handler word} 4-byte, dari 0x23d4 mundur. Baca 0x23d4..0x2420
print("JUMP TABLE @0x23d4:")
for a in range(0x23d4, 0x2420, 4):
    opc, hnd = struct.unpack_from("<HH", b, lb+a)
    print("  tbl@%04x  op=0x%02x -> handler 0x%04x"%(a, opc, hnd))
# handler op0x0F, op0x0E, op0x09
for h in (0x0f,0x0e,0x09):
    for a in range(0x23d4,0x2420,4):
        opc,hnd = struct.unpack_from("<HH", b, lb+a)
        if opc==h:
            print("=== op0x%02x handler @ 0x%04x ==="%(h,hnd))
            for insn in md.disasm(b[lb+hnd:lb+hnd+0x40], hnd):
                print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
