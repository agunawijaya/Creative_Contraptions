"""Diagnostik: opcode mana yang menyebabkan misalignment?"""
import struct
from collections import Counter

D = r"C:\Projects\Creative_Contraptions\work"
FIXED = {0x02: 1, 0x03: 2, 0x04: 7, 0x05: 0, 0x06: 0, 0x07: 1, 0x08: 2, 0x09: 1,
         0x0A: 2, 0x0C: 2, 0x0D: 0, 0x0E: 0, 0x0F: 0, 0x10: 0, 0x11: 4}
LIST_ITEM = {0x00: 2, 0x01: 1}

culprit = Counter()   # opcode SEBELUM yg gagal


def parse(s):
    i, n = 0, len(s)
    prev = None
    while i < n:
        op = s[i]; i += 1
        if op == 0xFF:
            return "OK" if i == n else "ff-tengah"
        if op in LIST_ITEM:
            isz = LIST_ITEM[op]
            while i < n and s[i] != 0xFF:
                i += isz
            if i >= n:
                culprit[prev]; return "list-overrun"
            i += 1
        elif op in FIXED:
            i += FIXED[op]
        else:
            culprit[prev] += 1   # opcode sebelumnya kemungkinan salah hitung
            return "invalid"
        prev = op
    return "tanpa-ff"


b = open(D + "\\ANIMATE", "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]
ok = 0
for r in recs:
    if r[5]:
        if parse(b[r[6]:r[6] + r[5]]) == "OK":
            ok += 1
print("OK: %d/240" % ok)
print("Opcode yg SEBELUM byte invalid (tersangka salah-hitung):")
for op, c in culprit.most_common():
    lbl = "0x%02x" % op if op is not None else "None"
    print("  %s : %d kali" % (lbl, c))
