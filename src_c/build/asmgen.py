"""Bangkitkan DRAFT sumber MASM dari disassembly biner asli.

Fungsi assembly tulisan tangan tidak bisa direkonstruksi lewat C, dan berbeda
dengan kode C, bytenya sudah diketahui PERSIS -- tidak ada kompiler yang harus
dilawan. Jadi rekonstruksinya MEKANIS: terjemahkan disassembly ke sintaks MASM,
rakit, bandingkan byte. Alat ini mengerjakan langkah pertama.

    python src_c/build/asmgen.py <nama> <addr> <size> [<addr> <size> ...]

Menulis src_c/asm/<nama>.asm. Keluarannya DRAFT -- selalu rakit dan bandingkan
dengan objcode.py; yang tidak bisa diterjemahkan ditandai komentar ";; ???".

Catatan sintaks MASM 1.27 yang sudah dibayar:
  - konstanta hex butuh akhiran H dan digit awal (0FFH, bukan FFH)
  - `word ptr` -> `WORD PTR`, `[bx + si]` -> `[BX+SI]`
  - lompatan/panggilan KE LUAR modul harus jadi EXTRN NEAR
  - berkas WAJIB CRLF (ditangani masm.ps1)
"""
import os
import re
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXE = os.path.join(ROOT, "work", "unpack", "CONTRAP_UNPACKED.EXE")
ASM = os.path.join(ROOT, "src_c", "asm")


def hexs(v):
    """Konstanta gaya MASM: akhiran H, digit awal wajib."""
    s = "%X" % v
    return (("0" + s) if s[0].isalpha() else s) + "H"


def conv(op, labels, lo, hi):
    """Terjemahkan operan capstone (Intel) ke sintaks MASM 1.x."""
    op = op.replace("word ptr", "WORD PTR").replace("byte ptr", "BYTE PTR")
    op = op.replace("dword ptr", "DWORD PTR")
    op = re.sub(r"\s*\+\s*", "+", op)
    op = re.sub(r"\s*-\s*", "-", op)

    def rep(m):
        v = int(m.group(0), 16)
        return labels.get(v, hexs(v)) if lo <= v < hi else hexs(v)
    op = re.sub(r"0x[0-9a-f]+", rep, op)
    op = op.upper()
    # MASM 1.27 menafsirkan kurung berisi KONSTANTA MURNI sebagai [BP+konst]
    # (mis. "[2128H]" -> 89 86 28 21). Alamat absolut harus diberi awalan
    # segmen eksplisit supaya keluar bentuk langsung (a3 28 21 / f7 36 ..).
    def abso(m):
        inner = m.group(1)
        if re.search(r"[A-Z]{2}", inner):     # ada nama register -> biarkan
            return m.group(0)
        return "DS:[" + inner + "]"
    op = re.sub(r"(?<![A-Z:])\[([^\]]+)\]", abso, op)
    return op


def gen(name, ranges):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    b = open(EXE, "rb").read()
    lb = struct.unpack_from("<H", b, 8)[0] * 16
    md = Cs(CS_ARCH_X86, CS_MODE_16)

    lo = min(a for a, _ in ranges)
    hi = max(a + n for a, n in ranges)

    insns = []
    for addr, size in ranges:
        for i in md.disasm(b[lb + addr: lb + addr + size], addr):
            insns.append(i)

    # kumpulkan target lompatan DI DALAM modul -> label; di luar -> EXTRN
    labels, extern = {}, set()
    for i in insns:
        if i.mnemonic[0] == "j" or i.mnemonic in ("call", "loop", "loope", "loopne"):
            m = re.fullmatch(r"0x([0-9a-f]+)", i.op_str)
            if m:
                t = int(m.group(1), 16)
                if lo <= t < hi:
                    labels[t] = "L%04X" % t
                else:
                    extern.add(t)
    for a, _ in ranges:
        labels.setdefault(a, "F%04X" % a)

    out = []
    out.append("; %s.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan." % name)
    out.append("; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).")
    out.append(";")
    for a, n in ranges:
        out.append(";   %04Xh  %d byte" % (a, n))
    out.append("")
    out.append("        NAME    %s" % name)
    out.append("")
    out.append("PGROUP  GROUP   PROG")
    out.append("DGROUP  GROUP   DATA")
    out.append("")
    out.append("DATA    SEGMENT WORD PUBLIC 'DATA'")
    out.append("DATA    ENDS")
    out.append("")
    out.append("PROG    SEGMENT BYTE PUBLIC 'PROG'")
    out.append("        ASSUME  CS:PGROUP, DS:DGROUP")
    out.append("")
    pubs = [labels[a] for a, _ in ranges]
    out.append("        PUBLIC  " + ", ".join(pubs))
    for t in sorted(extern):
        out.append("        EXTRN   X%04X:NEAR      ;; ??? target di luar modul" % t)
    out.append("")

    for i in insns:
        lab = labels.get(i.address, "")
        txt = i.mnemonic.upper()
        if i.op_str:
            txt += "\t" + conv(i.op_str, labels, lo, hi)
        m = re.fullmatch(r"0x([0-9a-f]+)", i.op_str)
        if m and int(m.group(1), 16) in extern:
            txt = "%s\tX%04X" % (i.mnemonic.upper(), int(m.group(1), 16))
        raw = " ".join("%02x" % c for c in i.bytes)
        out.append("%-8s%-28s; %04X  %s" % ((lab + ":") if lab else "", txt,
                                            i.address, raw))
    out.append("")
    out.append("PROG    ENDS")
    out.append("        END")

    os.makedirs(ASM, exist_ok=True)
    p = os.path.join(ASM, name + ".asm")
    with open(p, "w", newline="\r\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("%s: %d instruksi, %d label, %d target luar" %
          (p, len(insns), len(labels), len(extern)))


if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) % 2 != 0:
        print(__doc__)
        sys.exit(2)
    a = sys.argv[2:]
    gen(sys.argv[1], [(int(a[i], 16), int(a[i + 1])) for i in range(0, len(a), 2)])
