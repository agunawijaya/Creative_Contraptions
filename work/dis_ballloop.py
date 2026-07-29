import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE","rb").read()
lb = struct.unpack_from("<H", b, 8)[0]*16
md = Cs(CS_ARCH_X86, CS_MODE_16)
# cari call ke 2714 dan 26ae di dalam 18db (0x18db..0x2495)
targets = {0x2714:"2714_step",0x26ae:"26ae_draw",0x2692:"2692_delay",0x1791:"1791_input"}
lo,hi=0x18db,0x24c0
addrs=[]
for insn in md.disasm(b[lb+lo:lb+hi], lo):
    if insn.mnemonic=="call":
        try: t=int(insn.op_str,16)
        except: t=None
        if t in targets:
            addrs.append((insn.address,targets[t]))
print("calls:",addrs)
# print konteks tiap call
for a,nm in addrs:
    print("=== call %s @ %04x ==="%(nm,a))
    for insn in md.disasm(b[lb+a-0x18:lb+a+0x1a], a-0x18):
        print("  %04x  %s %s"%(insn.address,insn.mnemonic,insn.op_str))
