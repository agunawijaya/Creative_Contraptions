"""Parser ANIMATE v3: op4 sound panjang-variabel per mode."""
import struct
from collections import Counter

D = r"C:\Projects\Creative_Contraptions\work"
FIXED = {0x02: 1, 0x03: 2, 0x05: 0, 0x06: 0, 0x07: 1, 0x08: 2, 0x09: 1,
         0x0A: 2, 0x0C: 2, 0x0D: 0, 0x0E: 0, 0x0F: 0, 0x10: 0, 0x11: 4}
LIST_ITEM = {0x00: 2, 0x01: 1}   # daftar item s/d byte 0xff


CULPRIT = Counter()


def parse(s):
    i, n = 0, len(s)
    prev = None
    while i < n:
        op = s[i]; i += 1
        if op != 0xFF and op not in (0x04,) and op not in LIST_ITEM and op not in FIXED:
            CULPRIT[prev] += 1
        if op == 0xFF:
            return "OK" if i == n else "ff-tengah@%d/%d" % (i, n)
        if op == 0x04:                       # SOUND: variabel per mode
            mode = s[i]; i += 1
            if mode == 1:
                i += 6
            elif mode in (2, 3):
                while i + 1 < n and not (s[i] == 0xFF and s[i + 1] == 0xFF):
                    i += 1
                i += 2                        # konsumsi 0xff 0xff
            # mode 0: tak ada tambahan
        elif op in LIST_ITEM:
            isz = LIST_ITEM[op]
            while i < n and s[i] != 0xFF:
                i += isz
            i += 1
        elif op in FIXED:
            i += FIXED[op]
        else:
            return "invalid 0x%02x@%d" % (op, i - 1)
        prev = op
    return "tanpa-ff"


b = open(D + "\\ANIMATE", "rb").read()
n = struct.unpack_from("<I", b, 8)[0] // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]
ok = 0; tot = 0; fails = Counter()
for r in recs:
    if r[5]:
        tot += 1
        st = parse(b[r[6]:r[6] + r[5]])
        if st == "OK":
            ok += 1
        else:
            fails[st.split("@")[0].split(" ")[0]] += 1
print("Parse bersih: %d / %d" % (ok, tot))
print("Kegagalan: %s" % dict(fails.most_common()))
print("Opcode sebelum byte invalid: %s"
      % {("0x%02x" % k if k is not None else "None"): v for k, v in CULPRIT.most_common()})
