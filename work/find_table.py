"""Pindai file untuk tabel dispatch VM: 18 pasang {u16 opcode<0x100, u16 handler in code}."""
import struct

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()

# fungsi valid (entry offsets) utk validasi handler
funcs = {}
for line in open(r"C:\Projects\Creative_Contraptions\work\ghidra_out\functions.txt"):
    line = line.strip()
    parts = line.split()
    if len(parts) >= 3 and ":" in parts[1]:
        try:
            funcs[int(parts[1].split(":")[1], 16)] = parts[2]
        except ValueError:
            pass
fset = set(funcs)
code_lo, code_hi = 0x0e, 0x9070

best = []
for T in range(0, len(b) - 72, 2):
    ok = 0
    for e in range(0, 0x48, 4):
        op = struct.unpack_from("<H", b, T + e)[0]
        hd = struct.unpack_from("<H", b, T + e + 2)[0]
        if 0 < op < 0x100 and code_lo <= hd <= code_hi:
            ok += 1
        else:
            break
    if ok >= 6:
        best.append((ok, T))

best.sort(reverse=True)
print("Kandidat tabel (jumlah entri valid, offset file):")
for ok, T in best[:6]:
    print("\n== T=0x%X, %d entri valid ==" % (T, ok))
    for e in range(0, 0x48, 4):
        op = struct.unpack_from("<H", b, T + e)[0]
        hd = struct.unpack_from("<H", b, T + e + 2)[0]
        nm = funcs.get(hd, "-")
        exact = "<-FUN" if hd in fset else ""
        print("   op=0x%02x hd=0x%04x %s %s" % (op, hd, nm, exact))
