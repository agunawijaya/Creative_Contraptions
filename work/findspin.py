import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# cmp word ptr [0x2e4], 0  = 83 3E E4 02 00 ; disasm cek jg ke diri sendiri
pat = b"\x83\x3E\xE4\x02\x00"
i = lb
hits=[]
while True:
    j = b.find(pat, i, lb+0xa000)
    if j<0: break
    off = j-lb
    ins = list(md.disasm(b[j:j+12], off))
    nxt = ins[1] if len(ins)>1 else None
    s2 = ("%s %s"%(nxt.mnemonic,nxt.op_str)) if nxt else "?"
    # spin jika jg/jge kembali ke off (cmp addr)
    isspin = nxt and nxt.mnemonic in ("jg","jge","jns","ja") and hex(off) in nxt.op_str
    print("  off 0x%04x  cmp[0x2e4],0 ; %s   %s"%(off, s2, "<-- SPIN" if isspin else ""))
    if isspin: hits.append(off)
    i = j+1
print("SPINS:", [hex(h) for h in hits])
