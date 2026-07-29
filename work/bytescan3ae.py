import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# pola instruksi yg menyentuh word [0x3ae]:
#  A3 AE 03        mov [0x3ae], ax
#  C7 06 AE 03     mov word [0x3ae], imm16
#  89 xx AE 03 (modrm disp16 =06)   mov [0x3ae], reg
#  8B xx AE 03     mov reg, [0x3ae]
#  FF 06 AE 03     inc word [0x3ae]
pats = {b"\xA3\xAE\x03":"mov[3ae],ax", b"\xC7\x06\xAE\x03":"movw[3ae],imm",
        b"\x89\x1E\xAE\x03":"mov[3ae],bx", b"\x89\x36\xAE\x03":"mov[3ae],si",
        b"\x89\x06\xAE\x03":"mov[3ae],ax", b"\x89\x0E\xAE\x03":"mov[3ae],cx",
        b"\x89\x16\xAE\x03":"mov[3ae],dx", b"\xFF\x06\xAE\x03":"inc[3ae]"}
for pat,nm in pats.items():
    i=lb
    while True:
        j=b.find(pat,i,lb+0xa000)
        if j<0: break
        off=j-lb
        # disasm sekitar
        ins=next(md.disasm(b[j:j+8],off))
        print("  off %04x  %-16s  %s %s"%(off,nm,ins.mnemonic,ins.op_str))
        i=j+1
