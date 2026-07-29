"""Parse goal 1 lengkap; uji tafsiran: field3 = kategori mekanisme (MECHS id)."""
import struct

MECH = {100: "Inclined Plane", 101: "Inclined Plane", 110: "Pulley", 111: "Pulley",
        112: "Pulley", 115: "Wheel&Axle", 120: "Wedge", 130: "Pendulum", 131: "Pendulum",
        132: "Magnet", 133: "Pulley?", 135: "Screw", 140: "Lever", 141: "Lever", 150: "Spring"}

b = open(r"C:\Projects\Creative_Contraptions\work\CONTRAP", "rb").read()
recs = [struct.unpack_from("<HI", b, i * 6) for i in range(36)]

for goal in (1, 4):
    off = next(o for (i, o) in recs if i == goal)
    p = off
    goal_id = struct.unpack_from("<H", b, p)[0]; p += 2
    countA = struct.unpack_from("<H", b, p)[0]; p += 2
    arrA = [struct.unpack_from("<I", b, p + k * 4)[0] for k in range(countA)]; p += countA * 4
    countB = struct.unpack_from("<H", b, p)[0]; p += 2
    recB = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(countB)]; p += countB * 6
    countC = struct.unpack_from("<H", b, p)[0]; p += 2
    recC = [struct.unpack_from("<HHH", b, p + k * 6) for k in range(countC)]; p += countC * 6
    arrD = [struct.unpack_from("<H", b, p + k * 2)[0] for k in range(countB + countC)]

    print("\n===== GOAL %d @0x%X =====" % (goal, off))
    print("countA=%d arrA=%s" % (countA, [hex(a) for a in arrA]))
    print("countB=%d (kelompok 1):" % countB)
    for f0, f1, f2 in recB:
        m = MECH.get(f2, "?")
        print("   f0=%-4d f1=%-4d f2=%-4d  -> field3 sbg mekanisme: %s" % (f0, f1, f2, m))
    print("countC=%d (kelompok 2):" % countC)
    for f0, f1, f2 in recC:
        m = MECH.get(f2, "?")
        print("   f0=%-4d f1=%-4d f2=%-4d  -> %s" % (f0, f1, f2, m))
    print("arrD (%d nilai): %s" % (len(arrD), arrD))
