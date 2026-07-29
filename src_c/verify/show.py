"""Tampilkan satu fungsi: pseudo-C Ghidra + disassembly asli, berdampingan.

    python src_c/verify/show.py 3322          # pakai ukuran dari functions.txt
    python src_c/verify/show.py 3322 --asm    # disassembly saja
    python src_c/verify/show.py 3322 --c      # pseudo-C saja
"""
import os
import re
import sys
import struct

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXE = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
DEC = os.path.join(ROOT, "work", "ghidra_out", "decompiled.c")
FNS = os.path.join(ROOT, "work", "ghidra_out", "functions.txt")


def size_of(addr):
    for ln in open(FNS):
        m = re.match(r"(\w+):(\w+)\s+(\S+)\s+size=(\d+)", ln.strip())
        if m and int(m.group(2), 16) == addr:
            return int(m.group(4))
    return None


def show_c(addr):
    s = open(DEC, encoding="utf-8", errors="replace").read()
    tag = "==== FUN_1000_%04x" % addr
    i = s.find(tag)
    if i < 0:
        print("(tidak ada di decompiled.c)")
        return
    j = s.find("==== ", i + 10)
    print(s[i - 5: j if j > 0 else i + 3000].rstrip())


def show_asm(addr, size):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    b = open(EXE, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    md = Cs(CS_ARCH_X86, CS_MODE_16)
    for ins in md.disasm(b[lb + addr: lb + addr + size], addr):
        print("  %04x  %-7s %s" % (ins.address, ins.mnemonic, ins.op_str))


if __name__ == "__main__":
    addr = int(sys.argv[1], 16)
    size = size_of(addr)
    only = [a for a in sys.argv[2:] if a.startswith("--")]
    print("=== FUN_1000_%04x  (%s byte) ===" % (addr, size))
    if "--asm" not in only:
        show_c(addr)
        print()
    if "--c" not in only and size:
        show_asm(addr, size)
