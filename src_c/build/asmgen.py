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

# Nama publik per alamat. WAJIB sama dengan nama yang dipakai berkas .c,
# kalau tidak LINK melaporkan "Unresolved Externals". Alamat yang tidak ada
# di sini diberi nama otomatis F<addr>.
NAMES = {
    0x5a5b: "rnd",      0x5a7f: "sndsave", 0x5ac9: "sndrest",
    0x5cbb: "line",     0x5d98: "vbwait",  0x5da1: "vbend",
    0x5dce: "shftl",    0x644a: "bios10", 0x6453: "text",    0x6524: "putmsk",
    0x657c: "draw",     0x65e0: "put",     0x6600: "shftr",
    0x672f: "blit",     0x6869: "fillrect", 0x6939: "prep",
    0x2b11: "waitn",  0x5b73: "tone3",  0x5a74: "sndoff",
    0x5a76: "sndon",  0x5c84: "refresh", 0x6853: "rdkey",
    # pembantu suara di dalam snd1 yang dipanggil snd2 -- harus bernama
    # supaya terekspor, kalau tidak LINK melaporkan unresolved.
    0x5a78: "sndini", 0x5b23: "snda", 0x5b33: "sndb",
    0x5b3e: "sndc",   0x5b4e: "sndd",
}


def hexs(v):
    """Konstanta gaya MASM: akhiran H, digit awal wajib."""
    s = "%X" % v
    return (("0" + s) if s[0].isalpha() else s) + "H"


# capstone memakai nama mnemonik 32-bit walau di-set CS_MODE_16. MASM 1.27
# (1984) hanya kenal 8086, jadi harus diterjemahkan balik -- kalau tidak
# instruksinya DILEWATI diam-diam dan seluruh modul bergeser.
M16 = {
    "cdq": "CWD", "cwde": "CBW", "cdqe": "CBW",
    "movsd": "MOVSW", "stosd": "STOSW", "lodsd": "LODSW",
    "scasd": "SCASW", "cmpsd": "CMPSW", "insd": "INSW", "outsd": "OUTSW",
    "pushfd": "PUSHF", "popfd": "POPF", "iretd": "IRET", "jecxz": "JCXZ",
}


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
        # Batas kata WAJIB: konstanta "212CH" mengandung "CH" dan tanpa
        # batas akan dikira register. Ditulis pakai lookaround, bukan
        # \b, supaya aman dari escaping saat berkas ini dibangkitkan.
        REG = ("(?<![A-Z0-9])(AX|BX|CX|DX|SI|DI|BP|SP|AL|BL|CL|DL"
               "|AH|BH|CH|DH)(?![A-Z0-9])")
        if re.search(REG, inner):
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
                    labels[t] = NAMES.get(t, "L%04X" % t)
                else:
                    extern.add(t)
    for a, _ in ranges:
        labels.setdefault(a, NAMES.get(a, "F%04X" % a))
    # Satu modul bisa memuat BEBERAPA fungsi. Semua alamat bernama yang jatuh
    # di dalam rentang harus jadi label DAN publik, kalau tidak fungsi selain
    # yang pertama tidak terekspor dan LINK gagal.
    for a, nm in NAMES.items():
        if lo <= a < hi:
            labels[a] = nm

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
    pubs = sorted({labels[a] for a, _ in ranges} |
                  {nm for a, nm in NAMES.items() if lo <= a < hi})
    out.append("        PUBLIC  " + ", ".join(pubs))
    for t in sorted(extern):
        out.append("        EXTRN   %s:NEAR" % NAMES.get(t, "X%04X" % t))
    out.append("")

    for i in insns:
        lab = labels.get(i.address, "")
        txt = M16.get(i.mnemonic, i.mnemonic.upper())
        # Instruksi STRING: capstone mencetak operan implisitnya, MASM 1.x
        # menolaknya ("Extra characters on line"). Harus telanjang.
        if re.match(r"(lods|stos|movs|scas|cmps|ins|outs)[bwd]$", i.mnemonic):
            out.append("%-8s%-28s; %04X  %s" % (
                (labels.get(i.address, "") + ":") if i.address in labels else "",
                txt, i.address, " ".join("%02x" % c for c in i.bytes)))
            continue
        if i.op_str:
            txt += "\t" + conv(i.op_str, labels, lo, hi)
        m = re.fullmatch(r"0x([0-9a-f]+)", i.op_str)
        if m and int(m.group(1), 16) in extern:
            tv = int(m.group(1), 16)
            txt = "%s\t%s" % (i.mnemonic.upper(), NAMES.get(tv, "X%04X" % tv))
        # MASM 1.x memesan 3 byte untuk JMP MAJU (asumsi near di pass 1). Kalau
        # ternyata muat pendek, ia mengisi sisanya dengan NOP -> "EB xx 90",
        # dan seluruh modul bergeser 1 byte per lompatan. Paksa SHORT kalau
        # aslinya 2 byte. Ini penyebab tersering modul asm meleset panjang.
        if i.mnemonic == "jmp" and len(i.bytes) == 2 and m:
            txt = "JMP\tSHORT " + conv(i.op_str, labels, lo, hi)
        # MASM memendekkan imm16 yang muat di int8 jadi bentuk sign-extended
        # (opcode 81 -> 83). Kalau ASLINYA memakai 81, tidak ada sintaks MASM
        # untuk memaksanya -- pakai DB supaya bytenya persis.
        if i.bytes[0] == 0x81 and len(i.bytes) >= 4:
            imm = int.from_bytes(bytes(i.bytes[-2:]), "little", signed=True)
            if -128 <= imm <= 127:
                out.append("%-8s%-28s; %04X  %s  ;; DB: MASM akan memendekkannya"
                           % ((lab + ":") if lab else "",
                              "DB      " + ",".join(hexs(c) for c in i.bytes),
                              i.address,
                              " ".join("%02x" % c for c in i.bytes)))
                continue
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
