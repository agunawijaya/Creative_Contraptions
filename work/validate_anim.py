"""Validasi grammar ANIMATE: parse semua 241 skrip; hipotesis jumlah operand/opcode.
Skrip benar jika semua opcode valid dan berakhir tepat di 0xff."""
import struct
from collections import Counter

D = r"C:\Projects\Creative_Contraptions\work"

# Hipotesis jumlah OPERAND byte per opcode (dari akses 0x3ae /2)
OPERANDS = {0x00: 2, 0x01: 3, 0x02: 3, 0x03: 2, 0x04: 5, 0x05: 1, 0x06: 1,
            0x07: 3, 0x08: 2, 0x09: 3, 0x0A: 2, 0x0C: 2, 0x0D: 1, 0x0E: 2,
            0x0F: 2, 0x10: 0, 0x11: 3, 0xFF: 0}


def parse(script):
    i, n = 0, len(script)
    steps = []
    while i < n:
        op = script[i]
        if op == 0xFF:
            return steps, i, "OK" if i == n - 1 else "ff-di-tengah@%d/%d" % (i, n)
        if op not in OPERANDS:
            return steps, i, "opcode-invalid 0x%02x@%d" % (op, i)
        nb = OPERANDS[op]
        if i + 1 + nb > n:
            return steps, i, "overrun op0x%02x@%d" % (op, i)
        steps.append((op, script[i + 1:i + 1 + nb]))
        i += 1 + nb
    return steps, i, "tanpa-ff"


b = open(D + "\\ANIMATE", "rb").read()
first = struct.unpack_from("<I", b, 8)[0]
n = first // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]

ok = 0
fails = Counter()
for a, bb, h, w, f, ln, off in recs:
    if not ln:
        continue
    script = b[off:off + ln]
    steps, pos, status = parse(script)
    if status == "OK":
        ok += 1
    else:
        fails[status.split("@")[0].split(" ")[0]] += 1

print("Parse bersih: %d / %d" % (ok, sum(1 for r in recs if r[5])))
print("Jenis kegagalan: %s" % dict(fails.most_common()))
