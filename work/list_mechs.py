import os, sys, struct
sys.path.insert(0, r"C:\Projects\Creative_Contraptions\port")
from cc import assets
D = assets.find_data_dir()
raw = open(os.path.join(D, "MECHS"), "rb").read()
n = struct.unpack_from("<I", raw, 8)[0] // 12
majors = {}
for i in range(n):
    a, mi, h, w, f, ln, off = struct.unpack_from("<BBBBHHI", raw, i * 12)
    majors.setdefault(a, []).append(mi)
print("MECHS id_major -> id_minor list:")
for a in sorted(majors):
    print("  major %d : minors %s" % (a, sorted(majors[a])))
# tipe jawaban yg dipakai goal (dari diag): 100,101,110,111,112,120,130,132,133,135,140,141,150
print("\ncatatan: 'type' CONTRAP mungkin = major*? cek kecocokan dgn daftar di atas")
