"""Validasi struktur file CONTRAP menurut hasil decompile FUN_1000_5035.

Struktur per hasil decompile:
  Directory: 36 x {u16 id, u32 offset}   (216 byte)
  Per contraption @offset:
    u16 goal_id
    u16 countA          ; array u32[countA]
    u16 countB          ; array rec6[countB]   <- komponen + posisi?
    u16 countC          ; array rec6[countC]
    u16[countB+countC]
"""
import struct

f = r"C:\Projects\Creative_Contraptions\work\CONTRAP"
b = open(f, "rb").read()
print("CONTRAP size = %d\n" % len(b))

# Directory
dirn = 216 // 6
print("=== Directory (%d record) ===" % dirn)
recs = []
for i in range(dirn):
    iid, off = struct.unpack_from("<HI", b, i * 6)
    recs.append((iid, off))
uniq = sorted(set(r[0] for r in recs if r[0]))
print("  goal id unik: %s" % uniq)
from collections import Counter
print("  varian per goal: %s" % dict(Counter(r[0] for r in recs if r[0])))

# Parse contraption pertama untuk tiap goal
print("\n=== Uji parse struktur contraption ===")
for goal in uniq[:6]:
    off = next(o for (i, o) in recs if i == goal)
    p = off
    goal_id = struct.unpack_from("<H", b, p)[0]; p += 2
    countA = struct.unpack_from("<H", b, p)[0]; p += 2
    arrA = [struct.unpack_from("<I", b, p + k*4)[0] for k in range(countA)]; p += countA*4
    countB = struct.unpack_from("<H", b, p)[0]; p += 2
    recB = [b[p + k*6: p + k*6 + 6] for k in range(countB)]; p += countB*6
    countC = struct.unpack_from("<H", b, p)[0]; p += 2
    recC = [b[p + k*6: p + k*6 + 6] for k in range(countC)]; p += countC*6
    arrD = [struct.unpack_from("<H", b, p + k*2)[0] for k in range(countB+countC)]; p += (countB+countC)*2
    total = p - (off + 2)   # byte terbaca setelah goal_id
    expect = countA*4 + countB*6 + 6 + countC*6 + (countB+countC)*2  # sesuai local_32
    ok = "OK" if goal_id == goal else "!! goal_id=%d != %d" % (goal_id, goal)
    chk = "COCOK" if total == expect else "beda (%d vs %d)" % (total, expect)
    print("\ngoal %d @0x%X: goal_id=%d [%s]  checksum=%s" % (goal, off, goal_id, ok, chk))
    print("  countA=%d countB=%d countC=%d" % (countA, countB, countC))
    # tampilkan record 6-byte B sebagai 3 x u16 (dugaan: id,x,y)
    print("  recB (dugaan id,x,y):")
    for k, r in enumerate(recB[:8]):
        a, x, y = struct.unpack("<HHH", r)
        print("    [%d] %s -> %d, %d, %d" % (k, r.hex(), a, x, y))
