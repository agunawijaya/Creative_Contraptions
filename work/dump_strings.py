import re
b = open(r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE", "rb").read()
# ekstrak string ASCII cetak >=4 char, dgn offset
out = []
cur = bytearray(); start = 0
for i, ch in enumerate(b):
    if 32 <= ch < 127:
        if not cur:
            start = i
        cur.append(ch)
    else:
        if len(cur) >= 5:
            out.append((start, cur.decode("latin1")))
        cur = bytearray()
# tampilkan yg terkait mekanisme/review
kw = re.compile(r"(inclin|plane|pulley|wheel|axle|wedge|pendulum|magnet|screw|lever|spring|"
                r"swing|ramp|machine|mechanism|simple|clock|force|move|lift|push|roll|"
                r"review|zany|contraption)", re.I)
for off, s in out:
    if kw.search(s):
        print("0x%04X  %s" % (off, s))
