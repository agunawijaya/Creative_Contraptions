import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
tbl = {}
for a in range(0x23d4,0x241c,4):
    opc,hnd = struct.unpack_from("<HH", b, lb+a)
    tbl[opc]=hnd
# batas fungsi: sampai jmp 0x1cd2 / ret / jmp ke handler lain
for op in sorted(tbl):
    hnd=tbl[op]
    print("\n=== op 0x%02x @ 0x%04x ==="%(op,hnd))
    n=0
    for insn in md.disasm(b[lb+hnd:lb+hnd+0x60], hnd):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
        n+=1
        s="%s %s"%(insn.mnemonic,insn.op_str)
        if insn.mnemonic=="ret" or ("jmp" in insn.mnemonic and "0x1cd2" in s):
            break
        if n>28: break
