"""Parser ANIMATE v2 dgn grammar berdaftar (list 0xff-terminated)."""
import struct
from collections import Counter

D = r"C:\Projects\Creative_Contraptions\work"

# operand tetap (byte) per opcode; LIST = daftar item s/d 0xff
FIXED = {0x02: 1, 0x03: 2, 0x04: 7, 0x05: 0, 0x06: 0, 0x07: 1, 0x08: 2, 0x09: 1,
         0x0A: 2, 0x0C: 2, 0x0D: 0, 0x0E: 0, 0x0F: 0, 0x10: 0, 0x11: 4}
LIST_ITEM = {0x00: 2, 0x01: 1}   # ukuran item; diakhiri byte 0xff


def parse(s):
    i, n = 0, len(s)
    while i < n:
        op = s[i]; i += 1
        if op == 0xFF:
            return "OK" if i == n else "ff-tengah@%d/%d" % (i, n)
        if op in LIST_ITEM:
            isz = LIST_ITEM[op]
            while i < n and s[i] != 0xFF:
                i += isz
            if i >= n:
                return "list-overrun@op%02x" % op
            i += 1  # konsumsi 0xff penutup list
        elif op in FIXED:
            i += FIXED[op]
            if i > n:
                return "overrun@op%02x" % op
        else:
            return "opcode-invalid 0x%02x@%d" % (op, i - 1)
    return "tanpa-ff"


b = open(D + "\\ANIMATE", "rb").read()
first = struct.unpack_from("<I", b, 8)[0]
n = first // 12
recs = [struct.unpack_from("<BBBBHHI", b, i * 12) for i in range(n)]

ok = 0
tot = 0
fails = Counter()
for a, bb, h, w, f, ln, off in recs:
    if not ln:
        continue
    tot += 1
    st = parse(b[off:off + ln])
    if st == "OK":
        ok += 1
    else:
        fails[st.split("@")[0].split(" ")[0]] += 1
print("Parse bersih: %d / %d" % (ok, tot))
print("Kegagalan: %s" % dict(fails.most_common()))
